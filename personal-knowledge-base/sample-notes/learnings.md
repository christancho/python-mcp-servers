---
title: Learning Notes
tags: [learning, programming, til]
created: 2025-01-10
modified: 2025-02-01
---

# Learning Notes

Things I've learned recently.

## Python Async Best Practices

### When to Use Async

Async is beneficial when you have:
- I/O-bound operations (network requests, file I/O)
- Multiple concurrent operations
- Long-running tasks that can be parallelized

Async is NOT helpful for:
- CPU-bound operations (use multiprocessing instead)
- Simple sequential operations
- Operations that don't wait for I/O

### Common Patterns

**Concurrent requests:**
```python
async def fetch_all(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url) for url in urls]
        return await asyncio.gather(*tasks)
```

**Timeout handling:**
```python
try:
    result = await asyncio.wait_for(slow_operation(), timeout=5.0)
except asyncio.TimeoutError:
    print("Operation timed out")
```

**Task cancellation:**
```python
task = asyncio.create_task(long_running())
# Later...
task.cancel()
try:
    await task
except asyncio.CancelledError:
    print("Task was cancelled")
```

---

## Vector Embeddings and Semantic Search

### Key Concepts

**Embeddings**: Numerical representations of text that capture semantic meaning. Similar texts have similar embeddings (measured by cosine similarity).

**Vector Databases**: Specialized databases optimized for storing and querying high-dimensional vectors. Examples: ChromaDB, Pinecone, Weaviate, Qdrant.

**Semantic Search vs Keyword Search:**
- Keyword: Exact matches, synonyms missed
- Semantic: Understands meaning, finds conceptually similar content

### ChromaDB Tips

**Collection creation:**
```python
collection = client.create_collection(
    name="my_docs",
    metadata={"description": "My document collection"}
)
```

**Adding documents:**
```python
collection.add(
    documents=["text content here"],
    metadatas=[{"source": "file.md"}],
    ids=["unique-id"]
)
```

**Querying:**
```python
results = collection.query(
    query_texts=["search query"],
    n_results=5
)
```

**Performance:**
- Batch operations when possible
- Use appropriate embedding model for domain
- Consider HNSW index for large collections

---

## MCP Development Insights

### Server Structure

Keep it simple:
1. Initialize server
2. Define tools/resources/prompts
3. Implement handlers
4. Run with stdio transport

### Tool Design

Good tools are:
- **Single-purpose**: Do one thing well
- **Well-described**: Clear name and description
- **Predictable**: Consistent input/output format
- **Error-friendly**: Return helpful error messages

### Common Pitfalls

1. **Blocking operations**: Use async properly, don't block the event loop
2. **Missing validation**: Always validate inputs
3. **Poor error messages**: Be specific about what went wrong
4. **Resource leaks**: Clean up connections, files, etc.

### Testing Strategy

1. Test tools independently first
2. Use Claude Desktop for integration testing
3. Check error cases (missing files, invalid params)
4. Verify resource cleanup

---

## Docker Multi-Stage Builds

Learned about multi-stage builds for smaller, more secure images.

### Before (Single Stage)

```dockerfile
FROM python:3.11
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

Result: Large image with build tools, cache, etc.

### After (Multi-Stage)

```dockerfile
# Build stage
FROM python:3.11 as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Runtime stage
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
CMD ["python", "app.py"]
```

Result: Much smaller image, only runtime dependencies.

### Benefits
- Smaller image size (faster pulls/pushes)
- Fewer security vulnerabilities
- Build tools not in production image
- Can cache build stage

---

## Git Rebase vs Merge

Finally understand when to use each!

### Merge
- Preserves complete history
- Shows when branches diverged and merged
- Safe for public branches
- Creates merge commits

**Use for:**
- Merging feature branches to main
- Preserving history of long-running features
- Team collaboration

### Rebase
- Creates linear history
- Rewrites commit history
- Cleaner git log
- No merge commits

**Use for:**
- Updating feature branch with latest main
- Cleaning up local commits before PR
- Maintaining linear project history

**Never rebase:**
- Public/shared branches
- After pushing to remote (unless coordinated)

### Interactive Rebase

Super useful for cleaning up commits:
```bash
git rebase -i HEAD~3
```

Can:
- Squash commits together
- Reword commit messages
- Reorder commits
- Drop unwanted commits

---

## Python Type Hints Tips

Type hints make code more maintainable and catch bugs early.

### Union Types (Python 3.10+)

```python
# Old way
from typing import Union
def process(value: Union[int, str]) -> Union[int, None]:
    ...

# New way
def process(value: int | str) -> int | None:
    ...
```

### Generic Types

```python
from typing import TypeVar, Generic

T = TypeVar('T')

class Container(Generic[T]):
    def __init__(self, value: T):
        self.value = value

    def get(self) -> T:
        return self.value
```

### Protocol (Structural Typing)

```python
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> None: ...

def render(obj: Drawable) -> None:
    obj.draw()  # Any object with draw() method works
```

---

## PostgreSQL Performance Tips

### Indexing Strategy

1. **Index foreign keys**: Almost always beneficial
2. **Composite indexes**: Order matters (most selective first)
3. **Partial indexes**: Index only rows that matter
4. **Don't over-index**: Each index slows down writes

### Query Optimization

**Use EXPLAIN ANALYZE:**
```sql
EXPLAIN ANALYZE
SELECT * FROM users WHERE email = 'test@example.com';
```

Shows:
- Execution plan
- Actual runtime
- Rows scanned vs returned
- Index usage

**Common issues:**
- Sequential scans on large tables → Add index
- High planning time → Simplify query or update stats
- Nested loops with many rows → Adjust join strategy

### Connection Pooling

Always use connection pooling in production:
- Reduces connection overhead
- Limits max connections
- Improves performance under load

Libraries: pgbouncer, SQLAlchemy pooling, psycopg2 pool

---

## Markdown Frontmatter

Learned about YAML frontmatter in markdown for metadata.

### Format

```markdown
---
title: My Note
tags: [tag1, tag2]
created: 2025-01-10
author: John Doe
---

# Content starts here
```

### Use Cases

- Blog post metadata
- Static site generators (Jekyll, Hugo)
- Note-taking apps (Obsidian)
- Documentation sites

### Parsing in Python

```python
import frontmatter

with open('note.md') as f:
    post = frontmatter.load(f)
    print(post.metadata)  # Dict of frontmatter
    print(post.content)   # Markdown content
```

---

## Rate Limiting Strategies

Important for API integrations and public services.

### Token Bucket Algorithm

- Tokens added at constant rate
- Each request consumes a token
- Bucket has max capacity
- Request fails if no tokens available

Good for: Smooth rate limiting with bursts

### Fixed Window

- Track requests in fixed time window (e.g., per minute)
- Reset counter at window boundary

Problem: Burst at window boundaries

### Sliding Window

- Track timestamps of recent requests
- Count requests in rolling window

Most accurate but more memory intensive

### Implementation Tips

- Use Redis for distributed rate limiting
- Return Retry-After header
- Different limits for different endpoints
- Consider user tiers (free vs paid)

---

## TIL (Today I Learned)

Quick one-liners:

- Python's `@functools.lru_cache` can speed up recursive functions dramatically
- `git bisect` can binary search through commits to find bugs
- Docker `HEALTHCHECK` instruction is crucial for production containers
- SQLAlchemy's `lazy="selectin"` prevents N+1 query problems
- `asyncio.gather(return_exceptions=True)` prevents one failure from cancelling all tasks
- Chrome DevTools can throttle network speed for testing
- Python's `secrets` module is better than `random` for security-sensitive code
- `jq` is incredibly powerful for parsing JSON in bash scripts
- Postgres JSONB is faster than JSON for querying
- `docker system prune -a` frees up disk space from unused images
