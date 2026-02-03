import os
import requests
from typing import Optional
from dotenv import load_dotenv
from tavily import TavilyClient
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


# --- Guardrail Callback ---
def block_keyword_guardrail(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """
    Inspects the latest user message for 'BLOCK'. If found, blocks the LLM call
    and returns a predefined LlmResponse. Otherwise, returns None to proceed.
    """
    agent_name = callback_context.agent_name
    print(f"--- Callback: block_keyword_guardrail running for agent: {agent_name} ---")

    # Extract the text from the latest user message in the request history
    last_user_message_text = ""
    if llm_request.contents:
        for content in reversed(llm_request.contents):
            if content.role == 'user' and content.parts:
                if content.parts[0].text:
                    last_user_message_text = content.parts[0].text
                    break

    print(f"--- Callback: Inspecting last user message: '{last_user_message_text[:100]}...' ---")

    # --- Guardrail Logic ---
    keyword_to_block = "BLOCK"
    if keyword_to_block in last_user_message_text.upper():
        print(f"--- Callback: Found '{keyword_to_block}'. Blocking LLM call! ---")
        callback_context.state["guardrail_block_keyword_triggered"] = True
        print(f"--- Callback: Set state 'guardrail_block_keyword_triggered': True ---")

        return LlmResponse(
            content=types.Content(
                role="model",
                parts=[types.Part(text=f"I cannot process this request because it contains the blocked keyword '{keyword_to_block}'.")],
            )
        )
    else:
        print(f"--- Callback: Keyword not found. Allowing LLM call for {agent_name}. ---")
        return None


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


# --- Agent Definition with Guardrail ---
root_agent = Agent(
    name="guarded_agent",
    model="gemini-2.0-flash",
    description="Agent with guardrail that blocks certain keywords.",
    instruction=(
        "You are a helpful agent with two tools. "
        "Use get_weather for weather/temperature questions. "
        "Use tavily_search to search the web for any other questions."
    ),
    tools=[get_weather, tavily_search],
    before_model_callback=block_keyword_guardrail,  # Attach the guardrail
)

print("✅ Agent with guardrail created.")
