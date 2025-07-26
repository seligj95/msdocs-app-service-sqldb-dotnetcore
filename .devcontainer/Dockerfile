FROM mcr.microsoft.com/devcontainers/dotnet:1-8.0-bookworm

# Install SQL Tools: SQLPackage and sqlcmd
COPY mssql/installSQLtools.sh installSQLtools.sh
RUN bash ./installSQLtools.sh \
     && apt-get clean -y && rm -rf /var/lib/apt/lists/* /tmp/library-scripts

# Install Python 3.11+ and pip for Azure AI + MCP integration
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
        python3.11 \
        python3.11-venv \
        python3-pip \
        python3.11-dev \
        build-essential \
        curl \
        git \
    && apt-get clean -y && rm -rf /var/lib/apt/lists/*

# Create symlinks for python and pip commands
RUN ln -sf /usr/bin/python3.11 /usr/bin/python \
    && ln -sf /usr/bin/python3.11 /usr/bin/python3

# Install Azure CLI (latest version)
RUN curl -sL https://aka.ms/InstallAzureCLIDeb | bash

# [Optional] Uncomment this line to install global node packages.
# RUN su vscode -c "source /usr/local/share/nvm/nvm.sh && npm install -g <your-package-here>" 2>&1
