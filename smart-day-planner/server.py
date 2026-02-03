#!/usr/bin/env python3
"""
Smart Day Planner MCP Server

An advanced MCP server demonstrating production patterns:
- Async operations for concurrent API calls
- External API integration (OpenWeatherMap, Todoist)
- Secrets management with environment variables
- Configuration management with YAML
- Error handling across services
- Response caching with expiration
- Rate limiting awareness
- Graceful degradation when APIs fail

This server helps plan your day by combining weather data, todos, and calendar events.
"""

import asyncio
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

import aiohttp
import yaml
from dotenv import load_dotenv

from mcp.server import Server
from mcp.types import Resource, Tool, TextContent
from mcp.server.stdio import stdio_server

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("smart-day-planner")

# Initialize MCP server
server = Server("smart-day-planner")

# Load configuration
config_path = Path(__file__).parent / "config.yaml"
with open(config_path) as f:
    config = yaml.safe_load(f)

# API credentials
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
TODOIST_API_TOKEN = os.getenv("TODOIST_API_TOKEN")
DEFAULT_LOCATION = os.getenv("DEFAULT_LOCATION", "San Francisco")

# Cache for API responses
cache: dict[str, tuple[Any, datetime]] = {}


def get_from_cache(key: str) -> Optional[Any]:
    """Get value from cache if not expired."""
    if key not in cache:
        return None

    value, timestamp = cache[key]
    expiration = config.get("cache", {}).get("expiration_seconds", 300)

    if datetime.now() - timestamp > timedelta(seconds=expiration):
        del cache[key]
        return None

    return value


def set_cache(key: str, value: Any):
    """Set value in cache with current timestamp."""
    max_entries = config.get("cache", {}).get("max_entries", 100)

    # Simple cache eviction: remove oldest if at capacity
    if len(cache) >= max_entries:
        oldest_key = min(cache.keys(), key=lambda k: cache[k][1])
        del cache[oldest_key]

    cache[key] = (value, datetime.now())


async def fetch_with_retry(
    session: aiohttp.ClientSession,
    url: str,
    headers: Optional[dict] = None,
    max_retries: int = 3
) -> Optional[dict]:
    """
    Fetch URL with exponential backoff retry logic.

    Args:
        session: aiohttp ClientSession
        url: URL to fetch
        headers: Optional headers
        max_retries: Maximum number of retry attempts

    Returns:
        JSON response or None if all retries fail
    """
    for attempt in range(max_retries):
        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 429:  # Rate limited
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(f"Rate limited, waiting {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"HTTP {response.status}: {await response.text()}")
                    return None
        except asyncio.TimeoutError:
            logger.warning(f"Timeout on attempt {attempt + 1}/{max_retries}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    return None


async def get_weather(location: str = DEFAULT_LOCATION) -> Optional[dict]:
    """
    Fetch current weather data from OpenWeatherMap.

    Args:
        location: City name or coordinates

    Returns:
        Weather data dict or None if fetch fails
    """
    if not OPENWEATHER_API_KEY:
        logger.error("OpenWeatherMap API key not configured")
        return None

    # Check cache
    cache_key = f"weather:{location}"
    cached = get_from_cache(cache_key)
    if cached:
        logger.info(f"Weather data for {location} from cache")
        return cached

    base_url = config["apis"]["openweather"]["base_url"]
    url = f"{base_url}/weather?q={location}&appid={OPENWEATHER_API_KEY}&units=metric"

    timeout = aiohttp.ClientTimeout(total=config["apis"]["openweather"]["timeout"])

    async with aiohttp.ClientSession(timeout=timeout) as session:
        data = await fetch_with_retry(
            session,
            url,
            max_retries=config["apis"]["openweather"]["retry_attempts"]
        )

        if data:
            set_cache(cache_key, data)

        return data


async def get_weather_forecast(
    location: str = DEFAULT_LOCATION,
    days: int = 7
) -> Optional[dict]:
    """
    Fetch weather forecast from OpenWeatherMap.

    Args:
        location: City name or coordinates
        days: Number of days to forecast (max 7 for free tier)

    Returns:
        Forecast data dict or None if fetch fails
    """
    if not OPENWEATHER_API_KEY:
        logger.error("OpenWeatherMap API key not configured")
        return None

    # Check cache
    cache_key = f"forecast:{location}:{days}"
    cached = get_from_cache(cache_key)
    if cached:
        logger.info(f"Forecast data for {location} from cache")
        return cached

    base_url = config["apis"]["openweather"]["base_url"]
    url = f"{base_url}/forecast?q={location}&appid={OPENWEATHER_API_KEY}&units=metric&cnt={days * 8}"

    timeout = aiohttp.ClientTimeout(total=config["apis"]["openweather"]["timeout"])

    async with aiohttp.ClientSession(timeout=timeout) as session:
        data = await fetch_with_retry(
            session,
            url,
            max_retries=config["apis"]["openweather"]["retry_attempts"]
        )

        if data:
            set_cache(cache_key, data)

        return data


async def get_todos() -> Optional[list[dict]]:
    """
    Fetch tasks from Todoist.

    Returns:
        List of task dicts or None if fetch fails
    """
    if not TODOIST_API_TOKEN:
        logger.error("Todoist API token not configured")
        return None

    # Check cache
    cache_key = "todos:all"
    cached = get_from_cache(cache_key)
    if cached:
        logger.info("Todo data from cache")
        return cached

    base_url = config["apis"]["todoist"]["base_url"]
    url = f"{base_url}/tasks"

    headers = {"Authorization": f"Bearer {TODOIST_API_TOKEN}"}
    timeout = aiohttp.ClientTimeout(total=config["apis"]["todoist"]["timeout"])

    async with aiohttp.ClientSession(timeout=timeout) as session:
        data = await fetch_with_retry(
            session,
            url,
            headers=headers,
            max_retries=config["apis"]["todoist"]["retry_attempts"]
        )

        if data:
            set_cache(cache_key, data)

        return data


def format_weather(weather_data: dict) -> str:
    """Format weather data for display."""
    if not weather_data:
        return "Weather data unavailable"

    try:
        location = weather_data.get("name", "Unknown")
        temp = weather_data["main"]["temp"]
        feels_like = weather_data["main"]["feels_like"]
        description = weather_data["weather"][0]["description"]
        humidity = weather_data["main"]["humidity"]
        wind_speed = weather_data["wind"]["speed"]

        output = f"**Weather in {location}:**\n\n"
        output += f"- Temperature: {temp}°C (feels like {feels_like}°C)\n"
        output += f"- Conditions: {description.capitalize()}\n"
        output += f"- Humidity: {humidity}%\n"
        output += f"- Wind Speed: {wind_speed} m/s\n"

        return output
    except KeyError as e:
        logger.error(f"Error parsing weather data: {e}")
        return "Error formatting weather data"


def format_forecast(forecast_data: dict) -> str:
    """Format forecast data for display."""
    if not forecast_data:
        return "Forecast data unavailable"

    try:
        output = "**Weather Forecast:**\n\n"

        # Group by day
        daily_forecasts = {}
        for item in forecast_data.get("list", [])[:24]:  # Next 3 days (8 items per day)
            dt = datetime.fromtimestamp(item["dt"])
            date_key = dt.strftime("%Y-%m-%d")

            if date_key not in daily_forecasts:
                daily_forecasts[date_key] = {
                    "temps": [],
                    "descriptions": [],
                    "day": dt.strftime("%A")
                }

            daily_forecasts[date_key]["temps"].append(item["main"]["temp"])
            daily_forecasts[date_key]["descriptions"].append(
                item["weather"][0]["description"]
            )

        # Format each day
        for date_key, data in list(daily_forecasts.items())[:3]:
            avg_temp = sum(data["temps"]) / len(data["temps"])
            max_temp = max(data["temps"])
            min_temp = min(data["temps"])
            # Most common description
            description = max(set(data["descriptions"]), key=data["descriptions"].count)

            output += f"**{data['day']} ({date_key}):**\n"
            output += f"  Avg: {avg_temp:.1f}°C | High: {max_temp:.1f}°C | Low: {min_temp:.1f}°C\n"
            output += f"  Conditions: {description.capitalize()}\n\n"

        return output
    except Exception as e:
        logger.error(f"Error formatting forecast: {e}")
        return "Error formatting forecast data"


def format_todos(todos: list[dict]) -> str:
    """Format todos for display."""
    if not todos:
        return "No todos found or Todoist unavailable"

    output = f"**Your Tasks ({len(todos)} total):**\n\n"

    # Group by priority
    priority_map = {4: "P1 (Urgent)", 3: "P2 (High)", 2: "P3 (Medium)", 1: "P4 (Low)"}

    for priority in [4, 3, 2, 1]:
        priority_todos = [t for t in todos if t.get("priority") == priority]

        if priority_todos:
            output += f"**{priority_map[priority]}:**\n"
            for todo in priority_todos[:5]:  # Limit to 5 per priority
                content = todo.get("content", "Untitled")
                due = todo.get("due")
                due_str = f" (Due: {due['string']})" if due else ""
                output += f"  - {content}{due_str}\n"
            output += "\n"

    # Show total if truncated
    if len(todos) > 20:
        output += f"\n... and {len(todos) - 20} more tasks\n"

    return output


# MCP Tool Handlers

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools."""
    return [
        Tool(
            name="get_weather",
            description="Get current weather conditions for a location using OpenWeatherMap API.",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": f"City name or coordinates (default: {DEFAULT_LOCATION})"
                    }
                }
            }
        ),
        Tool(
            name="get_forecast",
            description="Get weather forecast for the next few days.",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": f"City name (default: {DEFAULT_LOCATION})"
                    },
                    "days": {
                        "type": "number",
                        "description": "Number of days to forecast (1-7, default: 3)",
                        "default": 3
                    }
                }
            }
        ),
        Tool(
            name="list_todos",
            description="Get all tasks from Todoist, organized by priority.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="analyze_week",
            description="Comprehensive weekly analysis combining weather forecast and todos.",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": f"Location for weather (default: {DEFAULT_LOCATION})"
                    }
                }
            }
        ),
        Tool(
            name="suggest_activities",
            description="Suggest activities based on weather conditions and available time.",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": f"Location for weather (default: {DEFAULT_LOCATION})"
                    }
                }
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""
    logger.info(f"Tool called: {name} with arguments: {arguments}")

    if name == "get_weather":
        location = arguments.get("location", DEFAULT_LOCATION)

        if not OPENWEATHER_API_KEY:
            return [TextContent(
                type="text",
                text="Error: OpenWeatherMap API key not configured. Please set OPENWEATHER_API_KEY in .env file."
            )]

        weather_data = await get_weather(location)

        if not weather_data:
            return [TextContent(
                type="text",
                text=f"Failed to fetch weather data for {location}. Please check the location name and try again."
            )]

        return [TextContent(
            type="text",
            text=format_weather(weather_data)
        )]

    elif name == "get_forecast":
        location = arguments.get("location", DEFAULT_LOCATION)
        days = min(int(arguments.get("days", 3)), 7)

        if not OPENWEATHER_API_KEY:
            return [TextContent(
                type="text",
                text="Error: OpenWeatherMap API key not configured."
            )]

        forecast_data = await get_weather_forecast(location, days)

        if not forecast_data:
            return [TextContent(
                type="text",
                text=f"Failed to fetch forecast for {location}."
            )]

        return [TextContent(
            type="text",
            text=format_forecast(forecast_data)
        )]

    elif name == "list_todos":
        if not TODOIST_API_TOKEN:
            return [TextContent(
                type="text",
                text="Error: Todoist API token not configured. Please set TODOIST_API_TOKEN in .env file."
            )]

        todos = await get_todos()

        if todos is None:
            return [TextContent(
                type="text",
                text="Failed to fetch todos from Todoist. Please check your API token."
            )]

        return [TextContent(
            type="text",
            text=format_todos(todos)
        )]

    elif name == "analyze_week":
        location = arguments.get("location", DEFAULT_LOCATION)

        # Fetch data concurrently
        weather_task = get_weather(location)
        forecast_task = get_weather_forecast(location, 7)
        todos_task = get_todos()

        # Use gather to run concurrently, with return_exceptions to handle failures
        results = await asyncio.gather(
            weather_task,
            forecast_task,
            todos_task,
            return_exceptions=True
        )

        current_weather, forecast, todos = results

        # Build comprehensive report
        output = "# Weekly Planning Report\n\n"

        # Current weather
        if isinstance(current_weather, dict):
            output += format_weather(current_weather) + "\n"
        else:
            output += "⚠️ Current weather unavailable\n\n"

        # Forecast
        if isinstance(forecast, dict):
            output += format_forecast(forecast) + "\n"
        else:
            output += "⚠️ Weather forecast unavailable\n\n"

        # Todos
        if isinstance(todos, list):
            output += format_todos(todos) + "\n"
        else:
            output += "⚠️ Todo list unavailable\n\n"

        # Analysis
        output += "## Weekly Planning Insights:\n\n"

        if isinstance(forecast, dict) and isinstance(todos, list):
            output += "Based on your weather forecast and task list:\n\n"

            # Check for urgent tasks
            urgent_tasks = [t for t in todos if t.get("priority") == 4]
            if urgent_tasks:
                output += f"- You have {len(urgent_tasks)} urgent tasks this week\n"

            # Check for good weather days
            output += "- Check the forecast for good weather days to plan outdoor activities\n"
            output += "- Consider scheduling indoor tasks on rainy or cold days\n"
        else:
            output += "Unable to provide insights due to missing data.\n"

        return [TextContent(type="text", text=output)]

    elif name == "suggest_activities":
        location = arguments.get("location", DEFAULT_LOCATION)

        # Get current weather
        weather_data = await get_weather(location)

        if not weather_data:
            return [TextContent(
                type="text",
                text="Unable to suggest activities without weather data."
            )]

        # Parse weather conditions
        temp = weather_data["main"]["temp"]
        description = weather_data["weather"][0]["main"].lower()

        output = f"**Activity Suggestions for {location}:**\n\n"
        output += format_weather(weather_data) + "\n"

        # Suggest based on conditions
        if "rain" in description:
            output += "**Indoor Activities Recommended:**\n"
            output += "- Work on indoor projects\n"
            output += "- Good day for focused work or reading\n"
            output += "- Visit museums or indoor venues\n"
            output += "- Catch up on indoor chores\n"
        elif temp > 25:
            output += "**Great Weather for Outdoor Activities:**\n"
            output += "- Go for a hike or bike ride\n"
            output += "- Visit the park or beach\n"
            output += "- Outdoor sports or exercise\n"
            output += "- Al fresco dining\n"
        elif temp < 10:
            output += "**Cold Weather Activities:**\n"
            output += "- Quick outdoor exercise (dress warm!)\n"
            output += "- Mostly indoor day recommended\n"
            output += "- Hot beverages and cozy activities\n"
            output += "- Good for gym or indoor exercise\n"
        else:
            output += "**Moderate Weather - Many Options:**\n"
            output += "- Great for walking or light outdoor activities\n"
            output += "- Mix of indoor and outdoor tasks\n"
            output += "- Comfortable for errands and meetings\n"
            output += "- Good day for varied activities\n"

        return [TextContent(type="text", text=output)]

    else:
        return [TextContent(
            type="text",
            text=f"Unknown tool: {name}"
        )]


# MCP Resource Handlers

@server.list_resources()
async def list_resources() -> list[Resource]:
    """List available resources."""
    return [
        Resource(
            uri="config://api-status",
            name="API Status",
            mimeType="text/plain",
            description="Status of configured APIs"
        ),
        Resource(
            uri="config://settings",
            name="Configuration Settings",
            mimeType="text/yaml",
            description="Current configuration"
        )
    ]


@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read a resource by URI."""
    if uri == "config://api-status":
        status = "# API Configuration Status\n\n"

        status += "**OpenWeatherMap:**\n"
        if OPENWEATHER_API_KEY:
            status += "  ✓ API key configured\n"
        else:
            status += "  ✗ API key not configured\n"

        status += "\n**Todoist:**\n"
        if TODOIST_API_TOKEN:
            status += "  ✓ API token configured\n"
        else:
            status += "  ✗ API token not configured\n"

        status += f"\n**Default Location:** {DEFAULT_LOCATION}\n"

        status += f"\n**Cache Status:**\n"
        status += f"  Entries: {len(cache)}\n"
        status += f"  Enabled: {config.get('cache', {}).get('enabled', False)}\n"

        return status

    elif uri == "config://settings":
        return yaml.dump(config, default_flow_style=False)

    raise ValueError(f"Unknown resource URI: {uri}")


# MCP Prompt Handlers

@server.list_prompts()
async def list_prompts() -> list[dict]:
    """List available prompt templates."""
    return [
        {
            "name": "plan-week",
            "description": "Create an intelligent weekly plan based on weather and tasks",
            "arguments": [
                {
                    "name": "location",
                    "description": "Location for weather data",
                    "required": False
                }
            ]
        },
        {
            "name": "outdoor-activities",
            "description": "Plan outdoor activities based on weather forecast",
            "arguments": [
                {
                    "name": "location",
                    "description": "Location for weather data",
                    "required": False
                }
            ]
        }
    ]


@server.get_prompt()
async def get_prompt(name: str, arguments: dict) -> list[Any]:
    """Get a prompt template."""
    if name == "plan-week":
        location = arguments.get("location", DEFAULT_LOCATION)

        prompt_text = f"""Help me plan my week effectively.

Please:
1. Use analyze_week to get comprehensive weekly data (weather + tasks) for {location}
2. Based on the information:
   - Identify the best days for outdoor activities
   - Suggest when to tackle high-priority tasks
   - Recommend indoor vs outdoor task scheduling
   - Note any weather concerns to plan around
3. Create a day-by-day suggested schedule
4. Prioritize urgent tasks while optimizing for weather conditions

Focus on practical, actionable planning advice.
"""

        return [{
            "role": "user",
            "content": {"type": "text", "text": prompt_text}
        }]

    elif name == "outdoor-activities":
        location = arguments.get("location", DEFAULT_LOCATION)

        prompt_text = f"""Help me plan outdoor activities this week.

Please:
1. Get the weather forecast for {location}
2. Use suggest_activities for current conditions
3. Analyze the forecast and identify:
   - Best days for outdoor activities
   - Times to avoid (rain, extreme temperatures)
   - Types of activities suitable for each day's conditions
4. Suggest specific outdoor activities for good weather days

Consider temperature, precipitation, and wind conditions.
"""

        return [{
            "role": "user",
            "content": {"type": "text", "text": prompt_text}
        }]

    raise ValueError(f"Unknown prompt: {name}")


async def main():
    """Main entry point."""
    logger.info("Starting Smart Day Planner MCP Server")

    # Check API configuration
    if not OPENWEATHER_API_KEY:
        logger.warning("OpenWeatherMap API key not configured")
    if not TODOIST_API_TOKEN:
        logger.warning("Todoist API token not configured")

    if not OPENWEATHER_API_KEY and not TODOIST_API_TOKEN:
        logger.error("No APIs configured! Please set up API keys in .env file")

    logger.info(f"Default location: {DEFAULT_LOCATION}")
    logger.info(f"Cache enabled: {config.get('cache', {}).get('enabled', False)}")

    # Run the MCP server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
