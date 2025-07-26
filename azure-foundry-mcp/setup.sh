#!/bin/bash

# Setup script for Azure AI Foundry MCP integration

echo "🚀 Setting up Azure AI Foundry MCP Integration..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file from template..."
    cp .env.template .env
    echo "📝 Please edit .env file with your Azure AI Foundry details:"
    echo "   - AZURE_SUBSCRIPTION_ID"
    echo "   - AZURE_RESOURCE_GROUP" 
    echo "   - AZURE_PROJECT_NAME"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your Azure AI Foundry project details"
echo "2. Make sure your local MCP server is running (dotnet run in main project)"
echo "3. Run the script: python connect_mcp_to_foundry.py"
echo ""
echo "To activate the virtual environment manually:"
echo "  source venv/bin/activate"
