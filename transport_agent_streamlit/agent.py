from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools import google_search


MODEL = "gemini-2.5-flash"

transport_research_agent = LlmAgent(
    model=MODEL,
    name='transport_research_agent',
    description='A helpful transport research assistant for user transport questions.',
    instruction='Check for various transport options and provide detailed information to answer user questions to the best of your knowledge Consider both public and private transport options.',
    tools=[google_search]
)

budget_agent = LlmAgent(
    model=MODEL,
    name='budget_agent',
    description='A helpful budget assistant for user transport questions.',
    instruction="""
    When the user first interacts with you:
    1. Greet them warmly
    2. Introduce yourself and explain that you can help them plan their travel route
    3. Mention that you have a specialized budget Analysis agent that will help gather their destination of interest and provide detailed planning information
    
    Obtain the most cost-effective transport options to answer user questions to the best of your knowledge
    """,
    tools=[google_search]
)

time_management_agent = LlmAgent(
    model=MODEL,
    name='time_management_agent',
    description='A helpful time management assistant for user transport questions.',
    instruction=
    """
    You are a friendly Travel Analysis Assistant.

    When the user first interacts with you:
    1. Greet them warmly
    2. Introduce yourself and explain that you can help them plan their travel route
    3. Mention that you have a specialized time management agent that will help gather their destination of interest and provide detailed planning information
    Provide the most time-efficient transport options to answer user questions to the best of your knowledge
    """,
    tools=[google_search]
)

# Workflow agent: Sequential orchestration of the two sub-agents
transport_workflow_agent = SequentialAgent(
    name="transport_workflow_agent",
    description="Sequential workflow that collects a ticker and then researches it.",
    sub_agents=[transport_research_agent, budget_agent, time_management_agent],
)

root_agent = LlmAgent(
    model=MODEL,
    name='travel_agent',
    description="A friendly travel planner that orchestrates specialized agents to plan trips.",
    instruction="""You are a friendly Travel Analysis Assistant.

When the user first interacts with you:
1. Greet them warmly
2. Introduce yourself and explain that you can help them plan their travel route
3. Mention that you have a specialized Travel Analysis agent that will help gather their destination of interest and provide detailed planning information

Extract the starting and ending destination and confirm it with the user.Store these 2 locations in your response so it can be passed to the next agent.

After your introduction, orchestrate travel planning by delegating to these sub-agents: "
        "1. transport_research_agent - for public and private transport options\n"\
        "2. budget_agent - for cost estimates\n"
        "3. time_management_agent - for time-efficient options\n"

Use the tools available to these sub-agents to gather information and provide the best possible travel plan for the user.

Do not request for additional information from the user and assume you have all the necessary details to plan the trip.""",
    sub_agents=[transport_workflow_agent]
)
