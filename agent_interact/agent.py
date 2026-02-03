import os
import requests
from dotenv import load_dotenv
from tavily import TavilyClient
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


# --- Tools ---
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


# --- Agent Definition ---
root_agent = Agent(
    name="assistant_agent",
    model="gemini-2.0-flash",
    description="Agent that can answer weather questions and search the web.",
    instruction=(
        "You are a helpful agent with two tools. "
        "Use get_weather for weather/temperature questions. "
        "Use tavily_search to search the web for any other questions like news, people, events, facts, etc."
    ),
    tools=[get_weather, tavily_search]
)

# --- Session Management ---
session_service = InMemorySessionService()

APP_NAME = "assistant_app"
USER_ID = "user_1"
SESSION_ID = "session_001"


async def setup_session():
    """Create the specific session where the conversation will happen."""
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    print(f"Session created: App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'")
    return session


# --- Runner ---
runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service
)


# --- Agent Interaction Function ---
async def call_agent_async(query: str, runner, user_id, session_id):
    """Sends a query to the agent and prints the final response."""
    print(f"\n>>> User Query: {query}")

    # Prepare the user's message in ADK format
    content = types.Content(role='user', parts=[types.Part(text=query)])

    final_response_text = "Agent did not produce a final response."  # Default

    # Key Concept: run_async executes the agent logic and yields Events.
    # We iterate through events to find the final answer.
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        # You can uncomment the line below to see *all* events during execution
        # print(f"  [Event] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}, Content: {event.content}")

        # Key Concept: is_final_response() marks the concluding message for the turn.
        if event.is_final_response():
            if event.content and event.content.parts:
                # Assuming text response in the first part
                final_response_text = event.content.parts[0].text
            elif event.actions and event.actions.escalate:  # Handle potential errors/escalations
                final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
            # Add more checks here if needed (e.g., specific error codes)
            break  # Stop processing events once the final response is found

    print(f"<<< Agent Response: {final_response_text}")


if __name__ == "__main__":
    import asyncio

    async def main():
        await setup_session()
        await call_agent_async("what's the weather in Singapore?", runner, USER_ID, SESSION_ID)

    asyncio.run(main())
