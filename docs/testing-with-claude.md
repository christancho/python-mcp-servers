# Testing with Claude Desktop

This guide covers how to test your MCP servers with Claude Desktop, debug issues, and verify that everything works correctly.

## Basic Testing Workflow

### 1. Configure the Server

Add your MCP server to Claude Desktop's configuration file as described in the [Setup Guide](setup-guide.md).

### 2. Restart Claude Desktop

**Important**: You must fully quit and restart Claude Desktop after any configuration changes. On macOS, use Cmd+Q to quit (not just close the window).

### 3. Verify Server Connection

In Claude Desktop, you can check if your server is connected:

1. Open Claude Desktop Settings
2. Look for the MCP Servers section
3. Your server should appear with a green indicator if connected

If it's not showing up or shows an error, see the Troubleshooting section below.

### 4. Test with Simple Queries

Start with basic queries that should trigger your tools:

**Docker Dev Assistant:**
```
List my Docker containers
```

**Personal Knowledge Base:**
```
What notes do I have?
```

**Smart Day Planner:**
```
What's the weather today?
```

### 5. Verify Tool Calls

Claude should indicate when it's using your tools. Look for messages like:
- "I'll check your Docker containers..."
- "Let me search your notes..."
- "I'll fetch the weather data..."

## Testing Each Project

### Docker Dev Assistant

#### Test Checklist

1. **List Containers**
   ```
   What Docker containers are running?
   ```
   Expected: List of running containers with names, images, and status

2. **Get Logs**
   ```
   Show me logs for container [container-name]
   ```
   Expected: Recent log output from the specified container

3. **Resource Usage**
   ```
   What are the resource stats for my containers?
   ```
   Expected: CPU and memory usage for running containers

4. **Read Docker Compose**
   ```
   Show me the docker-compose.yml file
   ```
   Expected: Contents of the docker-compose.yml file

5. **Debug Prompt**
   ```
   Help me debug container [container-name]
   ```
   Expected: Automated debugging workflow checking status, logs, and resources

#### Common Issues

- **"Docker is not running"**: Start Docker Desktop
- **"Container not found"**: Ensure the container name is correct (check with `docker ps`)
- **"Permission denied"**: Ensure your user has Docker access

### Personal Knowledge Base

#### Test Checklist

1. **List Notes**
   ```
   What notes do I have?
   ```
   Expected: List of all markdown files in the notes directory

2. **Semantic Search**
   ```
   Find notes about machine learning
   ```
   Expected: Semantically relevant notes, even if they use different terminology

3. **Keyword Search**
   ```
   Search for the exact phrase "python programming"
   ```
   Expected: Notes containing that exact phrase

4. **Get Specific Note**
   ```
   Show me the contents of [note-name]
   ```
   Expected: Full contents of the specified note

5. **Recent Notes**
   ```
   What are my recent notes?
   ```
   Expected: Recently modified notes with timestamps

6. **Find Similar**
   ```
   Find notes similar to my project ideas
   ```
   Expected: Notes with similar semantic content

7. **Summarize Topic**
   ```
   Summarize all my notes about Python
   ```
   Expected: Comprehensive summary combining multiple relevant notes

#### Common Issues

- **"No notes found"**: Check that notes directory exists and contains .md files
- **Slow first query**: First search builds the vector index (may take a few seconds)
- **"Vector index not ready"**: Wait a moment for indexing to complete
- **Inaccurate semantic search**: Ensure notes have meaningful content (not just titles)

### Smart Day Planner

#### Test Checklist

1. **Get Weather**
   ```
   What's the weather today?
   ```
   Expected: Current weather conditions

2. **Weather Forecast**
   ```
   What's the weather like this week?
   ```
   Expected: Weekly weather forecast

3. **List Todos**
   ```
   What's on my todo list?
   ```
   Expected: Tasks from Todoist

4. **Calendar Events**
   ```
   What's on my calendar?
   ```
   Expected: Upcoming calendar events

5. **Suggest Activities**
   ```
   Should I plan outdoor activities this weekend?
   ```
   Expected: Weather-aware activity suggestions

6. **Plan Week**
   ```
   Help me plan my week
   ```
   Expected: Intelligent weekly plan combining weather, todos, and calendar

#### Common Issues

- **"API key not found"**: Check .env file has correct keys
- **"API error"**: Verify API keys are valid and not expired
- **"Rate limit exceeded"**: Wait a few minutes (free tier limits)
- **"No calendar events"**: Check Google Calendar setup and permissions

## Debugging Techniques

### 1. Add Logging to Your Server

Add debug logging to see what's happening:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@server.call_tool()
async def my_tool(param: str):
    logger.debug(f"Tool called with param: {param}")
    # ... rest of implementation
```

### 2. Run Server Directly

Test your server outside of Claude Desktop:

```bash
python3 server.py
```

This will show any import errors, configuration issues, or startup problems.

### 3. Check Claude Desktop Logs

Claude Desktop has developer tools that show logs:

- **macOS**: Help → View Logs
- **Windows**: Help → View Logs
- Look for MCP-related errors in the console

### 4. Test with curl (Advanced)

For advanced debugging, you can test the MCP protocol directly using stdio:

```bash
echo '{"jsonrpc":"2.0","method":"tools/list","id":1}' | python3 server.py
```

### 5. Verify Dependencies

Ensure all required packages are installed:

```bash
pip list | grep mcp
pip list | grep chromadb  # for Knowledge Base
```

## Testing Best Practices

### Start Simple

Begin with the simplest tool in your server, then progress to more complex ones:

1. Test a tool that returns static data first
2. Then test tools that access external resources
3. Finally test tools that perform actions

### Test Error Cases

Don't just test the happy path:

1. **Invalid parameters**: Try calling tools with wrong arguments
2. **Missing resources**: Test when files/containers/APIs aren't available
3. **Network issues**: Test behavior when APIs are slow or unreachable
4. **Edge cases**: Empty inputs, very long inputs, special characters

### Verify Complete Responses

Check that responses include:

1. **Expected data**: The actual information requested
2. **Proper formatting**: Well-structured, readable output
3. **Error messages**: Clear explanations when things go wrong
4. **Context**: Enough information for Claude to formulate a good response

### Test Resource Access

For servers that expose resources:

1. **List resources**: Verify all expected resources appear
2. **Read resources**: Check content is accessible and correct
3. **Resource updates**: Ensure changes are reflected (for dynamic resources)

## Common Testing Scenarios

### Scenario 1: Tool Not Being Called

**Symptoms**: Claude responds without using your tool

**Possible causes**:
- Tool description isn't clear enough for Claude to understand when to use it
- Parameter types or descriptions are ambiguous
- Similar built-in functionality makes your tool redundant

**Solutions**:
- Improve tool descriptions to be more specific
- Give examples in the description
- Explicitly ask Claude to use the tool: "Use the [tool-name] tool to..."

### Scenario 2: Tool Called with Wrong Parameters

**Symptoms**: Tool receives unexpected parameter values

**Possible causes**:
- Parameter descriptions aren't clear
- Missing validation in tool implementation
- Claude misinterpreting user intent

**Solutions**:
- Add detailed parameter descriptions with examples
- Implement validation and return helpful error messages
- Use more specific parameter types

### Scenario 3: Tool Returns Error

**Symptoms**: Tool executes but returns an error

**Possible causes**:
- External dependency not available (Docker, files, APIs)
- Configuration missing (env variables, API keys)
- Permission issues

**Solutions**:
- Check prerequisites are met
- Verify configuration
- Add better error messages to guide debugging

## Performance Testing

### Response Time

MCP tools should respond quickly:

- **Simple tools**: < 1 second
- **File operations**: < 2 seconds
- **API calls**: < 5 seconds
- **Heavy processing**: Use async and show progress

### Resource Usage

Monitor your server's resource usage:

```bash
# Check Python process
ps aux | grep python
top -p [pid]
```

### Concurrent Requests

Test if your server handles multiple requests:

1. Ask Claude to perform multiple operations
2. Check for race conditions or conflicts
3. Ensure proper async handling

## Automated Testing

While Claude Desktop is great for manual testing, consider adding automated tests:

```python
# test_server.py
import pytest
from server import my_tool

@pytest.mark.asyncio
async def test_my_tool():
    result = await my_tool("test input")
    assert "expected" in result
```

Run tests before deploying changes:

```bash
pytest test_server.py
```

## Testing Checklist

Before considering your server complete:

- [ ] All tools work with valid inputs
- [ ] All tools handle invalid inputs gracefully
- [ ] All resources are accessible
- [ ] All prompts generate appropriate responses
- [ ] Error messages are clear and helpful
- [ ] Performance is acceptable
- [ ] Configuration is documented
- [ ] Common use cases are tested
- [ ] Edge cases are handled

## Getting Help

If you're stuck:

1. **Check the logs**: Both server logs and Claude Desktop logs
2. **Review documentation**: [Official MCP docs](https://modelcontextprotocol.io)
3. **Simplify**: Remove complexity until you find what works
4. **Ask the community**: GitHub issues, forums, Discord

## Next Steps

Once your server is working:

1. **Explore the code**: Read `server.py` to understand the implementation
2. **Extend functionality**: Add new tools or improve existing ones
3. **Optimize**: Improve performance and error handling
4. **Share**: Help others by documenting your experience

---

**Need help setting up?** Return to the [Setup Guide](setup-guide.md)

**Want to learn more about MCP?** Read [What is MCP?](what-is-mcp.md)
