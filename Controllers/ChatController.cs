using Microsoft.AspNetCore.Mvc;
using Azure.Identity;
using System.Text.Json;
using System.Text;
using DotNetCoreSqlDb.Models;

namespace DotNetCoreSqlDb.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class ChatController : ControllerBase
    {
        private readonly IConfiguration _configuration;
        private readonly ILogger<ChatController> _logger;
        private readonly HttpClient _httpClient;

        public ChatController(IConfiguration configuration, ILogger<ChatController> logger, HttpClient httpClient)
        {
            _configuration = configuration;
            _logger = logger;
            _httpClient = httpClient;
        }

        [HttpPost("message")]
        public async Task<IActionResult> SendMessage([FromBody] ChatMessageRequest request)
        {
            try
            {
                var endpoint = _configuration["AZURE_OPENAI_ENDPOINT"] ?? 
                              Environment.GetEnvironmentVariable("AZURE_OPENAI_ENDPOINT");
                
                var deploymentName = _configuration["AZURE_OPENAI_DEPLOYMENT_NAME"] ?? 
                                   Environment.GetEnvironmentVariable("AZURE_OPENAI_DEPLOYMENT_NAME") ?? 
                                   "gpt-4o-mini";

                if (string.IsNullOrEmpty(endpoint))
                {
                    return BadRequest("Azure OpenAI endpoint not configured");
                }

                // Get Azure access token
                var credential = new DefaultAzureCredential();
                var token = await credential.GetTokenAsync(new Azure.Core.TokenRequestContext(
                    new[] { "https://cognitiveservices.azure.com/.default" }));

                // Prepare the chat completion request
                var chatRequest = new
                {
                    messages = new object[]
                    {
                        new
                        {
                            role = "system",
                            content = @"You are a helpful assistant that manages todo items. You can:
1. Create new todo items
2. Read/list existing todos  
3. Update todo descriptions and dates
4. Delete todos

When users ask about todos, use the available functions to interact with the todo system.
Always be friendly and helpful. Format responses nicely with numbers or bullets when showing lists."
                        },
                        new
                        {
                            role = "user",
                            content = request.Message
                        }
                    },
                    functions = new object[]
                    {
                        new
                        {
                            name = "create_todo",
                            description = "Creates a new todo item",
                            parameters = new
                            {
                                type = "object",
                                properties = new
                                {
                                    description = new
                                    {
                                        type = "string",
                                        description = "The description of the todo item"
                                    },
                                    createdDate = new
                                    {
                                        type = "string",
                                        format = "date-time",
                                        description = "The creation date of the todo item"
                                    }
                                },
                                required = new[] { "description", "createdDate" }
                            }
                        },
                        new
                        {
                            name = "read_todos",
                            description = "Reads all todos or a specific todo by ID",
                            parameters = new
                            {
                                type = "object",
                                properties = new
                                {
                                    id = new
                                    {
                                        type = "string",
                                        description = "Optional ID of specific todo to read"
                                    }
                                }
                            }
                        },
                        new
                        {
                            name = "update_todo",
                            description = "Updates a todo item by ID",
                            parameters = new
                            {
                                type = "object",
                                properties = new
                                {
                                    id = new
                                    {
                                        type = "string",
                                        description = "The ID of the todo to update"
                                    },
                                    description = new
                                    {
                                        type = "string",
                                        description = "New description for the todo"
                                    },
                                    createdDate = new
                                    {
                                        type = "string",
                                        format = "date-time",
                                        description = "New creation date for the todo"
                                    }
                                },
                                required = new[] { "id" }
                            }
                        },
                        new
                        {
                            name = "delete_todo",
                            description = "Deletes a todo item by ID",
                            parameters = new
                            {
                                type = "object",
                                properties = new
                                {
                                    id = new
                                    {
                                        type = "string",
                                        description = "The ID of the todo to delete"
                                    }
                                },
                                required = new[] { "id" }
                            }
                        }
                    },
                    function_call = "auto",
                    max_tokens = 500,
                    temperature = 0.7
                };

                var jsonContent = JsonSerializer.Serialize(chatRequest);
                var content = new StringContent(jsonContent, Encoding.UTF8, "application/json");

                var url = $"{endpoint.TrimEnd('/')}/openai/deployments/{deploymentName}/chat/completions?api-version=2024-02-15-preview";
                
                _httpClient.DefaultRequestHeaders.Clear();
                _httpClient.DefaultRequestHeaders.Add("Authorization", $"Bearer {token.Token}");

                var response = await _httpClient.PostAsync(url, content);
                var responseText = await response.Content.ReadAsStringAsync();

                if (!response.IsSuccessStatusCode)
                {
                    _logger.LogError($"OpenAI API error: {response.StatusCode} - {responseText}");
                    return BadRequest("Failed to get response from AI");
                }

                var result = JsonDocument.Parse(responseText);
                var choices = result.RootElement.GetProperty("choices");
                var firstChoice = choices[0];
                var message = firstChoice.GetProperty("message");

                // Check if there's a function call
                if (message.TryGetProperty("function_call", out var functionCall))
                {
                    var functionName = functionCall.GetProperty("name").GetString();
                    var functionArgs = functionCall.GetProperty("arguments").GetString();

                    // Execute the function call
                    var functionResult = await HandleFunctionCall(functionName!, functionArgs!);

                    // Make a second call with the function result
                    var followUpRequest = new
                    {
                        messages = new object[]
                        {
                            new
                            {
                                role = "system",
                                content = @"You are a helpful assistant that manages todo items. When presenting function results, format them nicely and be conversational."
                            },
                            new
                            {
                                role = "user",
                                content = request.Message
                            },
                            new
                            {
                                role = "function",
                                name = functionName,
                                content = functionResult
                            }
                        },
                        max_tokens = 500,
                        temperature = 0.7
                    };

                    var followUpJson = JsonSerializer.Serialize(followUpRequest);
                    var followUpContent = new StringContent(followUpJson, Encoding.UTF8, "application/json");

                    var followUpResponse = await _httpClient.PostAsync(url, followUpContent);
                    var followUpText = await followUpResponse.Content.ReadAsStringAsync();

                    if (followUpResponse.IsSuccessStatusCode)
                    {
                        var followUpResult = JsonDocument.Parse(followUpText);
                        var followUpChoices = followUpResult.RootElement.GetProperty("choices");
                        var followUpChoice = followUpChoices[0];
                        var followUpMessage = followUpChoice.GetProperty("message");
                        var finalContent = followUpMessage.GetProperty("content").GetString();

                        return Ok(new ChatMessageResponse { Response = finalContent ?? "I completed that action." });
                    }
                }

                var responseContent = message.GetProperty("content").GetString();
                return Ok(new ChatMessageResponse { Response = responseContent ?? "I'm sorry, I couldn't understand that." });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error processing chat message");
                return StatusCode(500, "Internal server error");
            }
        }

        private async Task<string> HandleFunctionCall(string functionName, string arguments)
        {
            try
            {
                _logger.LogInformation($"Handling function call: {functionName} with args: {arguments}");
                
                // Get the MCP server URL from configuration
                var mcpUrl = _configuration["LOCAL_MCP_URL"] ?? 
                           Environment.GetEnvironmentVariable("LOCAL_MCP_URL") ?? 
                           "http://localhost:5093/api/mcp";

                // Parse the function arguments
                var argsJson = JsonDocument.Parse(arguments);
                var parameters = new Dictionary<string, object>();
                
                foreach (var property in argsJson.RootElement.EnumerateObject())
                {
                    parameters[property.Name] = property.Value.GetString() ?? property.Value.ToString();
                }
                
                // Create MCP request
                var mcpRequest = new
                {
                    jsonrpc = "2.0",
                    id = Guid.NewGuid().ToString(),
                    method = "tools/call",
                    @params = new
                    {
                        name = functionName,
                        arguments = parameters
                    }
                };
                
                var jsonContent = JsonSerializer.Serialize(mcpRequest);
                var content = new StringContent(jsonContent, Encoding.UTF8, "application/json");
                
                // Create a new HttpRequestMessage to set custom headers
                var request = new HttpRequestMessage(HttpMethod.Post, mcpUrl)
                {
                    Content = content
                };
                request.Headers.Add("Accept", "application/json, text/event-stream");
                
                var response = await _httpClient.SendAsync(request);
                var responseText = await response.Content.ReadAsStringAsync();
                
                _logger.LogInformation($"MCP Response: {responseText}");
                
                // Handle Server-Sent Events format
                if (responseText.StartsWith("event: message\ndata: "))
                {
                    var jsonData = responseText.Split("data: ", 2)[1];
                    var result = JsonDocument.Parse(jsonData);
                    
                    if (result.RootElement.TryGetProperty("result", out var resultElement))
                    {
                        return JsonSerializer.Serialize(resultElement);
                    }
                }
                
                // Try to parse as regular JSON
                var jsonResult = JsonDocument.Parse(responseText);
                if (jsonResult.RootElement.TryGetProperty("result", out var directResult))
                {
                    return JsonSerializer.Serialize(directResult);
                }
                
                return responseText;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, $"Error handling function call: {functionName}");
                return $"Error executing {functionName}: {ex.Message}";
            }
        }
    }

    public class ChatMessageRequest
    {
        public string Message { get; set; } = string.Empty;
    }

    public class ChatMessageResponse
    {
        public string Response { get; set; } = string.Empty;
    }
}
