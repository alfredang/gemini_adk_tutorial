# Multi-Agent Travel Planner using Google ADK
import os
from dotenv import load_dotenv
from google.adk.agents import Agent
from tavily import TavilyClient

import warnings
warnings.filterwarnings("ignore")

import logging
logging.basicConfig(level=logging.ERROR)

# Load environment variables
load_dotenv()

# API Keys
google_api_key = os.environ.get("GOOGLE_API_KEY")
tavily_key = os.environ.get("TAVILY_API_KEY")

if not google_api_key:
    raise ValueError("GOOGLE_API_KEY is not set in the environment variables")

if not tavily_key:
    raise ValueError("TAVILY_API_KEY is not set in the environment variables")

# Model constant
MODEL = "gemini-2.5-flash"

# Tavily client
tavily_client = TavilyClient(api_key=tavily_key)


# ---------- TAVILY SEARCH TOOL ----------

def search_web(query: str) -> dict:
    try:
        response = tavily_client.search(query=query, max_results=3)
        results = []
        for r in response.get("results", []):
            results.append(f"- {r.get('title', 'No title')}: {r.get('content', '')[:200]}")
        summary = "\n".join(results) if results else "No results found."
        return {"status": "success", "results": summary}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


# ---------- SPECIALIZED SUB-AGENTS ----------

research_agent = Agent(
    name="research_agent",
    model=MODEL,
    description="Researches CURRENT travel information. Use only when real-time data is needed like travel advisories, recent events, or current conditions.",
    instruction=(
        "You research CURRENT travel information. Use the search_web tool ONLY ONCE to get essential updates like:\n"
        "- Current travel advisories or restrictions\n"
        "- Recent attraction openings/closures\n"
        "- Current events or festivals during travel dates\n"
        "Do NOT search for general information you already know. Respond concisely in one message."
    ),
    tools=[search_web],
)

planner_agent = Agent(
    name="planner_agent",
    model=MODEL,
    description="Creates day-by-day travel itineraries. Use this agent when planning or outlining an itinerary, schedule, or daily plan.",
    instruction=(
        "Create a day-by-day travel itinerary. Be concise and respond in one message. "
        "Include key attractions and activities for each day."
    ),
)

budget_agent = Agent(
    name="budget_agent",
    model=MODEL,
    description="Estimates travel costs. Use this agent when the user mentions budget, price, cost, or asks 'how much'.",
    instruction=(
        "Estimate travel costs for lodging, food, transport, and activities. Be concise and respond in one message. "
        "Provide a breakdown and total estimate."
    ),
)

local_guide_agent = Agent(
    name="local_guide_agent",
    model=MODEL,
    description="Provides local food recommendations, restaurant suggestions, and cultural tips.",
    instruction=(
        "Provide local food recommendations, restaurant suggestions, and cultural tips. Be concise and respond in one message."
    ),
)

# ---------- ROOT TRAVEL AGENT (Orchestrator) ----------

root_agent = Agent(
    name="travel_agent",
    model=MODEL,
    description="A friendly travel planner that orchestrates specialized agents to plan trips.",
    instruction=(
        "You orchestrate travel planning by delegating to these sub-agents:\n"
        "1. planner_agent - for the itinerary\n"
        "2. budget_agent - for cost estimates\n"
        "3. local_guide_agent - for food and local tips\n"
        "4. research_agent - ONLY if user needs current/real-time info (advisories, recent events)\n\n"
        "IMPORTANT: Delegate to agents efficiently. Only use research_agent when truly necessary.\n"
        "After receiving their responses, present the combined travel plan with clear sections:\n"
        "## Itinerary\n[planner agent response]\n\n## Budget\n[budget agent response]\n\n## Local Tips\n[local guide response]\n\n## Current Updates\n[research agent response, if used]"
    ),
    sub_agents=[planner_agent, budget_agent, local_guide_agent, research_agent],
)
