import os
import requests
from dotenv import load_dotenv
from tavily import TavilyClient
from google.adk.agents import Agent

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


def get_weather(city: str) -> dict:
    """Retrieves the current weather and temperature for a specified city.

    Args:
        city (str): The name of the city.

    Returns:
        dict: status and result or error msg.
    """
    if not OPENWEATHER_API_KEY:
        return {"status": "error", "error_message": "OpenWeather API key not configured."}

    base_url = "http://api.openweathermap.org/data/2.5/weather"
    complete_url = f"{base_url}?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"

    try:
        response = requests.get(complete_url)
        data = response.json()

        if response.status_code != 200:
            return {"status": "error", "error_message": data.get("message", "Failed to fetch weather.")}

        weather_description = data["weather"][0]["description"]
        temperature = data["main"]["temp"]
        return {
            "status": "success",
            "report": f"The current weather in {city} is {weather_description} with a temperature of {temperature}°C.",
        }
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def tavily_search(query: str) -> dict:
    """Searches the web for information using Tavily.

    Args:
        query (str): The search query.

    Returns:
        dict: status and search results or error msg.
    """
    if not TAVILY_API_KEY:
        return {"status": "error", "error_message": "Tavily API key not configured."}

    try:
        tavily = TavilyClient(api_key=TAVILY_API_KEY)
        response = tavily.search(query=query, search_depth="basic")

        results = response.get("results", [])
        summary = "\n".join([f"Source: {res['url']}\nContent: {res['content']}" for res in results])
        return {"status": "success", "report": summary}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


root_agent = Agent(
    name="assistant_agent",
    model="gemini-2.0-flash",
    description="Agent that can answer weather questions and search the web.",
    instruction=(
        "You are a helpful agent with two tools. "
        "Use get_weather for weather/temperature questions. "
        "Use tavily_search to search the web for any other questions like news, people, events, facts, etc."
    ),
    tools=[get_weather, tavily_search],
)
