#!/usr/bin/env python3
"""
Personal Knowledge Base MCP Server

An intermediate MCP server demonstrating:
- File system operations and monitoring
- Vector embeddings with ChromaDB
- Semantic search vs keyword search
- Dynamic resource discovery
- Hybrid search patterns
- Markdown parsing with frontmatter

This server indexes markdown notes and provides AI-powered semantic search
alongside traditional keyword search.
"""

import asyncio
import logging
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import chromadb
import frontmatter
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from mcp.server import Server
from mcp.types import Resource, Tool, TextContent
from mcp.server.stdio import stdio_server

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("personal-knowledge-base")

# Initialize MCP server
server = Server("personal-knowledge-base")

# Global state
notes_dir: Path = Path(os.getenv("NOTES_DIR", "./sample-notes"))
chroma_client: Optional[chromadb.Client] = None
collection: Optional[chromadb.Collection] = None
embedding_model: Optional[SentenceTransformer] = None
notes_cache: dict[str, dict] = {}
indexing_complete: bool = False


class Note:
    """Represents a markdown note with metadata."""

    def __init__(self, path: Path):
        self.path = path
        self.name = path.stem
        self.content = ""
        self.metadata = {}
        self.links = []
        self.tags = []
        self.modified = datetime.fromtimestamp(path.stat().st_mtime)

        self._parse()

    def _parse(self):
        """Parse markdown file, extracting frontmatter and content."""
        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
                self.content = post.content
                self.metadata = post.metadata

                # Extract tags from frontmatter
                self.tags = self.metadata.get('tags', [])

                # Extract wiki-style links [[like this]]
                self.links = re.findall(r'\[\[(.*?)\]\]', self.content)

        except Exception as e:
            logger.error(f"Error parsing {self.path}: {e}")

    def to_dict(self) -> dict:
        """Convert note to dictionary for storage."""
        return {
            "name": self.name,
            "path": str(self.path),
            "tags": ", ".join(self.tags) if self.tags else "",  # Convert list to string
            "links": ", ".join(self.links) if self.links else "",  # Convert list to string
            "modified": self.modified.isoformat()
            # Note: metadata field removed as it may contain non-serializable types
        }


class NotesFileHandler(FileSystemEventHandler):
    """File system event handler for note changes."""

    def on_modified(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith('.md'):
            logger.info(f"Note modified: {event.src_path}")
            asyncio.create_task(index_note(Path(event.src_path)))

    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith('.md'):
            logger.info(f"Note created: {event.src_path}")
            asyncio.create_task(index_note(Path(event.src_path)))


def init_chromadb():
    """Initialize ChromaDB client and collection."""
    global chroma_client, collection, embedding_model

    # Initialize embedding model (runs locally, no API needed)
    logger.info("Loading embedding model...")
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

    # Initialize ChromaDB
    chroma_dir = Path("./chroma_db")
    chroma_dir.mkdir(exist_ok=True)

    chroma_client = chromadb.Client(Settings(
        persist_directory=str(chroma_dir),
        anonymized_telemetry=False
    ))

    # Get or create collection
    try:
        collection = chroma_client.get_collection("notes")
        logger.info("Loaded existing notes collection")
    except:
        collection = chroma_client.create_collection(
            name="notes",
            metadata={"description": "Personal notes collection"}
        )
        logger.info("Created new notes collection")


async def index_note(note_path: Path):
    """Index a single note in the vector database."""
    global collection, embedding_model, notes_cache

    try:
        note = Note(note_path)

        # Generate embedding
        embedding = embedding_model.encode(note.content).tolist()

        # Store in ChromaDB
        collection.upsert(
            ids=[note.name],
            documents=[note.content],
            embeddings=[embedding],
            metadatas=[note.to_dict()]
        )

        # Update cache
        notes_cache[note.name] = note.to_dict()

        logger.info(f"Indexed note: {note.name}")

    except Exception as e:
        logger.error(f"Error indexing note {note_path}: {e}")


async def index_all_notes():
    """Index all markdown files in the notes directory."""
    global indexing_complete

    logger.info(f"Indexing notes from {notes_dir}...")

    if not notes_dir.exists():
        logger.warning(f"Notes directory does not exist: {notes_dir}")
        notes_dir.mkdir(parents=True, exist_ok=True)
        indexing_complete = True
        return

    # Find all markdown files
    md_files = list(notes_dir.glob("**/*.md"))
    logger.info(f"Found {len(md_files)} markdown files")

    # Index each file
    for md_file in md_files:
        await index_note(md_file)

    indexing_complete = True
    logger.info("Indexing complete")


def start_file_watcher():
    """Start watching the notes directory for changes."""
    event_handler = NotesFileHandler()
    observer = Observer()
    observer.schedule(event_handler, str(notes_dir), recursive=True)
    observer.start()
    logger.info(f"Watching {notes_dir} for changes")
    return observer


# MCP Tool Handlers

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools."""
    return [
        Tool(
            name="semantic_search",
            description="AI-powered semantic search across notes using vector embeddings. Finds conceptually similar content even if exact keywords don't match.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (can be natural language)"
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of results (default: 5)",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="search_notes",
            description="Traditional keyword search across notes. Finds exact matches and substrings.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search keywords"
                    },
                    "case_sensitive": {
                        "type": "boolean",
                        "description": "Whether search is case-sensitive (default: false)",
                        "default": False
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_note",
            description="Read the full contents of a specific note by name.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Note name (without .md extension)"
                    }
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="list_notes",
            description="List all available notes with metadata (tags, modified date, etc).",
            inputSchema={
                "type": "object",
                "properties": {
                    "tag": {
                        "type": "string",
                        "description": "Optional tag filter"
                    }
                }
            }
        ),
        Tool(
            name="get_recent_notes",
            description="Get recently modified notes.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "number",
                        "description": "Number of recent notes to return (default: 5)",
                        "default": 5
                    }
                }
            }
        ),
        Tool(
            name="find_similar",
            description="Find notes semantically similar to a specific note.",
            inputSchema={
                "type": "object",
                "properties": {
                    "note_name": {
                        "type": "string",
                        "description": "Name of the note to find similar notes for"
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of similar notes (default: 5)",
                        "default": 5
                    }
                },
                "required": ["note_name"]
            }
        ),
        Tool(
            name="index_notes",
            description="Manually trigger re-indexing of all notes. Use if notes were added outside of the server.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""
    logger.info(f"Tool called: {name} with arguments: {arguments}")

    # Check if indexing is complete
    if not indexing_complete and name != "index_notes":
        return [TextContent(
            type="text",
            text="Note indexing is still in progress. Please wait a moment and try again."
        )]

    if name == "semantic_search":
        query = arguments.get("query", "")
        limit = arguments.get("limit", 5)

        if not query:
            return [TextContent(
                type="text",
                text="Error: Query is required for semantic search."
            )]

        try:
            # Generate query embedding
            query_embedding = embedding_model.encode(query).tolist()

            # Search ChromaDB
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=min(limit, len(notes_cache))
            )

            if not results['documents'] or not results['documents'][0]:
                return [TextContent(
                    type="text",
                    text=f"No results found for '{query}'."
                )]

            # Format results
            output = f"Semantic search results for '{query}':\n\n"

            for i, (doc_id, doc, metadata, distance) in enumerate(zip(
                results['ids'][0],
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            ), 1):
                similarity = 1 - distance  # Convert distance to similarity
                output += f"{i}. **{doc_id}** (similarity: {similarity:.2f})\n"

                if metadata.get('tags'):
                    output += f"   Tags: {', '.join(metadata['tags'])}\n"

                # Show preview
                preview = doc[:200] + "..." if len(doc) > 200 else doc
                output += f"   Preview: {preview}\n\n"

            return [TextContent(type="text", text=output)]

        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            return [TextContent(
                type="text",
                text=f"Error performing semantic search: {str(e)}"
            )]

    elif name == "search_notes":
        query = arguments.get("query", "")
        case_sensitive = arguments.get("case_sensitive", False)

        if not query:
            return [TextContent(
                type="text",
                text="Error: Query is required for keyword search."
            )]

        results = []

        for note_name, note_data in notes_cache.items():
            note_path = Path(note_data['path'])
            if not note_path.exists():
                continue

            note = Note(note_path)
            content = note.content

            if not case_sensitive:
                matches = query.lower() in content.lower()
            else:
                matches = query in content

            if matches:
                results.append((note_name, note_data, content))

        if not results:
            return [TextContent(
                type="text",
                text=f"No results found for '{query}'."
            )]

        output = f"Keyword search results for '{query}' ({len(results)} found):\n\n"

        for note_name, note_data, content in results:
            output += f"**{note_name}**\n"

            if note_data.get('tags'):
                output += f"Tags: {', '.join(note_data['tags'])}\n"

            # Find and show context around match
            if case_sensitive:
                idx = content.find(query)
            else:
                idx = content.lower().find(query.lower())

            if idx != -1:
                start = max(0, idx - 50)
                end = min(len(content), idx + len(query) + 50)
                context = content[start:end]
                output += f"Context: ...{context}...\n\n"

        return [TextContent(type="text", text=output)]

    elif name == "get_note":
        note_name = arguments.get("name", "")

        if not note_name:
            return [TextContent(
                type="text",
                text="Error: Note name is required."
            )]

        if note_name not in notes_cache:
            return [TextContent(
                type="text",
                text=f"Note '{note_name}' not found. Use list_notes to see available notes."
            )]

        note_path = Path(notes_cache[note_name]['path'])
        note = Note(note_path)

        output = f"# {note_name}\n\n"

        if note.metadata:
            output += "**Metadata:**\n"
            for key, value in note.metadata.items():
                output += f"- {key}: {value}\n"
            output += "\n"

        if note.tags:
            output += f"**Tags:** {', '.join(note.tags)}\n\n"

        if note.links:
            output += f"**Links:** {', '.join(note.links)}\n\n"

        output += "**Content:**\n\n"
        output += note.content

        return [TextContent(type="text", text=output)]

    elif name == "list_notes":
        tag_filter = arguments.get("tag")

        filtered_notes = notes_cache.items()

        if tag_filter:
            filtered_notes = [
                (name, data) for name, data in notes_cache.items()
                if tag_filter in data.get('tags', [])
            ]
        else:
            filtered_notes = list(notes_cache.items())

        if not filtered_notes:
            if tag_filter:
                return [TextContent(
                    type="text",
                    text=f"No notes found with tag '{tag_filter}'."
                )]
            else:
                return [TextContent(
                    type="text",
                    text="No notes found. Add markdown files to the notes directory."
                )]

        output = f"Found {len(filtered_notes)} note(s)"
        if tag_filter:
            output += f" with tag '{tag_filter}'"
        output += ":\n\n"

        for note_name, note_data in sorted(filtered_notes):
            output += f"**{note_name}**\n"

            if note_data.get('tags'):
                output += f"  Tags: {', '.join(note_data['tags'])}\n"

            if note_data.get('modified'):
                output += f"  Modified: {note_data['modified']}\n"

            output += "\n"

        return [TextContent(type="text", text=output)]

    elif name == "get_recent_notes":
        limit = arguments.get("limit", 5)

        # Sort notes by modified date
        sorted_notes = sorted(
            notes_cache.items(),
            key=lambda x: x[1].get('modified', ''),
            reverse=True
        )

        recent_notes = sorted_notes[:limit]

        if not recent_notes:
            return [TextContent(
                type="text",
                text="No notes found."
            )]

        output = f"Recently modified notes (top {len(recent_notes)}):\n\n"

        for note_name, note_data in recent_notes:
            output += f"**{note_name}**\n"

            if note_data.get('modified'):
                output += f"  Modified: {note_data['modified']}\n"

            if note_data.get('tags'):
                output += f"  Tags: {', '.join(note_data['tags'])}\n"

            output += "\n"

        return [TextContent(type="text", text=output)]

    elif name == "find_similar":
        note_name = arguments.get("note_name", "")
        limit = arguments.get("limit", 5)

        if not note_name:
            return [TextContent(
                type="text",
                text="Error: Note name is required."
            )]

        if note_name not in notes_cache:
            return [TextContent(
                type="text",
                text=f"Note '{note_name}' not found."
            )]

        try:
            # Get the note's content
            note_path = Path(notes_cache[note_name]['path'])
            note = Note(note_path)

            # Generate embedding for the note
            note_embedding = embedding_model.encode(note.content).tolist()

            # Find similar notes (excluding the note itself)
            results = collection.query(
                query_embeddings=[note_embedding],
                n_results=min(limit + 1, len(notes_cache))
            )

            # Filter out the source note
            similar_notes = []
            for doc_id, distance in zip(results['ids'][0], results['distances'][0]):
                if doc_id != note_name:
                    similar_notes.append((doc_id, distance))

            similar_notes = similar_notes[:limit]

            if not similar_notes:
                return [TextContent(
                    type="text",
                    text=f"No similar notes found for '{note_name}'."
                )]

            output = f"Notes similar to '{note_name}':\n\n"

            for i, (doc_id, distance) in enumerate(similar_notes, 1):
                similarity = 1 - distance
                note_data = notes_cache.get(doc_id, {})

                output += f"{i}. **{doc_id}** (similarity: {similarity:.2f})\n"

                if note_data.get('tags'):
                    output += f"   Tags: {', '.join(note_data['tags'])}\n"

                output += "\n"

            return [TextContent(type="text", text=output)]

        except Exception as e:
            logger.error(f"Error finding similar notes: {e}")
            return [TextContent(
                type="text",
                text=f"Error finding similar notes: {str(e)}"
            )]

    elif name == "index_notes":
        await index_all_notes()
        return [TextContent(
            type="text",
            text=f"Re-indexed {len(notes_cache)} notes successfully."
        )]

    else:
        return [TextContent(
            type="text",
            text=f"Unknown tool: {name}"
        )]


# MCP Resource Handlers

@server.list_resources()
async def list_resources() -> list[Resource]:
    """List all notes as resources."""
    resources = []

    for note_name, note_data in notes_cache.items():
        resources.append(Resource(
            uri=f"note:///{note_name}",
            name=note_name,
            mimeType="text/markdown",
            description=f"Note: {note_name}"
        ))

    return resources


@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read a note resource by URI."""
    if uri.startswith("note:///"):
        note_name = uri[8:]  # Remove "note:///" prefix

        if note_name not in notes_cache:
            raise ValueError(f"Note not found: {note_name}")

        note_path = Path(notes_cache[note_name]['path'])
        return note_path.read_text()

    raise ValueError(f"Unsupported URI scheme: {uri}")


# MCP Prompt Handlers

@server.list_prompts()
async def list_prompts() -> list[dict]:
    """List available prompt templates."""
    return [
        {
            "name": "summarize-topic",
            "description": "Summarize all notes related to a specific topic",
            "arguments": [
                {
                    "name": "topic",
                    "description": "Topic to summarize",
                    "required": True
                }
            ]
        },
        {
            "name": "connect-ideas",
            "description": "Find connections between concepts across notes",
            "arguments": [
                {
                    "name": "concept1",
                    "description": "First concept",
                    "required": True
                },
                {
                    "name": "concept2",
                    "description": "Second concept",
                    "required": True
                }
            ]
        }
    ]


@server.get_prompt()
async def get_prompt(name: str, arguments: dict) -> list[Any]:
    """Get a prompt template."""
    if name == "summarize-topic":
        topic = arguments.get("topic", "")

        prompt_text = f"""Please help me understand everything I know about {topic}.

Steps:
1. Use semantic_search to find all notes related to "{topic}"
2. Read the relevant notes using get_note
3. Provide a comprehensive summary that:
   - Identifies key themes and concepts
   - Notes any projects or applications
   - Highlights important learnings or insights
   - Suggests connections between different notes
   - Points out any gaps or areas to explore further

Focus on synthesizing the information across multiple notes rather than
summarizing each note individually.
"""

        return [{
            "role": "user",
            "content": {"type": "text", "text": prompt_text}
        }]

    elif name == "connect-ideas":
        concept1 = arguments.get("concept1", "")
        concept2 = arguments.get("concept2", "")

        prompt_text = f"""Help me find connections between "{concept1}" and "{concept2}" in my notes.

Steps:
1. Use semantic_search to find notes about "{concept1}"
2. Use semantic_search to find notes about "{concept2}"
3. Read relevant notes that mention either or both concepts
4. Analyze and explain:
   - Direct connections (notes that mention both)
   - Indirect connections (shared themes, complementary ideas)
   - Potential applications combining both concepts
   - Gaps where these ideas could be connected but aren't yet

Be creative in finding non-obvious connections!
"""

        return [{
            "role": "user",
            "content": {"type": "text", "text": prompt_text}
        }]

    raise ValueError(f"Unknown prompt: {name}")


async def main():
    """Main entry point."""
    logger.info("Starting Personal Knowledge Base MCP Server")
    logger.info(f"Notes directory: {notes_dir.absolute()}")

    # Initialize ChromaDB and embedding model
    init_chromadb()

    # Index all notes
    await index_all_notes()

    # Start file watcher
    observer = start_file_watcher()

    try:
        # Run the MCP server
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )
    finally:
        observer.stop()
        observer.join()


if __name__ == "__main__":
    asyncio.run(main())
