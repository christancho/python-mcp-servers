# MCP Examples: Real-World Python Servers

A collection of practical, production-quality MCP (Model Context Protocol) servers that showcase how to build AI-powered tools. Learn MCP by exploring three progressively complex projects, each demonstrating real-world use cases.

**📊 Repository Stats:**
- **3 Complete Examples**: From simple to advanced
- **2,100+ Lines of Code**: Production-quality implementations
- **13 Documentation Files**: Comprehensive guides and tutorials
- **Ready to Use**: Sample data and configurations included

---

## ⚡ Quick Start (5 Minutes)

### Prerequisites
- Python 3.10+
- Claude Desktop
- Git

### Step 1: Clone and Verify
```bash
git clone https://github.com/yourusername/mcp-examples.git
cd mcp-examples
python3 verify_setup.py
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
cd docker-dev-assistant
pip install -r requirements.txt
```

### Step 3: Test the Server
```bash
python3 server.py
```

You should see:
```
INFO:docker-dev-assistant:Starting Docker Dev Assistant MCP Server
```

Press Ctrl+C to stop.

### Step 4: Configure Claude Desktop

**Find your config file:**
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

**Add this configuration** (replace `/full/path/to/` with your actual path):

```json
{
  "mcpServers": {
    "docker-dev-assistant": {
      "command": "python3",
      "args": ["/full/path/to/mcp-examples/docker-dev-assistant/server.py"]
    }
  }
}
```

**Find your full path:**
```bash
cd docker-dev-assistant && pwd
```

### Step 5: Restart Claude Desktop

Fully quit and reopen Claude Desktop.

### Step 6: Test It!

Open Claude Desktop and try:
```
What Docker containers are running?
```

If Claude responds with container information (or says Docker isn't running), **it's working!** 🎉

**Troubleshooting?** See [docs/setup-guide.md](docs/setup-guide.md) for detailed help.

---

## What is MCP?

The Model Context Protocol (MCP) is an open standard that enables AI assistants like Claude to securely interact with external tools, data sources, and services. Think of it as a universal adapter that lets AI applications connect to your local environment and external APIs.

**Key Benefits:**
- **Extensibility**: Add custom capabilities to AI assistants without modifying the core application
- **Security**: Controlled access to resources through a standardized protocol
- **Reusability**: Write a server once, use it with any MCP-compatible AI client
- **Composability**: Combine multiple MCP servers to create powerful workflows

Learn more in [docs/what-is-mcp.md](docs/what-is-mcp.md)

---

## 📚 Projects Overview

This repository contains three tutorial projects, designed to be explored in order:

### 1. 🐳 Docker Dev Assistant (Simple - Foundation)

**Difficulty**: 🟢 Easy | **Time**: ~5 minutes | **Lines of Code**: 401

A practical assistant for managing Docker containers. Query running containers, check logs, and debug issues through natural language.

**What You'll Learn:**
- MCP server initialization
- Tool implementation with parameters
- Resource exposure (reading files)
- Basic error handling

**Features:**
- 4 Tools: docker_ps, docker_logs, docker_stats, read_docker_compose
- 1 Resource: docker-compose.yml exposure
- 1 Prompt: debug-container workflow

[→ Go to Docker Dev Assistant](docker-dev-assistant/)

---

### 2. 📚 Personal Knowledge Base (Intermediate - Building Complexity)

**Difficulty**: 🟡 Medium | **Time**: ~10 minutes | **Lines of Code**: 784

Transform your markdown notes into an AI-searchable knowledge base. Find information semantically, discover connections between ideas, and query your notes naturally.

**What You'll Learn:**
- File system operations and monitoring
- Vector embeddings with ChromaDB
- Semantic vs keyword search
- Dynamic resource discovery
- Hybrid search patterns

**Features:**
- 7 Tools: semantic_search, search_notes, get_note, list_notes, get_recent_notes, find_similar, index_notes
- Dynamic Resources: All markdown notes automatically exposed
- 2 Prompts: summarize-topic, connect-ideas
- Local AI: Uses sentence-transformers (no API needed)

[→ Go to Personal Knowledge Base](personal-knowledge-base/)

---

### 3. 📅 Smart Day Planner (Advanced - Production Patterns)

**Difficulty**: 🔴 Advanced | **Time**: ~5 minutes + API setup | **Lines of Code**: 760

Intelligent day planning by combining weather data, todo lists, and calendar events. Shows production-ready patterns for real-world API integration.

**What You'll Learn:**
- Async MCP servers
- External API integration (OpenWeatherMap, Todoist)
- Secrets management with .env files
- Complex tool orchestration
- Error handling across services
- Response caching and rate limiting

**Features:**
- 5 Tools: get_weather, get_forecast, list_todos, analyze_week, suggest_activities
- Async Operations: Concurrent API calls for speed
- Retry Logic: Exponential backoff for resilience
- Caching: Reduce API calls and costs

[→ Go to Smart Day Planner](smart-day-planner/)

---

## 🎓 Learning Path

We recommend following this progression:

1. **Docker Dev Assistant** (Start Here)
   - Understand MCP fundamentals
   - Learn tools, resources, and prompts
   - See basic error handling patterns

2. **Personal Knowledge Base** (Build Skills)
   - Add file operations and monitoring
   - Integrate vector search and AI
   - Handle dynamic resources

3. **Smart Day Planner** (Master Advanced Patterns)
   - Implement async operations
   - Integrate external APIs
   - Apply production error handling

Each project builds on concepts from the previous one while introducing new patterns and techniques.

---

## 📖 Documentation

### Getting Started
- [What is MCP?](docs/what-is-mcp.md) - MCP protocol explanation and key concepts
- [Setup Guide](docs/setup-guide.md) - Detailed installation and configuration
- [Testing with Claude](docs/testing-with-claude.md) - Testing and debugging techniques

### Per-Project Documentation
Each project includes:
- Comprehensive README with setup instructions
- Code walkthrough explaining MCP patterns
- Extension ideas for further learning
- Sample interactions showing real usage
- Troubleshooting guides

---

## 🏗️ Repository Structure

```
mcp-examples/
├── README.md                          # This file
├── LICENSE                            # MIT License
├── requirements.txt                   # Shared dependencies
├── verify_setup.py                    # Automated setup verification
│
├── docs/                              # Core documentation
│   ├── what-is-mcp.md                # MCP concepts
│   ├── setup-guide.md                # Installation guide
│   └── testing-with-claude.md        # Testing guide
│
├── docker-dev-assistant/              # Project 1: Simple
│   ├── server.py                     # MCP server (401 LOC)
│   ├── README.md
│   ├── requirements.txt
│   ├── docker-compose.yml
│   └── examples/
│
├── personal-knowledge-base/           # Project 2: Intermediate
│   ├── server.py                     # MCP server (784 LOC)
│   ├── README.md
│   ├── requirements.txt
│   ├── sample-notes/                 # Demo markdown files
│   └── examples/
│
└── smart-day-planner/                 # Project 3: Advanced
    ├── server.py                     # MCP server (760 LOC)
    ├── README.md
    ├── requirements.txt
    ├── .env.example                  # API keys template
    ├── config.yaml
    └── examples/
```

---

## ❓ Common Questions

**Q: Can I use all three servers at once?**

Yes! Add all three to your Claude Desktop config:
```json
{
  "mcpServers": {
    "docker-dev-assistant": {
      "command": "python3",
      "args": ["/path/to/docker-dev-assistant/server.py"]
    },
    "personal-knowledge-base": {
      "command": "python3",
      "args": ["/path/to/personal-knowledge-base/server.py"]
    },
    "smart-day-planner": {
      "command": "python3",
      "args": ["/path/to/smart-day-planner/server.py"]
    }
  }
}
```

**Q: Do I need Docker installed?**

Only for the Docker Dev Assistant example. The other two don't require Docker.

**Q: Do I need API keys?**

Only for Smart Day Planner (weather and todos). Docker Dev Assistant and Personal Knowledge Base work without any API keys.

**Q: Can I use this with other AI assistants?**

Yes! Any MCP-compatible client can use these servers. Claude Desktop is just the easiest to get started with.

**Q: What if I get stuck?**

1. Run `python3 verify_setup.py` to check your setup
2. Read [docs/setup-guide.md](docs/setup-guide.md) for detailed instructions
3. Check [docs/testing-with-claude.md](docs/testing-with-claude.md) for debugging tips
4. Open an issue on GitHub

---

## 🤝 Contributing

Contributions are welcome! Whether it's:

- Bug fixes
- New example projects
- Documentation improvements
- Code quality enhancements

Please feel free to open an issue or submit a pull request.

---

## 📚 Resources

- [Official MCP Documentation](https://modelcontextprotocol.io)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Claude Desktop](https://claude.ai/download)
- [MCP Specification](https://spec.modelcontextprotocol.io)

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

Built with the [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk).

---

## ✅ Success Checklist

- [ ] Repository cloned
- [ ] `verify_setup.py` passes
- [ ] Dependencies installed
- [ ] Server runs without errors
- [ ] Claude Desktop configured
- [ ] Test query works
- [ ] Ready to explore!

---

**Ready to get started?** Head to [Docker Dev Assistant](docker-dev-assistant/) to build your first MCP server! 🚀
