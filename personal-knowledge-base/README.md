# Personal Knowledge Base

An AI-powered personal knowledge management system that indexes markdown notes and provides semantic search capabilities. Query your notes naturally, discover connections between ideas, and leverage vector embeddings for intelligent information retrieval.

## Overview

This intermediate MCP project builds on the Docker Dev Assistant foundation and introduces:

- **File system operations**: Reading and monitoring markdown files
- **Vector embeddings**: Using sentence-transformers for local embeddings (no API required)
- **ChromaDB integration**: Vector database for semantic search
- **Hybrid search**: Combine semantic and keyword search for best results
- **Dynamic resources**: Notes automatically exposed as readable resources
- **File watching**: Automatic re-indexing when notes change
- **Markdown parsing**: Extract frontmatter, tags, and links

## Features

### Tools

1. **semantic_search** - AI-powered semantic search
   - Finds conceptually similar content
   - Works even if exact keywords don't match
   - Returns similarity scores
   - Example: "machine learning" finds notes about "neural networks" and "AI models"

2. **search_notes** - Traditional keyword search
   - Exact substring matching
   - Case-sensitive or case-insensitive
   - Shows context around matches
   - Fast and precise for known terms

3. **get_note** - Read specific note
   - Retrieve full content by name
   - Includes metadata, tags, and links
   - Formatted for readability

4. **list_notes** - List all available notes
   - Optional tag filtering
   - Shows modification dates
   - Displays metadata

5. **get_recent_notes** - Recently modified notes
   - Sorted by modification time
   - Configurable limit
   - Quick access to recent work

6. **find_similar** - Find semantically similar notes
   - Given a note, find related notes
   - Uses vector similarity
   - Discover unexpected connections

7. **index_notes** - Manually rebuild index
   - Re-index all notes
   - Use after adding notes externally
   - Updates vector embeddings

### Resources

- Each markdown note is exposed as a resource with URI `note:///note-name`
- Resources are dynamically discovered from the file system
- Includes metadata (tags, links, modification dates)

### Prompts

1. **summarize-topic** - Comprehensive topic summary
   - Searches across all notes for a topic
   - Synthesizes information from multiple sources
   - Identifies themes and connections

2. **connect-ideas** - Find connections between concepts
   - Searches for two different concepts
   - Discovers direct and indirect connections
   - Suggests novel combinations

## Prerequisites

- **Python 3.11 or 3.12** (required - Python 3.14 not yet supported by ChromaDB dependencies)
- **MCP SDK**: `pip install mcp`
- **ChromaDB**: Vector database
- **sentence-transformers**: Local embedding model
- **Claude Desktop** or another MCP client

## Installation

1. **Create and activate a virtual environment** (if not already done):
   ```bash
   # From the repository root
   # Use Python 3.11 (ChromaDB requires 3.11 or 3.12)
   python3.11 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Navigate to this directory:**
   ```bash
   cd personal-knowledge-base
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

   This will download:
   - MCP Python SDK
   - ChromaDB
   - Sentence Transformers (includes the embedding model, ~90MB)
   - Supporting libraries

4. **Prepare your notes:**

   The server includes sample notes in `sample-notes/`. You can:
   - Use the sample notes to test
   - Point to your own notes directory (see Configuration below)
   - Create a new notes directory

5. **Test the server:**
   ```bash
   python3 server.py
   ```

   You should see:
   ```
   INFO:personal-knowledge-base:Starting Personal Knowledge Base MCP Server
   INFO:personal-knowledge-base:Loading embedding model...
   INFO:personal-knowledge-base:Indexing notes from ./sample-notes...
   INFO:personal-knowledge-base:Found 3 markdown files
   INFO:personal-knowledge-base:Indexing complete
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
       "personal-knowledge-base": {
         "command": "/absolute/path/to/python-mcp-servers/venv/bin/python3",
         "args": ["/absolute/path/to/python-mcp-servers/personal-knowledge-base/server.py"]
       }
     }
   }
   ```

   **⚠️ Important**:
   - **Must use venv Python** - The directory is named `venv` (not `.venv`)
   - Use absolute paths - No `~/` or relative paths
   - Example: `/Users/yourname/python-mcp-servers/venv/bin/python3`

3. **Optional: Custom notes directory:**

   If you want to index notes from a different location:

   ```json
   {
     "mcpServers": {
       "personal-knowledge-base": {
         "command": "/absolute/path/to/python-mcp-servers/venv/bin/python3",
         "args": ["/absolute/path/to/python-mcp-servers/personal-knowledge-base/server.py"],
         "env": {
           "NOTES_DIR": "/path/to/your/notes"
         }
       }
     }
   }
   ```

4. **Restart Claude Desktop** (fully quit and reopen)

### Organizing Your Notes

The server works best with well-structured notes:

**Use frontmatter for metadata:**
```markdown
---
title: My Note Title
tags: [python, programming, tutorial]
created: 2025-01-15
modified: 2025-02-03
---

# Content starts here
```

**Supported frontmatter fields:**
- `title`: Note title
- `tags`: List of tags (used for filtering)
- `created`: Creation date
- `modified`: Last modified date
- Any custom fields you want

**Wiki-style links:**
Use `[[note-name]]` to link between notes. The server extracts these connections.

## Usage

### Example Queries

**Semantic search:**
```
Find notes about machine learning
What do I know about async programming?
Search for information on Docker deployment
```

**Keyword search:**
```
Search for the exact phrase "Model Context Protocol"
Find notes containing "ChromaDB"
```

**Browse notes:**
```
List all my notes
Show me notes tagged with "python"
What are my recent notes?
Show me the projects note
```

**Discover connections:**
```
Find notes similar to my machine learning article
What notes are related to my Python projects?
```

**Comprehensive analysis:**
```
Summarize everything I know about vector databases
Find connections between MCP and vector embeddings
```

### Semantic vs Keyword Search

**When to use semantic search:**
- Exploring a topic broadly
- Don't know exact terminology
- Want conceptually related content
- Looking for connections

**When to use keyword search:**
- Know exact phrase or term
- Looking for specific code or syntax
- Need precise matching
- Want to find where you mentioned something specific

**Best practice:** Use semantic search first for discovery, then keyword search for precision.

## How It Works

### Vector Embeddings

The server uses the `all-MiniLM-L6-v2` model from sentence-transformers:

```python
from sentence_transformers import SentenceTransformer

# Load model (runs locally, no API needed)
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Generate embedding for text
embedding = embedding_model.encode("your text here")
```

Embeddings are 384-dimensional vectors that capture semantic meaning. Similar texts have similar embeddings (measured by cosine similarity).

### ChromaDB Integration

ChromaDB stores and indexes the embeddings:

```python
import chromadb

# Initialize client
client = chromadb.Client(Settings(persist_directory="./chroma_db"))

# Create collection
collection = client.create_collection(name="notes")

# Add documents
collection.add(
    ids=["note-1"],
    documents=["note content"],
    embeddings=[embedding],
    metadatas=[{"tags": ["python"]}]
)

# Query
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=5
)
```

Benefits:
- Fast similarity search
- Persistent storage
- Metadata filtering
- Efficient for large collections

### File System Monitoring

The server uses `watchdog` to detect file changes:

```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class NotesFileHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('.md'):
            asyncio.create_task(index_note(Path(event.src_path)))
```

When you add or modify a note, it's automatically re-indexed.

### Indexing Process

On startup and for new notes:

1. **Read markdown file**: Parse content and frontmatter
2. **Extract metadata**: Tags, links, dates
3. **Generate embedding**: Convert content to vector
4. **Store in ChromaDB**: Save embedding and metadata
5. **Update cache**: Keep in-memory cache for fast access

### Search Process

**Semantic search:**
1. Generate embedding for query
2. Find nearest neighbors in vector space
3. Return top N results with similarity scores

**Keyword search:**
1. Load notes from cache
2. Search content for substring match
3. Extract context around matches
4. Return matching notes

## Extending

### Add More Tools

**Tag management:**
```python
Tool(
    name="get_tags",
    description="List all unique tags across notes",
    inputSchema={"type": "object", "properties": {}}
)
```

**Backlinks:**
```python
Tool(
    name="get_backlinks",
    description="Find notes that link to a specific note",
    inputSchema={
        "type": "object",
        "properties": {
            "note_name": {"type": "string"}
        },
        "required": ["note_name"]
    }
)
```

**Export functionality:**
```python
Tool(
    name="export_note",
    description="Export note to different format (HTML, PDF)",
    inputSchema={
        "type": "object",
        "properties": {
            "note_name": {"type": "string"},
            "format": {"type": "string", "enum": ["html", "pdf"]}
        },
        "required": ["note_name", "format"]
    }
)
```

### Different Embedding Models

Experiment with other sentence-transformers models:

**For better quality (larger, slower):**
```python
model = SentenceTransformer('all-mpnet-base-v2')  # 768 dimensions
```

**For speed (smaller, faster):**
```python
model = SentenceTransformer('all-MiniLM-L12-v2')  # 384 dimensions
```

**Domain-specific:**
- `msmarco-distilbert-base-v4` - For Q&A and search
- `multi-qa-MiniLM-L6-cos-v1` - For question answering

### Custom Metadata

Add custom frontmatter fields and expose them:

```markdown
---
title: My Note
project: MCP Tutorial
status: in-progress
priority: high
---
```

Then filter by custom fields in tools.

### Graph Visualization

Build a note graph based on links:

```python
import networkx as nx

def build_note_graph():
    G = nx.DiGraph()
    for note_name, note_data in notes_cache.items():
        G.add_node(note_name)
        for link in note_data.get('links', []):
            if link in notes_cache:
                G.add_edge(note_name, link)
    return G
```

## Troubleshooting

### Slow First Query

The first query may be slow because:
1. Embedding model needs to load (~90MB)
2. Notes are being indexed

Subsequent queries will be fast. The embedding model stays in memory.

### "Indexing in progress" Error

Wait a few seconds after starting the server for initial indexing to complete. For large note collections (100+ notes), this may take a minute.

### Notes Not Found

1. Check `NOTES_DIR` environment variable is set correctly
2. Ensure notes are `.md` files (not `.markdown` or `.txt`)
3. Try running `index_notes` tool to manually re-index

### Inaccurate Semantic Search

Semantic search quality depends on:
- **Content quality**: More detailed notes = better results
- **Note length**: Very short notes may not embed well
- **Query specificity**: Vague queries → vague results

Tips for better results:
- Use descriptive queries (not single words)
- Write comprehensive notes with context
- Use hybrid approach: semantic + keyword search

### ChromaDB Errors

If you see ChromaDB errors:

1. Delete the `chroma_db` directory and restart (rebuilds index)
2. Check disk space (embeddings require storage)
3. Ensure write permissions for `chroma_db` directory

### File Watcher Not Detecting Changes

On some systems, file watching may be unreliable:

1. Use the `index_notes` tool to manually trigger re-indexing
2. Restart the server after adding notes
3. Check file system permissions

## Performance Tips

### For Large Note Collections (1000+ notes)

1. **Batch indexing**: Notes are already batch-indexed on startup
2. **Pagination**: Add pagination to `list_notes` tool
3. **Lazy loading**: Don't load all note content into memory
4. **Better hardware**: Embeddings benefit from more RAM

### Memory Usage

- Embedding model: ~90MB
- ChromaDB index: ~1-2KB per note
- Notes cache: Depends on note count and size

For 100 notes (~10KB each): ~2MB + 90MB model = ~92MB total

### Query Performance

- Semantic search: O(log n) with HNSW index
- Keyword search: O(n) linear scan
- For large collections, semantic search is faster


## Example Usage

Example conversations using the Personal Knowledge Base MCP server.

## Semantic Search Examples

### Finding Related Content

**User:**
```
Find notes about machine learning
```

**Claude:**
```
I'll do a semantic search for machine learning topics.

[Uses semantic_search with query="machine learning"]

Semantic search results for 'machine learning':

1. **learnings** (similarity: 0.87)
   Tags: learning, programming, til
   Preview: # Learning Notes... Python Async Best Practices... Vector Embeddings
   and Semantic Search... Key Concepts: Embeddings are numerical representations...

2. **projects** (similarity: 0.72)
   Tags: projects, work, development
   Preview: # Current Projects... MCP Tutorial Repository... Machine Learning
   Blog Series... Writing a series of blog posts about practical machine learning...

3. **ideas** (similarity: 0.68)
   Tags: ideas, brainstorming, future
   Preview: # Project Ideas... AI-Powered Code Review Assistant... Using LLM for
   code analysis and suggestions...

I found three notes related to machine learning:
- **learnings**: Contains detailed notes about vector embeddings and semantic search
- **projects**: Mentions your ML blog series and upcoming articles
- **ideas**: Includes AI-powered project concepts

Would you like me to read any of these in detail?
```

## Keyword Search Examples

### Exact Phrase Search

**User:**
```
Search for "Model Context Protocol" in my notes
```

**Claude:**
```
I'll search for that exact phrase.

[Uses search_notes with query="Model Context Protocol"]

Keyword search results for 'Model Context Protocol' (1 found):

**learnings**
Tags: learning, programming, til
Context: ...Things I've learned recently. MCP Development Insights. Server Structure
Keep it simple: 1. Initialize Model Context Protocol server 2. Define tools/resources...

Found one mention in your learnings note, in the section about MCP development.
```

## Browsing Notes

### Listing by Tag

**User:**
```
Show me notes tagged with "projects"
```

**Claude:**
```
[Uses list_notes with tag="projects"]

Found 1 note(s) with tag 'projects':

**projects**
  Tags: projects, work, development
  Modified: 2025-02-03T10:30:00

This note contains information about your current active projects.
Would you like me to read it?
```

### Recent Activity

**User:**
```
What have I been working on recently? Show my recent notes.
```

**Claude:**
```
[Uses get_recent_notes]

Recently modified notes (top 5):

**projects**
  Modified: 2025-02-03T10:30:00
  Tags: projects, work, development

**learnings**
  Modified: 2025-02-01T15:20:00
  Tags: learning, programming, til

**ideas**
  Modified: 2025-01-28T14:10:00
  Tags: ideas, brainstorming, future

Looks like you've been most active on your projects note, followed by adding
learnings and brainstorming new ideas.
```

## Discovery and Connections

### Finding Similar Notes

**User:**
```
What notes are similar to my ideas note?
```

**Claude:**
```
[Uses find_similar with note_name="ideas"]

Notes similar to 'ideas':

1. **projects** (similarity: 0.81)
   Tags: projects, work, development

2. **learnings** (similarity: 0.65)
   Tags: learning, programming, til

Your ideas note is most similar to your projects note, which makes sense - many
of your project ideas align with your current work. The learnings note also shows
similarity, suggesting your ideas are influenced by what you've been learning.
```

### Topic Summary

**User:**
```
Summarize everything I know about Python
```

**Claude:**
```
[Uses semantic_search to find Python-related notes]
[Reads relevant notes]

Based on your notes, here's what you know about Python:

**Current Projects:**
- Working with Python 3.10+ for the MCP Tutorial Repository
- Using Python for the Knowledge Base server with ChromaDB integration

**Key Learnings:**

*Async Programming:*
- When async is beneficial (I/O-bound operations)
- Common patterns (concurrent requests, timeouts, cancellation)
- Using asyncio.gather() and asyncio.wait_for()

*Type Hints:*
- Modern union syntax (int | str instead of Union[int, str])
- Generic types and TypeVar
- Protocol for structural typing

*Best Practices:*
- Using functools.lru_cache for optimization
- secrets module for security over random
- Understanding when to use multiprocessing vs async

**Technologies:**
- ChromaDB for vector databases
- Sentence transformers for embeddings
- MCP SDK for building servers
- SQLAlchemy for database work

**Areas of Interest:**
- Machine learning applications
- Vector embeddings and semantic search
- API development and async patterns
- Production deployment

Your Python knowledge spans from fundamentals to advanced topics like async
programming and ML applications.
```

## Using Prompts

### Topic Analysis

**User:**
```
Use the summarize-topic prompt for "vector embeddings"
```

**Claude:**
```
[Uses summarize-topic prompt with topic="vector embeddings"]
[Performs semantic search and reads notes]

Here's a comprehensive summary of what you know about vector embeddings:

**Core Concepts:**
- Numerical representations of text that capture semantic meaning
- Similar texts have similar embeddings (cosine similarity)
- High-dimensional vectors (typically 384-768 dimensions)

**Practical Applications:**
You're actively using vector embeddings in your Personal Knowledge Base project:
- ChromaDB for storage and querying
- Sentence-transformers for local embeddings (no API needed)
- Semantic search across markdown notes

**Technical Details:**
- Using 'all-MiniLM-L6-v2' model (384 dimensions)
- ChromaDB HNSW index for efficient similarity search
- Hybrid approach: combining semantic + keyword search

**Performance Insights:**
- Batch operations when possible
- Appropriate embedding model selection for domain
- Query performance is O(log n) with HNSW index

**Future Applications:**
Your ideas note mentions several projects that could leverage embeddings:
- AI-powered code review with semantic analysis
- Note-taking app with intelligent search
- Recipe manager with semantic recipe discovery

**Connections to Other Topics:**
- Related to your ML blog series (planning RAG article)
- Connected to MCP server development patterns
- Part of broader semantic search and AI integration work

**Gaps to Explore:**
- Fine-tuning embedding models for specific domains
- Comparing different embedding models (mpnet vs MiniLM)
- Advanced vector database features (filtering, hybrid search)
```

### Finding Connections

**User:**
```
Find connections between "MCP" and "vector databases"
```

**Claude:**
```
[Uses connect-ideas prompt]
[Searches for both concepts and reads relevant notes]

Connections between "MCP" and "vector databases":

**Direct Connection:**
Your Personal Knowledge Base project directly combines both:
- MCP server architecture for exposing tools
- ChromaDB (vector database) for semantic search
- Shows how MCP can make vector search accessible via AI

**Shared Themes:**

1. **Enabling AI Capabilities:**
   - MCP: Gives AI access to tools and data
   - Vector DBs: Provide semantic understanding to AI

2. **Semantic Understanding:**
   - MCP: Helps AI understand user intent and available tools
   - Vector DBs: Enable AI to find semantically similar content

3. **Modern AI Stack:**
   - Both are emerging technologies in AI tooling
   - Complement each other in AI applications

**Practical Applications:**

1. **Knowledge Management:**
   - MCP exposes search tools
   - Vector DB powers semantic search
   - Result: Natural language knowledge retrieval

2. **RAG Systems:**
   - Vector DB stores document embeddings
   - MCP provides retrieval tools
   - AI combines retrieval with generation

3. **Context Augmentation:**
   - MCP gives AI access to real-time data
   - Vector DBs provide relevant historical context
   - Together: comprehensive context for AI responses

**Future Possibilities:**

From your ideas note, you could combine these in:
- AI code review (vector search for similar code patterns, MCP for tool access)
- Personal finance dashboard (semantic search of transactions, MCP for API access)
- Recipe manager (semantic recipe search, MCP for external data)

**Technical Synergy:**
- Both benefit from async operations
- Both require careful error handling
- Both are optimized for AI interactions
- Both support metadata and filtering

The combination of MCP + vector databases is particularly powerful for building
intelligent, context-aware AI assistants.
```

## Advanced Queries

### Complex Analysis

**User:**
```
I'm learning about async programming. What do I already know, and what related
projects am I working on?
```

**Claude:**
```
[Uses semantic_search for "async programming"]
[Uses semantic_search for "asynchronous" and "asyncio"]
[Reads matching notes]

**What You Know About Async Programming:**

From your learnings note:

*When to Use Async:*
- I/O-bound operations (network, file I/O)
- Multiple concurrent operations
- Long-running parallelizable tasks

*When NOT to Use Async:*
- CPU-bound operations (use multiprocessing)
- Simple sequential operations
- Operations without I/O waits

*Key Patterns You've Documented:*
```python
# Concurrent requests
await asyncio.gather(*tasks)

# Timeout handling
await asyncio.wait_for(operation(), timeout=5.0)

# Task cancellation
task.cancel()
```

*Specific Insights:*
- asyncio.gather(return_exceptions=True) prevents one failure from cancelling all tasks
- Don't block the event loop
- Proper async handling is crucial for MCP servers

**Related Projects:**

1. **MCP Tutorial Repository:**
   - Building async MCP servers
   - Smart Day Planner uses async for concurrent API calls
   - Personal Knowledge Base uses async patterns

2. **Planned Blog Series:**
   - Your ML blog mentions production deployment patterns
   - Async is relevant for ML API serving

**Connections:**
Your async knowledge is directly applied in your MCP projects. The Smart Day
Planner project specifically uses async to:
- Make concurrent API calls (weather, todos, calendar)
- Handle multiple requests efficiently
- Implement proper timeout and error handling

**Suggestions:**
Based on your notes, you might want to document:
- Performance comparisons (async vs sync for your use cases)
- Real-world async debugging experiences
- Patterns you've discovered in your MCP server development
```

## Tips for Better Searches

### Be Specific with Semantic Search
```
❌ "Python"  (too broad)
✓ "Python async programming patterns"
✓ "How to use ChromaDB with Python"
```

### Use Keyword Search for Code
```
✓ "Search for 'asyncio.gather'"
✓ "Find '@server.call_tool'"
```

### Combine Searches
```
✓ "Search semantically for machine learning, then show me the exact mentions
   of 'neural network'"
```

### Leverage Prompts
```
✓ "Use the summarize-topic prompt for databases"
✓ "Find connections between Docker and Python"
```

---

**Try these yourself!** The more notes you add, the more powerful semantic search becomes.

## Next Project

Ready for production patterns? Move on to the **Smart Day Planner** to learn about:

- Async MCP servers
- External API integration
- Secrets management
- Error handling across services
- Response caching and rate limiting

[→ Go to Smart Day Planner](../smart-day-planner/)

## Additional Resources

- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Sentence Transformers](https://www.sbert.net/)
- [Vector Embeddings Explained](https://www.pinecone.io/learn/vector-embeddings/)
- [Markdown Frontmatter](https://jekyllrb.com/docs/front-matter/)

---

**Questions or issues?** Check the main [README](../README.md) or [Testing Guide](../docs/testing-with-claude.md).
