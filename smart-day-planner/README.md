# Smart Day Planner

An advanced MCP server that intelligently plans your day by combining real-time weather data, task management, and calendar events. Demonstrates production-ready patterns including async operations, external API integration, error handling, and response caching.

## Overview

This advanced project showcases production MCP patterns:

- **Async operations**: Concurrent API calls using `aiohttp` and `asyncio.gather()`
- **External APIs**: OpenWeatherMap (weather), Todoist (tasks)
- **Secrets management**: Environment variables with `.env` files
- **Configuration**: YAML-based configuration management
- **Error handling**: Graceful degradation when APIs fail
- **Caching**: Response caching with TTL to reduce API calls
- **Rate limiting**: Retry logic with exponential backoff
- **Production patterns**: Logging, timeouts, connection pooling

## Features

### Tools

1. **get_weather** - Current weather conditions
   - Real-time weather data via OpenWeatherMap
   - Temperature, conditions, humidity, wind
   - Cached responses (5-minute TTL)

2. **get_forecast** - Weather forecast
   - 3-7 day forecast
   - Daily high/low temperatures
   - Expected conditions per day

3. **list_todos** - Task management
   - Fetch tasks from Todoist
   - Organized by priority (P1-P4)
   - Shows due dates

4. **analyze_week** - Comprehensive weekly analysis
   - Combines weather forecast and task list
   - Concurrent API calls for speed
   - Provides actionable insights
   - Handles partial failures gracefully

5. **suggest_activities** - Weather-aware suggestions
   - Indoor/outdoor activity recommendations
   - Based on current weather conditions
   - Temperature and precipitation considerations

### Resources

- **API Status**: Shows which APIs are configured
- **Configuration**: Current settings and feature flags

### Prompts

1. **plan-week** - Intelligent weekly planning
   - Optimizes tasks around weather
   - Prioritizes urgent items
   - Suggests best days for different activities

2. **outdoor-activities** - Plan outdoor time
   - Identifies best weather windows
   - Suggests specific outdoor activities
   - Warns about unfavorable conditions

## Prerequisites

- **Python 3.10+**
- **MCP SDK**
- **API Keys** (free tiers available):
  - OpenWeatherMap API key
  - Todoist API token

## Installation

### 1. Install Dependencies

```bash
cd smart-day-planner
pip install -r requirements.txt
```

### 2. Get API Keys

**OpenWeatherMap (Free):**
1. Go to [https://openweathermap.org/api](https://openweathermap.org/api)
2. Sign up for a free account
3. Navigate to API keys section
4. Copy your API key
5. Free tier: 1,000 calls/day, 60 calls/minute

**Todoist (Free):**
1. Go to [https://todoist.com](https://todoist.com)
2. Sign up or log in
3. Go to Settings → Integrations
4. Find "API token" and copy it
5. Free tier: Generous limits for personal use

### 3. Configure Environment Variables

Copy the example file and add your keys:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```bash
OPENWEATHER_API_KEY=your_actual_api_key_here
TODOIST_API_TOKEN=your_actual_token_here
DEFAULT_LOCATION=Your City Name
```

**Security Note:** Never commit `.env` to version control! It's in `.gitignore` by default.

### 4. Test the Server

```bash
python3 server.py
```

You should see:
```
INFO:smart-day-planner:Starting Smart Day Planner MCP Server
INFO:smart-day-planner:Default location: Your City
INFO:smart-day-planner:Cache enabled: True
```

## Configuration

### Claude Desktop Setup

1. **Edit Claude Desktop config:**

   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

2. **Add server configuration:**

   ```json
   {
     "mcpServers": {
       "smart-day-planner": {
         "command": "python3",
         "args": ["/absolute/path/to/smart-day-planner/server.py"],
         "env": {
           "OPENWEATHER_API_KEY": "your_key_here",
           "TODOIST_API_TOKEN": "your_token_here",
           "DEFAULT_LOCATION": "San Francisco"
         }
       }
     }
   }
   ```

   **Alternative:** Environment variables can also be loaded from `.env` file.

3. **Restart Claude Desktop**

### Configuration File

Edit `config.yaml` to customize:

```yaml
# API timeouts and retries
apis:
  openweather:
    timeout: 10
    retry_attempts: 3

# Cache settings
cache:
  enabled: true
  expiration_seconds: 300

# Feature flags
features:
  weather: true
  todos: true
```

## Usage

### Example Queries

**Current weather:**
```
What's the weather like today?
How's the weather in New York?
```

**Forecast:**
```
What's the weather forecast for this week?
Will it rain tomorrow?
```

**Tasks:**
```
What's on my todo list?
Show me my urgent tasks
```

**Weekly planning:**
```
Help me plan my week
Analyze my week and suggest a schedule
```

**Activity planning:**
```
Should I plan outdoor activities this weekend?
What activities would you suggest for today's weather?
```

**Using prompts:**
```
Use the plan-week prompt for San Francisco
Help me plan outdoor activities this week
```

## How It Works

### Async Operations

The server uses Python's `asyncio` for concurrent operations:

```python
# Fetch multiple APIs concurrently
results = await asyncio.gather(
    get_weather(location),
    get_forecast(location, 7),
    get_todos(),
    return_exceptions=True  # Don't fail if one API fails
)
```

Benefits:
- Faster response times (parallel vs sequential)
- Better resource utilization
- Handles timeouts independently

### API Integration with Retry Logic

All API calls include retry logic with exponential backoff:

```python
async def fetch_with_retry(session, url, max_retries=3):
    for attempt in range(max_retries):
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 429:  # Rate limited
                    wait_time = 2 ** attempt
                    await asyncio.sleep(wait_time)
        except asyncio.TimeoutError:
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
```

### Response Caching

Responses are cached to reduce API calls:

```python
cache: dict[str, tuple[Any, datetime]] = {}

def get_from_cache(key: str) -> Optional[Any]:
    if key in cache:
        value, timestamp = cache[key]
        if datetime.now() - timestamp < expiration:
            return value
    return None
```

Cache benefits:
- Reduced API costs
- Faster responses
- Less rate limiting
- Works offline (cached data)

### Error Handling

The server gracefully handles failures:

1. **Missing API keys**: Clear error messages
2. **Network timeouts**: Retry with backoff
3. **Rate limiting**: Exponential backoff
4. **Partial failures**: Continue with available data
5. **Invalid responses**: Log and return safe defaults

### Secrets Management

API keys are managed securely:

1. **Never hard-coded**: Always from environment
2. **`.env` file**: Gitignored by default
3. **Environment variables**: Loaded at startup
4. **No logs**: API keys never logged

## Extending

### Add Google Calendar Integration

The server is structured to easily add calendar support:

```python
async def get_calendar_events(days: int = 7) -> Optional[list[dict]]:
    # Implementation using Google Calendar API
    ...

Tool(
    name="get_calendar",
    description="Get upcoming calendar events",
    inputSchema={...}
)
```

### Additional API Integrations

Follow the same pattern for other APIs:

1. Add API credentials to `.env.example`
2. Create async fetch function with retry logic
3. Add caching
4. Define MCP tool
5. Add to `analyze_week` for comprehensive view

### Custom Activity Rules

Enhance activity suggestions:

```python
def suggest_activities(weather_data: dict, preferences: dict) -> list[str]:
    suggestions = []

    temp = weather_data["main"]["temp"]
    conditions = weather_data["weather"][0]["main"]

    # Custom rules based on preferences
    if preferences.get("likes_hiking") and temp > 15 and "Clear" in conditions:
        suggestions.append("Great day for a hike!")

    return suggestions
```

## Troubleshooting

### "API key not configured"

1. Check `.env` file exists in `smart-day-planner/` directory
2. Verify API key is correct (no extra spaces or quotes)
3. Restart the server after adding keys

### "Failed to fetch weather data"

1. **Check API key**: Test at [openweathermap.org/api](https://openweathermap.org/api)
2. **Check location**: Try different format ("London,UK" vs "London")
3. **Check network**: Ensure internet connectivity
4. **Check rate limits**: Free tier is 60 calls/minute

### "Failed to fetch todos"

1. **Check token**: Go to Todoist Settings → Integrations
2. **Regenerate token** if needed
3. **Check permissions**: Token must have read access

### Slow responses

1. **First call is slower**: API requests and caching overhead
2. **Subsequent calls faster**: Cache hits
3. **Adjust cache expiration**: Edit `config.yaml`
4. **Check network**: Slow internet affects API calls

### Rate limiting errors

1. **Wait a minute**: Most rate limits reset quickly
2. **Check free tier limits**: Ensure not exceeded
3. **Increase retry delay**: Edit `config.yaml`
4. **Use caching**: Reduces API calls significantly

## Production Considerations

### Monitoring

Add monitoring for production use:

```python
# Track API call success rates
metrics = {
    "weather_calls": 0,
    "weather_failures": 0,
    "cache_hits": 0
}
```

### Logging

Enhanced logging for debugging:

```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('planner.log'),
        logging.StreamHandler()
    ]
)
```

### Health Checks

Add health check endpoint:

```python
Tool(
    name="health_check",
    description="Check API connectivity and server health",
    inputSchema={"type": "object", "properties": {}}
)
```

### Security

1. **Rotate API keys regularly**
2. **Use separate keys for dev/prod**
3. **Monitor for unusual activity**
4. **Set up API usage alerts**
5. **Review API permissions**

## API Cost Management

### Free Tier Limits

**OpenWeatherMap:**
- 1,000 calls/day
- 60 calls/minute
- Current weather + 5-day forecast

**Todoist:**
- Generous limits for personal use
- Rate: 450 requests/minute

### Optimization Tips

1. **Enable caching**: Default 5-minute TTL
2. **Batch requests**: Use `analyze_week` instead of separate calls
3. **Adjust cache expiration**: Longer TTL = fewer API calls
4. **Monitor usage**: Check API dashboard regularly


## Example Usage

Example conversations using the Smart Day Planner MCP server.

## Basic Weather Queries

### Current Weather

**User:**
```
What's the weather like today?
```

**Claude:**
```
I'll check the current weather for you.

[Uses get_weather]

**Weather in San Francisco:**

- Temperature: 18°C (feels like 17°C)
- Conditions: Partly cloudy
- Humidity: 65%
- Wind Speed: 4.2 m/s

Pleasant conditions with partial cloud cover. Comfortable temperature for most activities.
```

### Weather in Different Location

**User:**
```
How's the weather in Tokyo?
```

**Claude:**
```
[Uses get_weather with location="Tokyo"]

**Weather in Tokyo:**

- Temperature: 12°C (feels like 10°C)
- Conditions: Clear sky
- Humidity: 55%
- Wind Speed: 3.1 m/s

Cool and clear conditions. You'll want a light jacket if heading outside.
```

## Weather Forecasting

### Weekly Forecast

**User:**
```
What's the weather forecast for this week?
```

**Claude:**
```
I'll get the week's forecast.

[Uses get_forecast with days=7]

**Weather Forecast:**

**Monday (2025-02-03):**
  Avg: 17.3°C | High: 20.1°C | Low: 14.5°C
  Conditions: Partly cloudy

**Tuesday (2025-02-04):**
  Avg: 16.8°C | High: 19.2°C | Low: 14.1°C
  Conditions: Light rain

**Wednesday (2025-02-05):**
  Avg: 18.5°C | High: 21.3°C | Low: 15.7°C
  Conditions: Clear sky

The week starts pleasant, expect some light rain on Tuesday, then clearing up
for a nice Wednesday. Good planning opportunity for outdoor activities on
Monday and Wednesday.
```

## Task Management

### Viewing Todos

**User:**
```
What's on my todo list?
```

**Claude:**
```
Let me check your Todoist tasks.

[Uses list_todos]

**Your Tasks (8 total):**

**P1 (Urgent):**
  - Finish project proposal (Due: Today)
  - Review pull requests (Due: Tomorrow)

**P2 (High):**
  - Update documentation
  - Schedule team meeting (Due: This week)

**P3 (Medium):**
  - Research new frameworks
  - Clean up old branches

**P4 (Low):**
  - Read industry articles
  - Update personal website

You have 2 urgent tasks that need attention today and tomorrow. The project
proposal is your top priority.
```

## Comprehensive Analysis

### Weekly Planning

**User:**
```
Help me plan my week
```

**Claude:**
```
I'll analyze your week comprehensively.

[Uses analyze_week - fetches weather, forecast, and todos concurrently]

# Weekly Planning Report

**Weather in San Francisco:**

- Temperature: 18°C (feels like 17°C)
- Conditions: Partly cloudy
- Humidity: 65%
- Wind Speed: 4.2 m/s

**Weather Forecast:**

**Monday (2025-02-03):**
  Avg: 17.3°C | High: 20.1°C | Low: 14.5°C
  Conditions: Partly cloudy

**Tuesday (2025-02-04):**
  Avg: 16.8°C | High: 19.2°C | Low: 14.1°C
  Conditions: Light rain

**Wednesday (2025-02-05):**
  Avg: 18.5°C | High: 21.3°C | Low: 15.7°C
  Conditions: Clear sky

**Your Tasks (8 total):**

**P1 (Urgent):**
  - Finish project proposal (Due: Today)
  - Review pull requests (Due: Tomorrow)

**P2 (High):**
  - Update documentation
  - Schedule team meeting (Due: This week)

**P3 (Medium):**
  - Research new frameworks
  - Clean up old branches

## Weekly Planning Insights:

Based on your weather forecast and task list:

- You have 2 urgent tasks this week
- Check the forecast for good weather days to plan outdoor activities
- Consider scheduling indoor tasks on rainy or cold days

**Suggested Schedule:**

**Monday (Today):**
- Morning: Focus on finishing project proposal (urgent)
- Afternoon: Take advantage of good weather for outdoor break or walking meeting
- Evening: Light tasks

**Tuesday (Rain expected):**
- Perfect day for indoor focused work
- Review pull requests (urgent)
- Update documentation
- Stay indoors and be productive

**Wednesday (Clear, nice weather):**
- Schedule outdoor meetings if possible
- Team meeting - maybe suggest outdoor venue?
- Research can be done anywhere - consider change of scenery

**Rest of week:**
- Medium priority tasks on remaining days
- Save low-priority items for fill-in time
```

## Activity Suggestions

### Should I Go Outside?

**User:**
```
Should I plan outdoor activities today?
```

**Claude:**
```
Let me check the current conditions.

[Uses suggest_activities]

**Activity Suggestions for San Francisco:**

**Weather in San Francisco:**

- Temperature: 18°C (feels like 17°C)
- Conditions: Partly cloudy
- Humidity: 65%
- Wind Speed: 4.2 m/s

**Moderate Weather - Many Options:**
- Great for walking or light outdoor activities
- Mix of indoor and outdoor tasks
- Comfortable for errands and meetings
- Good day for varied activities

Yes! Today is excellent for outdoor activities. The temperature is comfortable
and conditions are pleasant. Perfect for:
- A lunch walk
- Outdoor meeting
- Running errands
- Light exercise
- Park visit

Just keep a light jacket handy in case it gets breezy.
```

### Rainy Day Activities

**User:**
```
It's raining today. What should I do?
```

**Claude:**
```
[Uses suggest_activities]

**Activity Suggestions for San Francisco:**

**Weather in San Francisco:**

- Temperature: 14°C (feels like 12°C)
- Conditions: Light rain
- Humidity: 82%
- Wind Speed: 5.1 m/s

**Indoor Activities Recommended:**
- Work on indoor projects
- Good day for focused work or reading
- Visit museums or indoor venues
- Catch up on indoor chores

Perfect day to:
- Tackle your focused work tasks (like that documentation update)
- Catch up on reading or research
- Indoor exercise at the gym
- Cozy productive day at home or office
- Good weather for deep work without FOMO about being outside
```

## Using Prompts

### Weekly Planning Prompt

**User:**
```
Use the plan-week prompt to help me organize my week
```

**Claude:**
```
[Uses plan-week prompt which triggers analyze_week]
[Analyzes weather, forecast, and todos]

Based on your weekly analysis, here's an optimized schedule:

## Recommended Weekly Schedule

**High-Priority Days:**

**Monday & Wednesday** - Best weather days (clear, 19-21°C)
- Schedule any outdoor meetings
- Plan for outdoor lunch breaks
- Good morale boost with nice weather

**Tuesday** - Rain day (perfect for focus)
- Tackle your urgent code reviews
- Update documentation (requires concentration)
- No distractions from nice weather

**Task Optimization:**

**Urgent (This Week):**
1. **Today**: Finish project proposal (3-4 hours focused time)
2. **Tomorrow**: Review pull requests (Tuesday's rain = perfect focus day)

**High Priority:**
3. **Wednesday**: Schedule team meeting (good weather = better mood)
4. **This week**: Update documentation (Tuesday during rain)

**Medium Priority:**
- Research frameworks: Thursday/Friday (flexible timing)
- Clean up branches: Friday afternoon (good wind-down task)

**Low Priority:**
- Reading articles: Evenings or weekend
- Personal website: Weekend project

**Weather-Task Alignment:**

✓ Intensive focus work → Tuesday (rain keeps you inside)
✓ Collaborative work → Monday/Wednesday (good weather improves mood)
✓ Flexible tasks → Adjust based on how week progresses

**Pro Tips:**
- Set up outdoor walking meeting with team on Wednesday if possible
- Use Monday's nice weather for a refreshing lunch walk
- Keep Tuesday clear of meetings for deep work during rain
- Front-load urgent tasks early in week

Would you like me to help you with any of these specific tasks?
```

### Outdoor Activity Planning

**User:**
```
Help me plan outdoor activities this weekend using the outdoor-activities prompt
```

**Claude:**
```
[Uses outdoor-activities prompt]
[Gets forecast and current conditions]

## Weekend Outdoor Activity Planning

**Current Conditions:**
Temperature: 18°C, Partly cloudy - Nice conditions!

**Weekend Forecast:**

**Saturday:**
- High: 21°C, Low: 15°C
- Conditions: Clear sky
- ⭐ **EXCELLENT for outdoor activities**

**Sunday:**
- High: 19°C, Low: 14°C
- Conditions: Partly cloudy
- ✓ **GOOD for outdoor activities**

**Saturday - Prime Day:**
Clear skies and warm temperatures make this the best day of the weekend!

**Recommended Activities:**
- Hiking or long nature walks
- Cycling or outdoor sports
- Beach or park visit
- Outdoor dining
- Photography (great lighting)
- Picnic lunch
- Gardening projects

**Sunday - Also Good:**
Still pleasant, slightly cooler.

**Recommended Activities:**
- Morning jog or run
- Farmers market visit
- Outdoor brunch
- Casual outdoor activities
- Walking tours

**Planning Tips:**
- Book Saturday for your most desired outdoor activity
- Plan around midday (warmest time: 11am-3pm)
- Bring sunscreen - clear skies mean more sun exposure
- Stay hydrated
- Have backup indoor options just in case

**Suggested Weekend Schedule:**

**Saturday:**
- Morning: Early hike or bike ride (beat crowds)
- Lunch: Outdoor dining
- Afternoon: Beach or park
- Evening: Outdoor dinner

**Sunday:**
- Morning: Farmers market or light exercise
- Lunch: Outdoor brunch
- Afternoon: Relaxed outdoor time or indoor recovery
- Evening: Prep for next week

Make the most of this great weather weekend!
```

## Complex Scenarios

### Adapting to Changes

**User:**
```
My urgent task is done. What should I focus on now given the weather?
```

**Claude:**
```
Great job completing that task! Let me check conditions.

[Uses get_weather and list_todos]

**Current Weather:** 19°C, Clear sky - Beautiful day!

**Remaining Tasks:**

**High Priority:**
- Update documentation
- Schedule team meeting

**Medium Priority:**
- Research new frameworks
- Clean up old branches

**Recommendation:**

Since it's beautiful outside and you've completed your urgent work:

1. **Take a well-deserved break**: 20-30 minute walk outside to recharge

2. **Then tackle one of these:**
   - Schedule team meeting (quick task, good to complete)
   - Update documentation (but maybe in a cafe with outdoor seating?)

3. **Save for later/tomorrow:**
   - Research frameworks (can be done anytime)
   - Branch cleanup (good rainy day task)

**Optimal Approach:**
Work on "schedule team meeting" now (quick win), then enjoy the weather with a
working lunch outdoors while doing some documentation updates. Save the heavy
research for a less nice weather day when you won't feel bad being inside.

Work-life balance matters! You're ahead on urgent tasks, so take advantage of
the nice weather while staying productive.
```

## Error Handling Examples

### Missing API Configuration

**User:**
```
What's the weather?
```

**Claude:**
```
[Uses get_weather]

Error: OpenWeatherMap API key not configured. Please set OPENWEATHER_API_KEY in .env file.

To set up weather functionality:
1. Get a free API key from https://openweathermap.org/api
2. Add it to your .env file: OPENWEATHER_API_KEY=your_key_here
3. Restart the server

I can help with other tasks if you have Todoist configured!
```

### Graceful Degradation

**User:**
```
Analyze my week
```

**Claude:**
```
[Uses analyze_week - Todoist works, weather API fails]

# Weekly Planning Report

⚠️ Current weather unavailable

⚠️ Weather forecast unavailable

**Your Tasks (8 total):**

**P1 (Urgent):**
  - Finish project proposal (Due: Today)
  - Review pull requests (Due: Tomorrow)

[... full task list ...]

## Weekly Planning Insights:

I can see your task list, but weather data is currently unavailable.

**Task-Based Recommendations:**
- Focus on your 2 urgent tasks first
- Schedule team meeting this week
- Plan medium-priority tasks for later in week

For weather-aware planning, please check your OpenWeatherMap API configuration.
I can still help you prioritize and organize your tasks!
```

## Tips for Best Results

### Be Specific About Locations
```
❌ "Weather?"
✓ "What's the weather in Seattle?"
```

### Use Contextual Queries
```
✓ "Should I go hiking this weekend?"
✓ "Help me plan indoor work for rainy days"
✓ "When's the best day for outdoor meetings?"
```

### Leverage Prompts for Complex Planning
```
✓ "Use the plan-week prompt"
✓ "Help me plan outdoor activities for the weekend"
```

### Combine Multiple Data Sources
```
✓ "Based on weather and my tasks, what should I do today?"
✓ "Which day this week is best for focused work?"
```

---

**Experiment with these patterns!** The more context you provide, the better
the recommendations become.

## Additional Resources

- [OpenWeatherMap API Docs](https://openweathermap.org/api)
- [Todoist API Docs](https://developer.todoist.com/rest/v2/)
- [aiohttp Documentation](https://docs.aiohttp.org/)
- [Python asyncio Guide](https://docs.python.org/3/library/asyncio.html)

## What's Next

You've completed all three MCP tutorial projects! You now understand:

- ✅ Basic MCP server structure (Docker Dev Assistant)
- ✅ File operations and vector search (Personal Knowledge Base)
- ✅ Async operations and API integration (Smart Day Planner)

**Next steps:**

1. **Build your own MCP server** for a personal use case
2. **Combine concepts** from all three projects
3. **Share your creation** with the community
4. **Contribute** improvements to these examples

---

**Questions?** Check the [main README](../README.md) or [documentation](../docs/).
