# Docker Dev Assistant

A simple MCP server that helps you manage Docker containers through natural language. Query running containers, inspect logs, monitor resource usage, and read Docker Compose configurations—all through your AI assistant.

## Overview

This is the foundational project in the MCP examples series. It demonstrates:

- **Basic MCP server structure**: How to set up and initialize an MCP server
- **Tool implementation**: Creating callable functions with parameters
- **Resource exposure**: Making files (like docker-compose.yml) accessible to the AI
- **Prompt templates**: Guided workflows for common tasks (debugging)
- **Error handling**: Gracefully handling missing dependencies and failures
- **Subprocess management**: Safely executing Docker commands

## Features

### Tools

1. **docker_ps** - List Docker containers
   - Shows running containers by default
   - Optional `all` parameter to show stopped containers too
   - Returns container ID, name, image, status, and ports

2. **docker_logs** - Get container logs
   - Retrieve recent logs from any container
   - Configurable number of lines (default: 50)
   - Useful for debugging issues

3. **docker_stats** - Monitor resource usage
   - CPU and memory usage for running containers
   - Network and disk I/O statistics
   - Can target specific container or show all

4. **read_docker_compose** - Read Docker Compose files
   - Parse and display docker-compose.yml
   - Supports custom file paths
   - Helps understand service configurations

### Resources

- **docker-compose.yml**: Automatically exposed as a readable resource if present in the working directory

### Prompts

- **debug-container**: Automated debugging workflow that checks container status, retrieves logs, monitors resources, and suggests fixes

## Prerequisites

- **Python 3.10+**
- **Docker** installed and running
- **MCP SDK**: `pip install mcp`
- **Claude Desktop** (or another MCP-compatible client)

## Installation

1. **Create and activate a virtual environment** (if not already done):
   ```bash
   # From the repository root
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Navigate to this directory:**
   ```bash
   cd docker-dev-assistant
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Test the server:**
   ```bash
   python3 server.py
   ```

   If Docker is running, you should see:
   ```
   INFO:docker-dev-assistant:Starting Docker Dev Assistant MCP Server
   INFO:docker-dev-assistant:Docker is available and running
   ```

## Configuration

### Claude Desktop Setup

1. **Locate the Claude Desktop config file:**

   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

2. **Add the server configuration:**

   ```json
   {
     "mcpServers": {
       "docker-dev-assistant": {
         "command": "/absolute/path/to/python-mcp-servers/venv/bin/python3",
         "args": ["/absolute/path/to/python-mcp-servers/docker-dev-assistant/server.py"]
       }
     }
   }
   ```

   **⚠️ Important**:
   - Replace `/absolute/path/to/` with the actual path on your system
   - **Must use venv Python** - The directory is named `venv` (not `.venv`)
   - Use absolute paths - No `~/` or relative paths
   - Example: `/Users/yourname/python-mcp-servers/venv/bin/python3`

3. **Restart Claude Desktop** (fully quit and reopen)

### Using a Virtual Environment

If using a virtual environment, point to the venv's Python:

```json
{
  "mcpServers": {
    "docker-dev-assistant": {
      "command": "/absolute/path/to/venv/bin/python3",
      "args": ["/absolute/path/to/docker-dev-assistant/server.py"]
    }
  }
}
```

## Usage

Once configured, you can interact with Docker through natural language in Claude Desktop.

### Example Queries

**List containers:**
```
What Docker containers are running?
Show me all containers, including stopped ones.
```

**Get logs:**
```
Show me the logs for the nginx container
Get the last 100 lines from container web-app
```

**Monitor resources:**
```
What's the CPU and memory usage of my containers?
Show me resource stats for the database container
```

**Read configuration:**
```
Show me the docker-compose.yml file
What services are defined in my Docker Compose setup?
```

**Debug issues:**
```
Help me debug the api-server container
Why isn't my postgres container starting?
```

### Using the Debug Prompt

The debug prompt provides a guided workflow:

```
Use the debug-container prompt for my-failing-container
```

This automatically:
1. Checks if the container is running
2. Retrieves recent logs
3. Checks resource usage
4. Analyzes the information
5. Suggests next steps

## How It Works

### Server Structure

```python
from mcp.server import Server
from mcp.server.stdio import stdio_server

# Initialize the server
server = Server("docker-dev-assistant")

# Define tools
@server.list_tools()
async def list_tools() -> list[Tool]:
    return [...]

@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    # Tool implementation
    ...
```

### Key MCP Concepts

#### 1. Tools

Tools are functions the AI can call. They're defined in two parts:

**Declaration** (`list_tools`):
```python
Tool(
    name="docker_ps",
    description="List all Docker containers",
    inputSchema={
        "type": "object",
        "properties": {
            "all": {"type": "boolean", "description": "Show all containers"}
        }
    }
)
```

**Implementation** (`call_tool`):
```python
if name == "docker_ps":
    show_all = arguments.get("all", False)
    # Execute Docker command and return results
```

#### 2. Resources

Resources are data sources the AI can read:

```python
@server.list_resources()
async def list_resources() -> list[Resource]:
    return [
        Resource(
            uri="file:///path/to/docker-compose.yml",
            name="docker-compose.yml",
            mimeType="text/yaml"
        )
    ]
```

#### 3. Prompts

Prompts are reusable templates:

```python
@server.get_prompt()
async def get_prompt(name: str, arguments: dict):
    return [{
        "role": "user",
        "content": {"type": "text", "text": prompt_text}
    }]
```

### Docker Command Execution

The server uses Python's `subprocess` module to safely execute Docker commands:

```python
def run_docker_command(args: list[str]) -> tuple[str, str, int]:
    """Run a Docker command and return stdout, stderr, return code."""
    result = subprocess.run(
        ["docker"] + args,
        capture_output=True,
        text=True,
        timeout=30
    )
    return result.stdout, result.stderr, result.returncode
```

This approach:
- Captures output for parsing
- Handles timeouts (30 seconds)
- Checks for Docker availability
- Returns clear error messages

### Error Handling

The server checks if Docker is available before executing commands:

```python
def check_docker_available() -> tuple[bool, str]:
    """Check if Docker is available and running."""
    stdout, stderr, returncode = run_docker_command(["info"])
    if returncode == 0:
        return True, ""
    return False, stderr or "Docker is not running"
```

If Docker isn't available, tools return helpful error messages instead of crashing.

## Extending

Here are some ideas for extending this server:

### Add More Tools

**Stop a container:**
```python
Tool(
    name="docker_stop",
    description="Stop a running container",
    inputSchema={
        "type": "object",
        "properties": {
            "container": {"type": "string", "description": "Container name or ID"}
        },
        "required": ["container"]
    }
)
```

**Start a container:**
```python
Tool(
    name="docker_start",
    description="Start a stopped container",
    inputSchema={
        "type": "object",
        "properties": {
            "container": {"type": "string", "description": "Container name or ID"}
        },
        "required": ["container"]
    }
)
```

**Execute commands in container:**
```python
Tool(
    name="docker_exec",
    description="Execute a command inside a running container",
    inputSchema={
        "type": "object",
        "properties": {
            "container": {"type": "string"},
            "command": {"type": "string"}
        },
        "required": ["container", "command"]
    }
)
```

### Expose More Resources

- Dockerfile contents
- Container configuration details
- Volume mappings
- Network configurations

### Add More Prompts

- **optimize-resources**: Analyze and suggest resource optimizations
- **health-check**: Comprehensive health check across all containers
- **backup-volumes**: Guide through backing up Docker volumes

## Troubleshooting

### Server doesn't appear in Claude Desktop

1. Check JSON syntax in config file (use [jsonlint.com](https://jsonlint.com))
2. Verify the path to `server.py` is absolute and correct
3. Ensure Python executable path is correct
4. Restart Claude Desktop completely (Cmd+Q on macOS)

### "Docker is not available" error

1. Ensure Docker Desktop is running
2. Test Docker from command line: `docker ps`
3. Check Docker permissions (user should be in docker group on Linux)

### "Container not found" error

1. Check container name with `docker ps -a`
2. Try using container ID instead of name
3. Ensure the container exists and hasn't been removed

### Tools not being called

1. Make tool descriptions more specific
2. Try explicitly requesting: "Use the docker_ps tool to list containers"
3. Check Claude Desktop logs for errors

## Example Usage

Here are some example conversations showing how to use the Docker Dev Assistant with Claude Desktop.

### Basic Container Management

#### Listing Containers

**User:**
```
What Docker containers are running on my system?
```

**Claude's Response:**
```
I'll check your running containers.

[Uses docker_ps tool]

You have 3 containers running:

1. web (nginx:alpine)
   - Status: Up 2 hours
   - Ports: 0.0.0.0:8080->80/tcp

2. db (postgres:15-alpine)
   - Status: Up 2 hours
   - Ports: 5432/tcp

3. cache (redis:7-alpine)
   - Status: Up 2 hours
   - Ports: 0.0.0.0:6379->6379/tcp

All containers appear to be healthy and running normally.
```

#### Viewing Logs

**User:**
```
Show me the latest logs from the web container
```

**Claude's Response:**
```
I'll fetch the recent logs for you.

[Uses docker_logs tool with container="web", lines=50]

Here are the last 50 lines from the web container:

192.168.1.100 - - [03/Feb/2025:10:15:23 +0000] "GET / HTTP/1.1" 200 612
192.168.1.100 - - [03/Feb/2025:10:15:24 +0000] "GET /style.css HTTP/1.1" 200 1234
192.168.1.100 - - [03/Feb/2025:10:15:30 +0000] "GET /api/users HTTP/1.1" 200 456

The logs show normal HTTP traffic with successful 200 responses. No errors are present.
```

### Resource Monitoring

#### Checking Container Stats

**User:**
```
What are the resource stats for my containers?
```

**Claude's Response:**
```
Let me check the resource usage.

[Uses docker_stats tool]

Resource usage for your containers:

CONTAINER   CPU %    MEM USAGE / LIMIT     MEM %    NET I/O           BLOCK I/O
web         0.02%    12.5MiB / 7.775GiB    0.16%    5.2kB / 3.1kB     0B / 0B
db          0.35%    145.2MiB / 7.775GiB   1.82%    12.3kB / 8.5kB    45MB / 12MB
cache       0.01%    8.2MiB / 7.775GiB     0.11%    1.1kB / 890B      0B / 0B

Everything looks healthy:
- CPU usage is low across all containers
- Memory usage is well within limits
- The database has moderate I/O as expected
- No resource constraints detected
```

### Configuration Review

#### Reading Docker Compose File

**User:**
```
Show me my Docker Compose configuration
```

**Claude's Response:**
```
I'll read your docker-compose.yml file.

[Uses read_docker_compose tool]

Your Docker Compose setup defines 3 services:

1. **web** (nginx:alpine)
   - Exposes port 8080 → 80
   - Mounts local html directory
   - Auto-restart enabled

2. **db** (postgres:15-alpine)
   - Environment variables for user/password/database
   - Persistent volume for data storage
   - Connected to app-network

3. **cache** (redis:7-alpine)
   - Exposes port 6379
   - Auto-restart enabled
   - Connected to app-network

All services are on a shared bridge network (app-network) for inter-container communication.
The database uses a named volume (postgres-data) for data persistence.
```

### Debugging Workflows

#### Using the Debug Prompt

**User:**
```
Help me debug the db container using your debug workflow
```

**Claude's Response:**
```
I'll run through a comprehensive debugging check.

[Uses the debug-container prompt with container_name="db"]

Debug Report for Container: db
================================

1. Container Status:
   [Uses docker_ps tool]
   ✓ Container is running (Up 2 hours)
   ✓ Status appears healthy

2. Recent Logs (last 100 lines):
   [Uses docker_logs tool with container="db", lines=100]

   2025-02-03 10:00:15.123 UTC [1] LOG:  database system is ready to accept connections
   2025-02-03 10:05:20.456 UTC [23] LOG:  connection received
   2025-02-03 10:05:20.457 UTC [23] LOG:  connection authorized

   ✓ No errors in recent logs
   ✓ Database is accepting connections normally

3. Resource Usage:
   [Uses docker_stats tool with container="db"]

   CPU: 0.35%
   Memory: 145.2MiB / 7.775GiB (1.82%)

   ✓ Resource usage is normal
   ✓ No memory pressure or CPU spikes

Summary:
--------
The db container appears to be running normally with no issues detected.
- Container is healthy and running
- No errors in logs
- Resource usage is appropriate
- Accepting connections successfully

If you're experiencing issues, they might be:
- Connection problems from client applications
- Incorrect credentials being used
- Network configuration issues

Let me know if you need help investigating any specific aspect!
```

### Tips for Effective Use

**Be Specific:**
```
❌ "Check Docker"
✓ "Show me logs for the nginx container"
```

**Use Natural Language:**
```
✓ "Which container is using the most memory?"
✓ "Is my postgres container healthy?"
✓ "Why is the web container not responding?"
```

**Combine Multiple Operations:**
```
✓ "Check if all my containers are running, and if any have errors in their logs"
✓ "Show me the resource usage and recent logs for the api container"
```

## Next Project

Once you're comfortable with this server, move on to the **Personal Knowledge Base** to learn about:

- File system operations
- Vector embeddings and semantic search
- Dynamic resource discovery
- More complex data handling

[→ Go to Personal Knowledge Base](../personal-knowledge-base/)

## Additional Resources

- [MCP Documentation](https://modelcontextprotocol.io)
- [Docker CLI Reference](https://docs.docker.com/engine/reference/commandline/cli/)
- [Python subprocess module](https://docs.python.org/3/library/subprocess.html)

---

**Questions or issues?** Check the main [README](../README.md) or [Setup Guide](../docs/setup-guide.md).
