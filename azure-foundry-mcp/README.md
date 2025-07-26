# Azure AI + MCP Todo Agent

This project demonstrates a complete integration between **Azure OpenAI Assistants** and a **Model Context Protocol (MCP) server** running on Azure App Service. It showcases how to build AI agents that can interact with cloud-based applications through standardized protocols.

## 🏗️ Architecture

```
User Query → Azure OpenAI Assistant → Function Calling → Azure App Service (MCP Server) → SQL Database
```

- **Azure OpenAI**: GPT-4.1-mini model with function calling capabilities
- **Azure App Service**: .NET 8 web application with MCP server endpoints
- **SQL Database**: Persistent storage for todo items
- **Model Context Protocol**: Standardized interface for AI-tool interactions

## ✨ Features

- **Natural Language Interface**: Ask the AI assistant to manage your todos
- **Cloud-to-Cloud Integration**: Azure OpenAI calling Azure App Service MCP endpoints
- **Full CRUD Operations**: Create, read, update, and delete todos through conversation
- **Server-Sent Events**: Proper SSE format handling for MCP responses
- **Production Ready**: Deployed infrastructure with proper authentication

## 🚀 Quick Start

### Prerequisites

- Azure subscription with OpenAI service enabled
- Azure CLI installed and configured
- Python 3.11+
- .NET 8 SDK (for the main application)

### 1. Clone and Setup

```bash
git clone https://github.com/seligj95/app-service-to-do-mcp-agent.git
cd app-service-to-do-mcp-agent/azure-foundry-mcp
```

### 2. Install Python Dependencies

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment

Copy `.env.template` to `.env` and fill in your Azure details:

```bash
cp .env.template .env
# Edit .env with your Azure subscription ID, resource group, etc.
```

### 4. Deploy the App Service (Optional)

If you want to deploy your own instance:

```bash
cd ..  # Back to main directory
azd up  # Deploy to Azure
```

### 5. Run the MCP Integration

```bash
cd azure-foundry-mcp
source venv/bin/activate
python connect_mcp_openai.py
```

## 🎯 Usage Examples

Once running, you can interact with your todos through natural language:

```
You: Show me all my todos
Assistant: Here are all your todos:
1. "Buy groceries" - Due: 2025-07-26
2. "Finish project" - Due: 2025-07-27

You: Create a new todo: Call the dentist tomorrow
Assistant: I've created a new todo "Call the dentist tomorrow" for 2025-07-27.

You: Delete todo 1
Assistant: I've successfully deleted the todo "Buy groceries".
```

## 📁 Project Structure

```
azure-foundry-mcp/
├── connect_mcp_openai.py      # Main integration script (Azure OpenAI + MCP)
├── connect_mcp_to_foundry.py  # Original Azure AI Foundry attempt
├── test_endpoints.py          # API endpoint testing utilities
├── find_endpoint.py           # Azure resource discovery helper
├── requirements.txt           # Python dependencies
├── .env.template             # Environment variables template
├── .env                      # Your actual configuration (gitignored)
└── README.md                 # This file

Main Application (../)
├── Program.cs                # .NET app with MCP server endpoints
├── Controllers/              # MVC controllers including TodosController
├── Models/                   # Data models (Todo, etc.)
├── McpServer/               # MCP server tools implementation
├── infra/                   # Azure infrastructure (Bicep)
└── azure.yaml              # Azure Developer CLI configuration
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file based on `.env.template`:

```bash
# Azure AI Configuration
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_RESOURCE_GROUP=your-resource-group
AZURE_PROJECT_NAME=your-project-name

# MCP Server Configuration  
LOCAL_MCP_URL=https://your-app.azurewebsites.net/api/mcp
MCP_SERVER_NAME=todos-mcp
```

### Azure OpenAI Setup

1. Deploy an Azure OpenAI resource
2. Deploy a GPT-4 model (e.g., gpt-4o-mini, gpt-4.1-mini)
3. Ensure your Azure CLI is authenticated: `az login`

## 🛠️ Development

### Testing MCP Endpoints

```bash
# Test the MCP server directly
curl -X POST https://your-app.azurewebsites.net/api/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}'
```

### Local Development

For local development, run the .NET application locally:

```bash
cd ..  # Main directory
dotnet run
```

Then update your `.env` to point to `http://localhost:5093/api/mcp`.

## 🌟 Technical Highlights

### Server-Sent Events (SSE) Parsing

The MCP server returns responses in SSE format. The integration properly handles this:

```python
# Handle Server-Sent Events (SSE) format
if response_text.startswith('event: message\ndata: '):
    json_data = response_text.split('data: ', 1)[1]
    result = json.loads(json_data)
```

### Function Calling Integration

Azure OpenAI function definitions map directly to MCP tools:

```python
{
    "type": "function",
    "function": {
        "name": "create_todo",
        "description": "Creates a new todo item",
        "parameters": {
            "type": "object",
            "properties": {
                "description": {"type": "string"},
                "createdDate": {"type": "string", "format": "date-time"}
            }
        }
    }
}
```

### Authentication

Uses Azure CLI credentials with `DefaultAzureCredential`:

```python
credential = DefaultAzureCredential()
token = credential.get_token("https://cognitiveservices.azure.com/.default")
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Azure OpenAI team for the assistants API
- Model Context Protocol specification
- Azure App Service team for excellent .NET 8 support

## 📞 Support

If you encounter issues:

1. Check the Azure portal for App Service logs
2. Verify your Azure OpenAI model deployment
3. Ensure MCP endpoints are responding correctly
4. Review the `.env` configuration

For questions, please open an issue on GitHub.

---

**Built with ❤️ using Azure AI, .NET 8, and Model Context Protocol**
