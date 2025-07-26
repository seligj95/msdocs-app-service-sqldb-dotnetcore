#!/bin/bash

# Setup Python environment for Azure AI + MCP integration
echo "🐍 Setting up Python environment for Azure AI + MCP integration..."

# Check Python version
python_version=$(python3 --version 2>&1 | grep -o '[0-9]\+\.[0-9]\+')
echo "📋 Found Python version: $python_version"

# Navigate to the azure-foundry-mcp directory
cd /workspaces/$(basename $PWD)/azure-foundry-mcp

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo "⚠️  requirements.txt not found in azure-foundry-mcp directory"
    echo "💡 Skipping Python package installation"
    exit 0
fi

# Create Python virtual environment
echo "📦 Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment and install dependencies
echo "🔧 Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip

# Install the required packages
pip install -r requirements.txt

echo "✅ Python environment setup complete!"
echo ""
echo "🚀 To get started:"
echo "1. cd azure-foundry-mcp"
echo "2. source venv/bin/activate"
echo "3. cp .env.template .env"
echo "4. Edit .env with your Azure configuration"
echo "5. python connect_mcp_openai.py"
echo ""
echo "📚 See README.md for full setup instructions"
