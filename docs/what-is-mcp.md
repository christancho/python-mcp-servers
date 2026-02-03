# What is MCP?

## Introduction

The **Model Context Protocol (MCP)** is an open standard that enables AI applications to securely connect with external data sources and tools. MCP provides a universal way to give AI assistants access to the context they need—whether that's local files, databases, APIs, or custom tools.

## The Problem MCP Solves

Modern AI assistants are powerful, but they're limited by their training data and lack of access to your specific context:

- Your local development environment
- Your private notes and documents
- Your organization's APIs and databases
- Real-time data from external services

Without MCP, integrating each of these requires custom code for each AI application. With MCP, you write a server once and it works with any MCP-compatible client.

## How MCP Works

MCP uses a client-server architecture:

```
┌─────────────────┐         ┌──────────────────┐
│   AI Assistant  │         │   MCP Server     │
│  (Claude, etc.) │ ←─MCP──→│  (Your Code)     │
│     [Client]    │         │                  │
└─────────────────┘         └──────────────────┘
                                      ↓
                            ┌──────────────────┐
                            │   Resources      │
                            │  - Files         │
                            │  - Databases     │
                            │  - APIs          │
                            └──────────────────┘
```

1. **Client**: The AI application (e.g., Claude Desktop) that wants to use external tools
2. **Server**: Your custom code that exposes tools, resources, and prompts via the MCP protocol
3. **Resources**: The actual data sources and services your server can access

## Core MCP Concepts

### 1. Tools

**Tools** are functions that the AI can call to perform actions. They have:
- A name and description
- Input parameters (with types and descriptions)
- Return values

**Example**: A `search_files` tool that takes a query string and returns matching file paths.

```python
@server.call_tool()
async def search_files(query: str) -> list[str]:
    """Search for files matching the query."""
    # Implementation
    return matching_files
```

The AI assistant can decide when to call this tool based on user requests like "find all Python files containing 'async'".

### 2. Resources

**Resources** are data sources that the AI can read. They're identified by URIs and can represent:
- Files on disk
- Database records
- API responses
- Configuration data

**Example**: Exposing markdown files as resources:

```python
@server.list_resources()
async def list_notes() -> list[Resource]:
    """List all available notes."""
    return [
        Resource(
            uri=f"note:///{note.name}",
            name=note.name,
            mimeType="text/markdown"
        )
        for note in notes
    ]
```

### 3. Prompts

**Prompts** are reusable prompt templates that help users accomplish common tasks. They can:
- Include dynamic arguments
- Combine multiple tools and resources
- Guide the AI toward specific workflows

**Example**: A debugging prompt that automatically gathers relevant logs and context:

```python
@server.list_prompts()
async def debug_container(container_name: str) -> str:
    """Generate a debugging prompt for a container."""
    return f"""Help debug the Docker container '{container_name}'.

Please:
1. Check if the container is running
2. Review recent logs
3. Check resource usage
4. Suggest potential issues
"""
```

## Why Use MCP?

### For Developers

- **Standardized**: One protocol works with all MCP-compatible clients
- **Reusable**: Write once, use everywhere
- **Composable**: Combine multiple servers for complex workflows
- **Type-safe**: Strong typing for tools and resources
- **Well-documented**: Clear specification and SDKs

### For Users

- **Powerful**: AI assistants can access your actual data and tools
- **Secure**: You control what the AI can access
- **Flexible**: Add new capabilities without updating the AI application
- **Natural**: Interact with complex systems through natural language

## MCP vs Other Approaches

### MCP vs Custom APIs
- **MCP**: Standardized protocol, works with any client, AI-native design
- **Custom API**: Requires client-side integration, not optimized for AI interaction

### MCP vs Plugins
- **MCP**: Open standard, server runs in your environment, full control
- **Plugins**: Proprietary, often sandboxed, limited access to resources

### MCP vs RAG
- **MCP**: Interactive tools and live data access, can perform actions
- **RAG**: Static knowledge retrieval, read-only, no dynamic operations

MCP and RAG are complementary—you can use MCP to build a RAG system (like our Personal Knowledge Base example).

## When to Use MCP

MCP is ideal when you want to:

- Give AI access to local files, databases, or APIs
- Build custom tools for repetitive workflows
- Integrate AI with existing systems
- Create domain-specific AI assistants
- Enable AI to perform actions (not just retrieve information)

## Security Considerations

MCP servers run in your environment with your permissions. Security best practices:

1. **Least Privilege**: Only expose necessary tools and resources
2. **Input Validation**: Validate all parameters in tools
3. **Error Handling**: Don't leak sensitive information in errors
4. **Secrets Management**: Use environment variables for API keys
5. **Audit Logging**: Log tool invocations for security monitoring

## Getting Started

The best way to learn MCP is by building. This repository provides three progressively complex examples:

1. **Docker Dev Assistant**: Learn the basics with simple tools
2. **Personal Knowledge Base**: Add file operations and search
3. **Smart Day Planner**: Master async operations and external APIs

Start with [Docker Dev Assistant](../docker-dev-assistant/) to build your first MCP server.

## Additional Resources

- [Official MCP Documentation](https://modelcontextprotocol.io)
- [MCP Specification](https://spec.modelcontextprotocol.io)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Claude Desktop](https://claude.ai/download)

---

**Next**: [Setup Guide](setup-guide.md) - Get your environment ready for MCP development
