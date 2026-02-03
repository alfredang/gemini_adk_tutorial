import asyncio
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.mcp_tool import McpToolset, SseConnectionParams
from google.genai import types


# --- MCP SSE Server Configuration ---
# Replace with your actual SSE MCP server URL
MCP_SSE_URL = "http://localhost:8000/sse"


async def create_agent_with_mcp_sse():
    """Create agent with MCP SSE server tools."""

    # Configure MCP SSE connection
    sse_params = SseConnectionParams(url=MCP_SSE_URL)

    # Create MCP toolset with SSE connection
    mcp_toolset = McpToolset(connection_params=sse_params)

    # Get tools from MCP server
    tools = await mcp_toolset.get_tools()

    print(f"✅ Connected to MCP SSE server. Available tools: {[t.name for t in tools]}")

    # Create agent with MCP tools
    agent = Agent(
        name="mcp_sse_agent",
        model="gemini-2.0-flash",
        description="An agent that uses MCP SSE server tools.",
        instruction=(
            "You are an intelligent assistant. Use the tools exposed by the MCP server "
            "to retrieve answers or perform actions. Use the MCP tools to answer the user's queries with accurate output."
        ),
        tools=tools,
    )

    return agent, mcp_toolset


# --- For ADK CLI compatibility ---
root_agent = Agent(
    name="mcp_sse_agent",
    model="gemini-2.0-flash",
    description="An agent that uses MCP SSE server tools.",
    instruction=(
        "You are an intelligent assistant. Use the tools exposed by the MCP server "
        "to retrieve answers or perform actions. Use the MCP tools to answer the user's queries with accurate output."
    ),
)


# --- Session and Runner for programmatic use ---
session_service = InMemorySessionService()

APP_NAME = "mcp_sse_app"
USER_ID = "user_1"
SESSION_ID = "session_001"


async def run_mcp_agent(query: str):
    """Run the MCP SSE agent with a query."""
    agent, mcp_toolset = await create_agent_with_mcp_sse()

    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )

    runner = Runner(
        agent=agent,
        app_name=APP_NAME,
        session_service=session_service
    )

    print(f"\n>>> User Query: {query}")
    content = types.Content(role='user', parts=[types.Part(text=query)])

    try:
        async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content):
            if event.is_final_response():
                if event.content and event.content.parts:
                    print(f"<<< Agent Response: {event.content.parts[0].text}")
                break
    finally:
        await mcp_toolset.close()


if __name__ == "__main__":
    asyncio.run(run_mcp_agent("What tools are available?"))
