---
languages:
- csharp
- aspx-csharp
- bicep
page_type: sample
products:
- azure
- aspnet-core
- azure-app-service
- azure-sql-database
- azure-virtual-network
urlFragment: msdocs-app-service-sqldb-dotnetcore
name: Deploy an ASP.NET Core web app with SQL Database in Azure
description: "A sample application you can use to follow along with Tutorial: Deploy an ASP.NET Core and Azure SQL Database app to Azure App Service."
---

# Deploy an ASP.NET Core web app with SQL Database in Azure

This is an ASP.NET Core application that you can use to follow along with the tutorial at 
[Tutorial: Deploy an ASP.NET Core and Azure SQL Database app to Azure App Service](https://learn.microsoft.com/azure/app-service/tutorial-dotnetcore-sqldb-app) or by using the [Azure Developer CLI (azd)](https://learn.microsoft.com/azure/developer/azure-developer-cli/overview) according to the instructions below.

## 🤖 NEW: AI Chat Interface

This application now includes a built-in AI chat interface that lets you manage todos using natural language! Features include:

- **💬 Web-based Chat UI**: No need for separate Python scripts - chat directly in the web app
- **🔗 Azure OpenAI Integration**: Uses Azure OpenAI with function calling to interact with your todos
- **📱 Mobile-friendly Interface**: Responsive design works on all devices
- **⚡ Real-time Responses**: Instant AI responses with loading indicators

### How to Use the Chat Interface

1. **Navigate to Chat**: Click "AI Chat" in the navigation menu
2. **Start Chatting**: Type natural language commands like:
   - "Show me all my todos"
   - "Create a todo: Buy groceries tomorrow"  
   - "Delete the first todo"
   - "How many todos do I have?"

### Configuration for AI Chat

#### Local Development
Update your `appsettings.json` with your Azure OpenAI details:

```json
{
  "AZURE_OPENAI_ENDPOINT": "https://your-openai-resource.openai.azure.com/",
  "AZURE_OPENAI_DEPLOYMENT_NAME": "gpt-4o-mini",
  "LOCAL_MCP_URL": "http://localhost:5093/api/mcp"
}
```

#### Azure App Service Deployment
When deploying to Azure App Service, you need to configure managed identity and app settings:

1. **Enable System Assigned Managed Identity**:
   - Go to your App Service → Identity → System assigned
   - Toggle Status to "On" and Save

2. **Grant Azure OpenAI Access**:
   - Navigate to your Azure OpenAI resource → Access control (IAM)
   - Add role assignment: "Cognitive Services User"
   - Assign to your App Service's managed identity

3. **Configure App Settings** in your App Service:
   ```
   AZURE_OPENAI_ENDPOINT = https://your-openai-resource.openai.azure.com/
   AZURE_OPENAI_DEPLOYMENT_NAME = gpt-4o-mini
   LOCAL_MCP_URL = https://your-app-service-name.azurewebsites.net/api/mcp
   ```

The managed identity allows secure authentication to Azure OpenAI without storing API keys.

## Run the sample

This project has a [dev container configuration](.devcontainer/), which makes it easier to develop apps locally, deploy them to Azure, and monitor them. The easiest way to run this sample application is inside a GitHub codespace. Follow these steps:

1. Fork this repository to your account.

1. From the repository root of your fork, select **Code** > **Codespaces** > **+**.

1. In the codespace terminal, run the following commands:

    ```shell
    dotnet ef database update
    dotnet run
    ```

1. When you see the message `Your application running on port 5093 is available.`, click **Open in Browser**.

## Quick deploy

This project is designed to work well with the [Azure Developer CLI](https://learn.microsoft.com/azure/developer/azure-developer-cli/overview), which makes it easier to develop apps locally, deploy them to Azure, and monitor them.

🎥 Watch a deployment of the code in [this screencast](https://www.youtube.com/watch?v=JDlZ4TgPKYc).

In the GitHub codespace:

1. Log in to Azure.

    ```shell
    azd auth login
    ```

1. Provision and deploy all the resources:

    ```shell
    azd up
    ```

    It will prompt you to create a deployment environment name, pick a subscription, and provide a location (like `westeurope`). Then it will provision the resources in your account and deploy the latest code. If you get an error with deployment, changing the location (like to "centralus") can help, as there may be availability constraints for some of the resources.

1. When `azd` has finished deploying, you'll see an endpoint URI in the command output. Visit that URI, and you should see the CRUD app! 🎉 If you see an error, open the Azure Portal from the URL in the command output, navigate to the App Service, select Logstream, and check the logs for any errors.

1. When you've made any changes to the app code, you can just run:

    ```shell
    azd deploy
    ```

## How is database migrations automated?

The [AZD template](infra/resources.bicep) in this repo secures the database in a virtual network through a private endpoint. The web app can access the database through the private endpoint because it's integrated with the virtual network. In this architecture, the simplest way to do database migrations is directly from within the web app itself.

Because the Linux .NET container in App Service doesn't come with the .NET SDK, you cannot run the migrations command `dotnet ef database update` easily. However, you can upload a [self-contained migrations bundle](https://learn.microsoft.com/ef/core/managing-schemas/migrations/applying?tabs=dotnet-core-cli#bundles). This repo automates the deployment of the migrations bundle as follows:

- In [azure.yaml](azure.yaml), use the `prepackage` hook to generate a *migrationsbundle* file with `dotnet ef migrations bundle`.
- In the [.csproj](DotNretCoreSqlDb.csproj) file, include the generated *migrationsbundle* file. During the `azd package` stage, *migrationsbundle* will be added to the deploy package.
- In [infra/resources.bicep](infra/resources.bicep), add the `appCommandLine` property to the web app to run the uploaded *migrationsbundle*.

## How does the AZD template configure passwords?

Two types of secrets are involved: the SQL Database administrator password and the access key for Cache for Redis, and they are both present in the respective connection strings. The [AZD template](infra/resources.bicep) in this repo manages both connection strings in a key vault that's secured behind a private endpoint.

To simplify the scenario, the AZD template generates a new database password each time you run `azd provision` or `azd up`, and the database connection string in the key vault is modified too. If you want to fully utilize `secretOrRandomPassword` in the [parameter file](infra/main.parameters.json) by committing the automatically generated password to the key vault the first time and reading it on subsequent `azd` commands, you must relax the networking restriction of the key vault to allow traffic from public networks. For more information, see [What is the behavior of the `secretOrRandomPassword` function?](https://learn.microsoft.com/azure/developer/azure-developer-cli/faq#what-is-the-behavior-of-the--secretorrandompassword--function).

## Getting help

If you're working with this project and running into issues, please post in [Issues](/issues).
