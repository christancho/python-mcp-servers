#!/usr/bin/env python3
"""
Docker Dev Assistant MCP Server

A simple MCP server that provides tools for managing Docker containers.
This is a foundational example demonstrating:
- Basic MCP server structure
- Tool implementation with parameters
- Resource exposure (docker-compose.yml)
- Error handling
- Subprocess management for Docker commands
"""

import asyncio
import json
import logging
import os
import subprocess
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.types import Resource, Tool, TextContent, ImageContent, EmbeddedResource
from mcp.server.stdio import stdio_server

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("docker-dev-assistant")

# Initialize MCP server
server = Server("docker-dev-assistant")

# Get the directory where this script lives
SCRIPT_DIR = Path(__file__).parent


def run_docker_command(args: list[str]) -> tuple[str, str, int]:
    """
    Run a Docker command and return stdout, stderr, and return code.

    Args:
        args: Command arguments to pass to docker

    Returns:
        Tuple of (stdout, stderr, return_code)
    """
    try:
        result = subprocess.run(
            ["docker"] + args,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", "Command timed out after 30 seconds", 1
    except FileNotFoundError:
        return "", "Docker is not installed or not in PATH", 1
    except Exception as e:
        return "", f"Error running docker command: {str(e)}", 1


def check_docker_available() -> tuple[bool, str]:
    """
    Check if Docker is available and running.

    Returns:
        Tuple of (is_available, error_message)
    """
    stdout, stderr, returncode = run_docker_command(["info"])
    if returncode == 0:
        return True, ""
    return False, stderr or "Docker is not running"


# MCP Tool Handlers

@server.list_tools()
async def list_tools() -> list[Tool]:
    """
    List all available tools.

    MCP calls this to discover what tools this server provides.
    Each tool should have a clear name, description, and input schema.
    """
    return [
        Tool(
            name="docker_ps",
            description="List all Docker containers (running and stopped). Shows container ID, name, image, status, and ports.",
            inputSchema={
                "type": "object",
                "properties": {
                    "all": {
                        "type": "boolean",
                        "description": "Show all containers (default shows just running)",
                        "default": False
                    }
                }
            }
        ),
        Tool(
            name="docker_logs",
            description="Get logs from a Docker container. Useful for debugging issues.",
            inputSchema={
                "type": "object",
                "properties": {
                    "container": {
                        "type": "string",
                        "description": "Container name or ID"
                    },
                    "lines": {
                        "type": "number",
                        "description": "Number of lines to show (default: 50)",
                        "default": 50
                    }
                },
                "required": ["container"]
            }
        ),
        Tool(
            name="docker_stats",
            description="Get resource usage statistics for running containers (CPU, memory, network, disk I/O).",
            inputSchema={
                "type": "object",
                "properties": {
                    "container": {
                        "type": "string",
                        "description": "Specific container name or ID (optional, shows all if not provided)"
                    }
                }
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """
    Handle tool calls from the MCP client.

    This is where the actual tool logic is implemented.
    Each tool should validate inputs and return clear, structured output.
    """
    logger.info(f"Tool called: {name} with arguments: {arguments}")

    # Check if Docker is available for Docker-related tools
    if name in ["docker_ps", "docker_logs", "docker_stats"]:
        available, error = check_docker_available()
        if not available:
            return [TextContent(
                type="text",
                text=f"Error: Docker is not available. {error}\n\nPlease ensure Docker is installed and running."
            )]

    # Handle each tool
    if name == "docker_ps":
        show_all = arguments.get("all", False)
        args = ["ps"]
        if show_all:
            args.append("-a")

        stdout, stderr, returncode = run_docker_command(args)

        if returncode != 0:
            return [TextContent(
                type="text",
                text=f"Error listing containers: {stderr}"
            )]

        return [TextContent(
            type="text",
            text=stdout or "No containers found."
        )]

    elif name == "docker_logs":
        container = arguments.get("container")
        lines = arguments.get("lines", 50)

        if not container:
            return [TextContent(
                type="text",
                text="Error: Container name or ID is required."
            )]

        stdout, stderr, returncode = run_docker_command([
            "logs",
            "--tail", str(lines),
            container
        ])

        if returncode != 0:
            return [TextContent(
                type="text",
                text=f"Error getting logs for container '{container}': {stderr}"
            )]

        return [TextContent(
            type="text",
            text=stdout or f"No logs found for container '{container}'."
        )]

    elif name == "docker_stats":
        container = arguments.get("container")

        # Use --no-stream to get a single snapshot instead of continuous updates
        args = ["stats", "--no-stream"]
        if container:
            args.append(container)

        stdout, stderr, returncode = run_docker_command(args)

        if returncode != 0:
            return [TextContent(
                type="text",
                text=f"Error getting stats: {stderr}"
            )]

        return [TextContent(
            type="text",
            text=stdout or "No running containers to show stats for."
        )]

    else:
        return [TextContent(
            type="text",
            text=f"Unknown tool: {name}"
        )]


# MCP Resource Handlers

@server.list_resources()
async def list_resources() -> list[Resource]:
    """
    List available resources.

    This server doesn't expose any static resources - it connects to
    the existing Docker daemon and provides tools to interact with it.
    """
    return []


@server.read_resource()
async def read_resource(uri: str) -> str:
    """
    Read a resource by URI.

    This is called when the AI wants to access a resource.
    """
    logger.info(f"Resource requested: {uri}")

    # Extract file path from URI
    if uri.startswith("file://"):
        file_path = Path(uri[7:])

        if not file_path.exists():
            raise ValueError(f"File not found: {file_path}")

        return file_path.read_text()

    raise ValueError(f"Unsupported URI scheme: {uri}")


# MCP Prompt Handlers

@server.list_prompts()
async def list_prompts() -> list[dict]:
    """
    List available prompt templates.

    Prompts are reusable templates that help users accomplish common tasks.
    """
    return [
        {
            "name": "debug-container",
            "description": "Help debug a Docker container that's failing or misbehaving",
            "arguments": [
                {
                    "name": "container_name",
                    "description": "Name or ID of the container to debug",
                    "required": True
                }
            ]
        }
    ]


@server.get_prompt()
async def get_prompt(name: str, arguments: dict) -> list[Any]:
    """
    Get a prompt template with arguments filled in.

    This generates a prompt that guides the AI through a workflow.
    """
    if name == "debug-container":
        container_name = arguments.get("container_name", "")

        prompt_text = f"""Help me debug the Docker container '{container_name}'.

Please perform the following steps:

1. Check if the container is running using docker_ps
2. If it's running, get the last 100 lines of logs using docker_logs
3. Check resource usage with docker_stats
4. Analyze the information and suggest potential issues

Based on what you find, provide:
- Current status of the container
- Any errors or warnings in the logs
- Resource usage concerns (high CPU/memory)
- Suggested next steps for debugging
"""

        return [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": prompt_text
                }
            }
        ]

    raise ValueError(f"Unknown prompt: {name}")


async def main():
    """Main entry point for the MCP server."""
    logger.info("Starting Docker Dev Assistant MCP Server")

    # Check if Docker is available at startup
    available, error = check_docker_available()
    if not available:
        logger.warning(f"Docker is not available: {error}")
        logger.warning("Server will start but Docker tools may not work")
    else:
        logger.info("Docker is available and running")

    # Run the server using stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
