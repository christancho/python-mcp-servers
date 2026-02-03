# Setup Guide

This guide walks you through setting up your environment to build and test MCP servers with these examples.

## Prerequisites

### 1. Python 3.10 or Higher

Check your Python version:

```bash
python3 --version
```

If you need to install or upgrade Python:

- **macOS**: Use [Homebrew](https://brew.sh/)
  ```bash
  brew install python@3.11
  ```

- **Linux**: Use your package manager
  ```bash
  # Ubuntu/Debian
  sudo apt update
  sudo apt install python3.11 python3.11-venv python3-pip

  # Fedora
  sudo dnf install python3.11
  ```

- **Windows**: Download from [python.org](https://www.python.org/downloads/)

### 2. Claude Desktop

Claude Desktop is the easiest way to test MCP servers. Download it from:

- [Claude Desktop Download](https://claude.ai/download)

Available for macOS, Windows, and Linux.

### 3. Docker (Optional)

Required only for the Docker Dev Assistant example:

- **macOS/Windows**: [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- **Linux**: [Docker Engine](https://docs.docker.com/engine/install/)

Verify installation:

```bash
docker --version
docker ps
```

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/mcp-examples.git
cd mcp-examples
```

### 2. Create a Virtual Environment

Using a virtual environment keeps dependencies isolated:

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

Your prompt should now show `(venv)` indicating the virtual environment is active.

### 3. Install Shared Dependencies

```bash
pip install -r requirements.txt
```

This installs the core MCP SDK and common dependencies used across projects.

### 4. Install Project-Specific Dependencies

Each project has its own requirements. For example:

```bash
cd docker-dev-assistant
pip install -r requirements.txt
```

Repeat this for each project you want to use.

## Configuring Claude Desktop

Claude Desktop needs to know about your MCP servers. This is done through a configuration file.

### Configuration File Location

The location depends on your operating system:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### Configuration Format

The configuration file uses JSON format. Here's the general structure:

```json
{
  "mcpServers": {
    "server-name": {
      "command": "python3",
      "args": ["/absolute/path/to/server.py"],
      "env": {
        "OPTIONAL_ENV_VAR": "value"
      }
    }
  }
}
```

### Example Configuration

Here's an example with all three projects configured:

```json
{
  "mcpServers": {
    "docker-dev-assistant": {
      "command": "python3",
      "args": ["/Users/yourname/mcp-examples/docker-dev-assistant/server.py"]
    },
    "personal-knowledge-base": {
      "command": "python3",
      "args": ["/Users/yourname/mcp-examples/personal-knowledge-base/server.py"],
      "env": {
        "NOTES_DIR": "/Users/yourname/notes"
      }
    },
    "smart-day-planner": {
      "command": "python3",
      "args": ["/Users/yourname/mcp-examples/smart-day-planner/server.py"],
      "env": {
        "OPENWEATHER_API_KEY": "your-api-key-here",
        "TODOIST_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

**Important Notes:**

1. **Use Absolute Paths**: Always use full paths, not relative paths like `~/` or `./`
2. **Use Your Python**: The `command` should point to your Python executable. If using a virtual environment, point to the venv's Python:
   ```json
   "command": "/Users/yourname/mcp-examples/venv/bin/python3"
   ```
3. **One Server at a Time**: When learning, start with just one server configured

### Step-by-Step Configuration

1. **Locate the config file** (create it if it doesn't exist):
   ```bash
   # macOS
   mkdir -p ~/Library/Application\ Support/Claude
   touch ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

2. **Edit the file** with your text editor:
   ```bash
   # macOS
   open ~/Library/Application\ Support/Claude/claude_desktop_config.json

   # Linux
   nano ~/.config/Claude/claude_desktop_config.json
   ```

3. **Add your server configuration** (see project READMEs for specific configs)

4. **Save the file**

5. **Restart Claude Desktop** completely (quit and reopen)

6. **Verify** the server loaded by checking Claude Desktop's settings or trying a test query

## Troubleshooting

### Server Not Appearing

If your server doesn't show up in Claude Desktop:

1. **Check JSON syntax**: Use a JSON validator like [jsonlint.com](https://jsonlint.com)
2. **Check file path**: Ensure the path to `server.py` is absolute and correct
3. **Check Python path**: Ensure the Python executable exists
4. **Check permissions**: Ensure Claude Desktop can execute the Python script
5. **Restart Claude Desktop**: Fully quit and reopen the application
6. **Check logs**: Look for error messages in Claude Desktop's developer console

### Import Errors

If you get `ModuleNotFoundError`:

1. **Install dependencies**: Run `pip install -r requirements.txt` in the project directory
2. **Check virtual environment**: Ensure you're using the same Python that has the packages installed
3. **Use absolute path to venv Python**: In the config, use `/path/to/venv/bin/python3` instead of system Python

### Server Starts But Tools Don't Work

1. **Check server logs**: Add logging to your server (see project code for examples)
2. **Test outside Claude**: Run the server script directly to see error messages
3. **Check prerequisites**: Ensure Docker is running (for Docker Dev Assistant), notes exist (for Knowledge Base), etc.

### Environment Variables Not Working

1. **Check syntax**: Ensure the `env` object in config is properly formatted
2. **Check values**: Ensure no extra quotes or spaces in environment variable values
3. **Restart Claude**: Environment variables are loaded at startup

## Testing Your Setup

Once configured, test that everything works:

1. **Open Claude Desktop**
2. **Start a new conversation**
3. **Try a simple query** that would use your server

For Docker Dev Assistant:
```
What Docker containers are currently running?
```

For Personal Knowledge Base:
```
Search my notes for "machine learning"
```

For Smart Day Planner:
```
What's the weather like today?
```

If Claude successfully calls your MCP server and returns results, you're all set up!

## Next Steps

Now that your environment is ready:

1. **Start with Docker Dev Assistant**: [Docker Dev Assistant](../docker-dev-assistant/)
2. **Learn testing techniques**: [Testing with Claude](testing-with-claude.md)
3. **Explore the code**: Each project's `server.py` is heavily commented to explain MCP patterns

## Additional Resources

- [Official MCP Documentation](https://modelcontextprotocol.io)
- [Claude Desktop Settings](https://claude.ai/settings)
- [MCP Python SDK Documentation](https://github.com/modelcontextprotocol/python-sdk)

---

**Next**: [Testing with Claude](testing-with-claude.md) - Learn how to test and debug MCP servers
