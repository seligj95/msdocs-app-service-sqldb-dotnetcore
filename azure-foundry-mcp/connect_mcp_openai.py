#!/usr/bin/env python3
"""
Azure OpenAI Assistants with Local MCP Server Integration

This script demonstrates how to connect Azure OpenAI Assistants API 
to a local Model Context Protocol (MCP) server for the todos application.

Since Azure AI Foundry Agent Service is not available, we'll use the 
OpenAI assistants API which is supported by the Azure resource.
"""

import os
import time
import json
import asyncio
import logging
import requests
from typing import Dict, Any, List
from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential
from openai import AzureOpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPOpenAIConnector:
    """Handles connection between Azure OpenAI Assistants and local MCP server"""
    
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        self.subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
        self.resource_group = os.getenv("AZURE_RESOURCE_GROUP") 
        self.project_name = os.getenv("AZURE_PROJECT_NAME")
        self.openai_endpoint = "https://portalfoundry.openai.azure.com/"
        self.mcp_url = os.getenv("LOCAL_MCP_URL", "http://localhost:5093/api/mcp")
        self.mcp_server_name = os.getenv("MCP_SERVER_NAME", "todos-mcp")
        
        # Validate required environment variables
        self._validate_config()
        
        # Initialize Azure OpenAI client
        self.credential = DefaultAzureCredential()
        self.client = None
        
    def _validate_config(self):
        """Validate that required configuration is present"""
        required_vars = ["AZURE_SUBSCRIPTION_ID", "AZURE_RESOURCE_GROUP", "AZURE_PROJECT_NAME"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}. "
                f"Please copy .env.template to .env and fill in your values."
            )
    
    def initialize_client(self):
        """Initialize the Azure OpenAI client"""
        try:
            # Get access token for Azure OpenAI
            token = self.credential.get_token("https://cognitiveservices.azure.com/.default")
            
            self.client = AzureOpenAI(
                azure_endpoint=self.openai_endpoint,
                azure_ad_token=token.token,
                api_version="2024-12-01-preview"  # Latest API version with assistants
            )
            
            logger.info("Successfully connected to Azure OpenAI")
            
            # Test connection by listing models
            models = self.client.models.list()
            logger.info(f"Available models: {len(models.data)} models found")
            
        except Exception as e:
            logger.error(f"Failed to initialize Azure OpenAI client: {e}")
            raise
    
    def create_mcp_function_definitions(self) -> List[Dict[str, Any]]:
        """Create function definitions for MCP server tools"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "create_todo",
                    "description": "Creates a new todo item with a description and creation date",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "description": {
                                "type": "string",
                                "description": "The description of the todo item"
                            },
                            "createdDate": {
                                "type": "string",
                                "format": "date-time",
                                "description": "Creation date of the todo (ISO format)"
                            }
                        },
                        "required": ["description", "createdDate"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "read_todos",
                    "description": "Reads all todos, or a single todo if an id is provided",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "id": {
                                "type": "string",
                                "description": "Optional ID of the todo to read (if not provided, returns all todos)"
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_todo",
                    "description": "Updates the specified todo fields by id",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "id": {
                                "type": "string",
                                "description": "ID of the todo to update"
                            },
                            "description": {
                                "type": "string",
                                "description": "New description (optional)"
                            },
                            "createdDate": {
                                "type": "string",
                                "format": "date-time",
                                "description": "New creation date (optional)"
                            }
                        },
                        "required": ["id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_todo",
                    "description": "Deletes a todo by id",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "id": {
                                "type": "string",
                                "description": "ID of the todo to delete"
                            }
                        },
                        "required": ["id"]
                    }
                }
            }
        ]
    
    def call_mcp_server(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Call the local MCP server with the specified tool and parameters"""
        try:
            # Map the function name to the MCP tool name (they should be the same now)
            mcp_tool_map = {
                "create_todo": "create_todo",
                "read_todos": "read_todos", 
                "update_todo": "update_todo",
                "delete_todo": "delete_todo"
            }
            
            mcp_tool = mcp_tool_map.get(tool_name)
            if not mcp_tool:
                return {"error": f"Unknown tool: {tool_name}"}
            
            # Prepare the request payload for MCP server
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": mcp_tool,
                    "arguments": parameters
                }
            }
            
            logger.info(f"Calling MCP server: {mcp_tool} with {parameters}")
            
            # Call the MCP server
            response = requests.post(
                self.mcp_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                try:
                    # Handle Server-Sent Events (SSE) format
                    response_text = response.text.strip()
                    
                    # Parse SSE format: event: message\ndata: {...}
                    if response_text.startswith('event: message\ndata: '):
                        json_data = response_text.split('data: ', 1)[1]
                        result = json.loads(json_data)
                        logger.info(f"MCP response: {result}")
                        return result.get("result", {})
                    else:
                        # Try parsing as regular JSON
                        result = response.json()
                        logger.info(f"MCP response: {result}")
                        return result.get("result", {})
                        
                except (json.JSONDecodeError, IndexError) as e:
                    # Handle cases where response is not valid JSON or SSE
                    logger.error(f"Invalid response from MCP server: {response.text}")
                    return {"error": f"Invalid response format: {response.text}"}
            else:
                error_msg = f"MCP server error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {"error": error_msg}
                
        except Exception as e:
            error_msg = f"Failed to call MCP server: {e}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    def create_assistant_with_mcp(self):
        """Create an Azure OpenAI assistant configured with MCP tools"""
        try:
            # Define the assistant with MCP function tools
            mcp_tools = self.create_mcp_function_definitions()
            
            logger.info("Creating assistant with MCP tool functions...")
            
            assistant = self.client.beta.assistants.create(
                name="TodosAssistant",
                description="An AI assistant that can manage todos using a local MCP server",
                model="gpt-4.1-mini",  # Use the deployed model
                instructions="""
                You are a helpful AI assistant that can manage todos using a local MCP server.
                You have access to the following todo operations through function calls:
                - create_todo: Create new todos with description and date
                - read_todos: Read/list existing todos (all or by ID)
                - update_todo: Update todo descriptions and dates by ID
                - delete_todo: Delete todos by ID
                
                When users ask about todos, use the appropriate function calls to help them.
                Always provide clear, helpful responses about the todo operations.
                If there are any errors from the MCP server, explain them clearly to the user.
                
                For dates, use ISO format (YYYY-MM-DDTHH:MM:SS) when creating or updating todos.
                """,
                tools=mcp_tools
            )
            
            logger.info(f"Successfully created assistant: {assistant.id}")
            return assistant
            
        except Exception as e:
            logger.error(f"Failed to create assistant with MCP: {e}")
            raise
    
    def handle_function_calls(self, required_action):
        """Handle function calls from the assistant"""
        tool_outputs = []
        
        for tool_call in required_action.submit_tool_outputs.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            logger.info(f"Assistant called function: {function_name} with args: {function_args}")
            
            # Call the MCP server
            result = self.call_mcp_server(function_name, function_args)
            
            # Format the result for the assistant
            tool_outputs.append({
                "tool_call_id": tool_call.id,
                "output": json.dumps(result)
            })
        
        return tool_outputs
    
    def test_mcp_integration(self, assistant):
        """Test the MCP integration by having the assistant interact with todos"""
        try:
            # Create a thread for conversation
            thread = self.client.beta.threads.create()
            logger.info(f"Created thread: {thread.id}")
            
            # Send a test message asking about todos
            test_message = "Can you show me all my current todos?"
            
            message = self.client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=test_message
            )
            
            logger.info(f"Sent test message: {test_message}")
            
            # Run the assistant
            run = self.client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=assistant.id
            )
            
            logger.info(f"Started run: {run.id}")
            
            # Wait for completion and handle function calls
            while run.status in ["queued", "in_progress", "requires_action"]:
                time.sleep(1)
                run = self.client.beta.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id
                )
                
                logger.info(f"Run status: {run.status}")
                
                if run.status == "requires_action":
                    # Handle function calls
                    tool_outputs = self.handle_function_calls(run.required_action)
                    
                    # Submit tool outputs
                    run = self.client.beta.threads.runs.submit_tool_outputs(
                        thread_id=thread.id,
                        run_id=run.id,
                        tool_outputs=tool_outputs
                    )
            
            if run.status == "completed":
                # Get the response
                messages = self.client.beta.threads.messages.list(thread_id=thread.id)
                
                for message in messages.data:
                    if message.role == "assistant":
                        for content in message.content:
                            if content.type == "text":
                                logger.info(f"Assistant response: {content.text.value}")
                        break
                        
            else:
                logger.error(f"Run failed with status: {run.status}")
                # Get more details about the failure
                if hasattr(run, 'last_error') and run.last_error:
                    logger.error(f"Error details: {run.last_error}")
                # Try to get the run steps for more debugging info
                try:
                    run_steps = self.client.beta.threads.runs.steps.list(
                        thread_id=thread.id,
                        run_id=run.id
                    )
                    for step in run_steps.data:
                        logger.error(f"Step {step.id}: {step.status}")
                        if hasattr(step, 'last_error') and step.last_error:
                            logger.error(f"Step error: {step.last_error}")
                except Exception as e:
                    logger.error(f"Could not get run steps: {e}")
                        
        except Exception as e:
            logger.error(f"Failed to test MCP integration: {e}")
            raise
    
    def run_interactive_session(self, assistant):
        """Run an interactive session with the MCP-enabled assistant"""
        try:
            # Create a thread for the session
            thread = self.client.beta.threads.create()
            logger.info(f"Started interactive session with thread: {thread.id}")
            
            print("\n" + "="*60)
            print("🤖 Azure OpenAI Assistant with MCP Todos Integration")
            print("="*60)
            print("You can now interact with your todos through the AI assistant!")
            print("Try commands like:")
            print("  - 'Show me all my todos'")
            print("  - 'Create a new todo: Buy groceries'") 
            print("  - 'Delete todo with ID 2'")
            print("  - 'Update todo 3 with new description: Finish project'")
            print("\nType 'quit' to exit.\n")
            
            while True:
                user_input = input("You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("👋 Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                try:
                    # Send user message
                    self.client.beta.threads.messages.create(
                        thread_id=thread.id,
                        role="user",
                        content=user_input
                    )
                    
                    # Run the assistant
                    run = self.client.beta.threads.runs.create(
                        thread_id=thread.id,
                        assistant_id=assistant.id
                    )
                    
                    # Wait for completion and handle function calls
                    while run.status in ["queued", "in_progress", "requires_action"]:
                        time.sleep(0.5)
                        run = self.client.beta.threads.runs.retrieve(
                            thread_id=thread.id,
                            run_id=run.id
                        )
                        
                        if run.status == "requires_action":
                            # Handle function calls
                            tool_outputs = self.handle_function_calls(run.required_action)
                            
                            # Submit tool outputs
                            run = self.client.beta.threads.runs.submit_tool_outputs(
                                thread_id=thread.id,
                                run_id=run.id,
                                tool_outputs=tool_outputs
                            )
                    
                    if run.status == "completed":
                        # Get the latest assistant message
                        messages = self.client.beta.threads.messages.list(
                            thread_id=thread.id,
                            limit=1
                        )
                        
                        if messages.data:
                            latest_message = messages.data[0]
                            if latest_message.role == "assistant":
                                for content in latest_message.content:
                                    if content.type == "text":
                                        print(f"Assistant: {content.text.value}\n")
                                        break
                    else:
                        print(f"❌ Request failed with status: {run.status}")
                        # Get more details about the failure
                        if hasattr(run, 'last_error') and run.last_error:
                            print(f"Error details: {run.last_error}")
                        print()
                        
                except Exception as e:
                    print(f"❌ Error: {e}\n")
                    
        except Exception as e:
            logger.error(f"Interactive session failed: {e}")
            raise

def main():
    """Main function to demonstrate MCP integration with OpenAI assistants"""
    connector = MCPOpenAIConnector()
    
    try:
        # Initialize the client
        connector.initialize_client()
        
        # Create assistant with MCP tools
        assistant = connector.create_assistant_with_mcp()
        
        # Test the integration
        print("🧪 Testing MCP integration...")
        connector.test_mcp_integration(assistant)
        
        # Run interactive session
        connector.run_interactive_session(assistant)
        
        # Clean up - delete the assistant
        try:
            connector.client.beta.assistants.delete(assistant.id)
            logger.info(f"Deleted assistant: {assistant.id}")
        except Exception as e:
            logger.warning(f"Failed to delete assistant: {e}")
        
    except Exception as e:
        logger.error(f"Application failed: {e}")
        print(f"\n❌ Error: {e}")
        print("\nMake sure:")
        print("1. Your .env file is configured with correct Azure details")
        print("2. Your local MCP server is running on http://localhost:5093/api/mcp")
        print("3. You have the necessary Azure permissions")
        print("4. The Azure OpenAI service is properly configured")

if __name__ == "__main__":
    main()
