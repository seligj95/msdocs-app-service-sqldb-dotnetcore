# Azure AI Foundry MCP Integration

This folder contains a Python script that demonstrates how to connect Azure AI Foundry Agent Service to your local Model Context Protocol (MCP) server for the todos application.

## Overview

The integration allows Azure AI Foundry agents to interact with your local todos MCP server, enabling AI-powered todo management through natural language commands.

## Prerequisites

1. **Azure AI Foundry Project**: You need an Azure AI Foundry project set up in Azure
2. **Local MCP Server**: Your .NET todos application should be running locally on port 5093
3. **Python 3.8+**: Required for running the integration script
4. **Azure Authentication**: Either Azure CLI login or service principal credentials

## Quick Start

1. **Run the setup script** (recommended):
   ```bash
   ./setup.sh
   ```

2. **Or set up manually**:
   ```bash
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Copy environment template
   cp .env.template .env
   ```

3. **Configure your Azure details** in `.env`:
   ```bash
   AZURE_SUBSCRIPTION_ID=your-subscription-id
   AZURE_RESOURCE_GROUP=your-resource-group
   AZURE_PROJECT_NAME=your-project-name
   ```

4. **Start your local MCP server** (in the main project directory):
   ```bash
   dotnet run
   ```

5. **Run the integration script**:
   ```bash
   python connect_mcp_to_foundry.py
   ```

## How It Works

### 1. MCP Server Configuration
The script connects to your local MCP server running at `http://localhost:5093/api/mcp` and registers the following tools:
- `mcp_create_todo`: Create new todos
- `mcp_read_todos`: List all todos or get a specific todo
- `mcp_update_todo`: Update existing todos
- `mcp_delete_todo`: Delete todos

### 2. Azure AI Foundry Agent
The script creates an Azure AI Foundry agent with:
- Access to your local MCP tools
- Instructions for managing todos
- Natural language interface for todo operations

### 3. Interactive Session
Once connected, you can interact with your todos using natural language:

```
You: Show me all my todos
Agent: Here are your current todos: [lists todos from MCP server]

You: Create a new todo: Buy groceries for dinner
Agent: I've created a new todo "Buy groceries for dinner" for you.

You: Delete the todo with ID 2
Agent: I've successfully deleted todo with ID 2.
```

## Features

- **Natural Language Interface**: Ask about todos in plain English
- **Real-time Integration**: Direct connection to your local MCP server
- **Full CRUD Operations**: Create, read, update, and delete todos
- **Error Handling**: Robust error handling and logging
- **Interactive Mode**: Chat-like interface for todo management

## Configuration Files

### `.env` (Required)
Contains your Azure AI Foundry project configuration:
- `AZURE_SUBSCRIPTION_ID`: Your Azure subscription ID
- `AZURE_RESOURCE_GROUP`: Resource group containing your AI Foundry project
- `AZURE_PROJECT_NAME`: Your AI Foundry project name
- `LOCAL_MCP_URL`: URL of your local MCP server (default: http://localhost:5093/api/mcp)

### `requirements.txt`
Python dependencies for the integration:
- `azure-ai-agents`: Azure AI Foundry Agent Service client
- `azure-identity`: Azure authentication
- `python-dotenv`: Environment variable management

## Troubleshooting

### Common Issues

1. **Authentication Errors**:
   - Make sure you're logged into Azure CLI: `az login`
   - Verify your subscription and resource group names
   - Check that you have proper permissions on the AI Foundry project

2. **MCP Server Connection Issues**:
   - Ensure your .NET application is running on port 5093
   - Check that the MCP endpoint `/api/mcp` is accessible
   - Verify the MCP server is responding to requests

3. **Agent Creation Failures**:
   - Confirm your AI Foundry project has the necessary model deployments
   - Check that MCP support is enabled in your Azure AI Foundry project
   - Verify the project URL format is correct

### Debugging

Enable detailed logging by setting the log level in the script:
```python
logging.basicConfig(level=logging.DEBUG)
```

## Example Usage

```bash
# Start your .NET MCP server
cd /workspaces/msdocs-app-service-sqldb-dotnetcore
dotnet run

# In another terminal, run the integration
cd azure-foundry-mcp
source venv/bin/activate
python connect_mcp_to_foundry.py
```

## Architecture

```
┌─────────────────────┐    ┌──────────────────────┐    ┌─────────────────┐
│ Azure AI Foundry    │    │ Python Integration   │    │ Local MCP Server│
│ Agent Service       │◄──►│ Script               │◄──►│ (.NET App)      │
│                     │    │                      │    │                 │
│ - Natural Language  │    │ - MCP Tool Defs      │    │ - Todo CRUD     │
│ - Agent Runtime     │    │ - Azure Client       │    │ - HTTP API      │
│ - Tool Orchestration│    │ - Error Handling     │    │ - Database      │
└─────────────────────┘    └──────────────────────┘    └─────────────────┘
```

## References

- [Azure AI Foundry MCP Support Blog Post](https://devblogs.microsoft.com/foundry/announcing-model-context-protocol-support-preview-in-azure-ai-foundry-agent-service/)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [Azure AI Foundry Documentation](https://learn.microsoft.com/azure/ai-studio/)
