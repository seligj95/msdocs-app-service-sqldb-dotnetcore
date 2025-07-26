# .devcontainer directory

This `.devcontainer` directory contains the configuration for a [dev container](https://docs.github.com/codespaces/setting-up-your-project-for-codespaces/adding-a-dev-container-configuration/introduction-to-dev-containers) and isn't used by the sample application.

The dev container configuration lets you open the repository in a [GitHub codespace](https://docs.github.com/codespaces/overview) or a dev container in Visual Studio Code. For your convenience, the dev container is configured with the following:

## 🛠️ Pre-installed Tools

- **.NET 8**: ASP.NET Core application development
- **SQL Server**: Database for the todo application
- **Azure CLI**: Command-line tool for Azure resource management
- **[Azure Developer CLI](https://learn.microsoft.com/azure/developer/azure-developer-cli/overview)**: So you can run `azd` commands directly

## 🎯 VS Code Extensions

- **GitHub Copilot**: AI-powered code completion
- **Azure Extensions**: Azure account and Azure Developer CLI integration
- **C# Dev Kit**: Enhanced .NET development
- **SQL Server extension**: (uncomment code in [devcontainer.json](devcontainer.json))

## 🚀 Auto-Setup Features

The dev container automatically:

1. **Sets up SQL Server** with the todo database
2. **Configures port forwarding** for local development (5093 HTTP, 7085 HTTPS)

## 🔧 Getting Started

After the container builds, you can immediately:

```bash
# Run the .NET application with integrated Azure AI chat
dotnet run
```

The application includes an integrated Azure AI chat interface with MCP protocol support for managing todos. See the main [README.md](../README.md) for complete setup instructions.