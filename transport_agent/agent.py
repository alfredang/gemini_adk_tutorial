from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools import google_search

MODEL = "gemini-2.0-flash"

# Sub-agent 1: Greets user and asks for stock ticker
destination_input_agent = LlmAgent(
    model=MODEL,
    name="destination_input_agent",
    description="Agent that greets the user and collects a location of interest.",
    instruction="""You are the location Input agent.

Greet the user warmly and introduce yourself as the Route Planner Agent
Explain that you can help to find the fastest route for various transport methods (e.g., MRT, BUS, TAXI, CYCLING, WALKING).
Ask the user to provide a current Location and a destination location
Once the user provides their location as well as the destination, extract the locations and confirm it with the user.
Store the location in your response so it can be passed to the next agent.""",
)

# Sub-agent 2: Searches and synthesizes stock information
flight_research_agent = LlmAgent(
    model=MODEL,
    name="cross_country_research_agent",
    description="Agent that researches information route between 2 countries and chooses the most cost to time efficient route.",
    instruction="""You are a cross country Research agent specialized in getting the best flight between 2 countries.

Base all timing related considerations to the system time of SINGAPORE.

Check both location using the google_search tool on whether the location is valid in SINGAPORE, if the user provides both locations within SINGAPORE, proceed to Store the locations in your response so it can be passed to the next agent.

Otherwise, using the google_search tool, identify the country of both locations and gather the following information:
- Methods to get from country of the current location to the country of the destination location
- Cost of each method
- Time taken for each method
- Any significant events or announcements

Store the 2 location in your response along with the most optimal route for cost to time spend ratio across country so it can be passed to the next agent.
""",
    tools=[google_search],
)

# Sub-agent 2: Searches and synthesizes stock information
route_research_agent = LlmAgent(
    model=MODEL,
    name="route_research_agent",
    description="Agent that researches route information and creates the most time efficient route.",
    instruction="""You are a Route Research agent specialized in transportation planning.

Base all timing related considerations to the current time of the country of interest.

If you dont receive any information regarding cross country travel from the previous agent, take the current location and destination location provided by the previous agent, starting from the given current location, and use the google_search tool to gather:
- Latest route information and travel times for various transport methods (TRAIN/MRT, BUS, TAXI, WALK)
- Traffic conditions and delays
- Alternative routes and options
- Public transport schedules and availability

After gathering information, synthesize everything into a comprehensive, well-formatted report that includes:
1. **By Bus** - A route from the current location to the destination strictly by bus only
2. **By MRT/Train** - A route from the current location to the destination strictly by MRT/Train only
3. **By Taxi** - A route from the current location to the destination strictly by taxi
4. **By Cycling** - A route from the current location to the destination strictly by cycling/biking
5. **By Walking** - A route from the current location to the destination strictly by walking
6. **Fastest Route** - A route from the current location to the destination by all means of transport available in SINGAPORE while optimizing the best cost to time spent ratio.

Present the information in a clear, professional format that would be concise for a person who is in a rush.""",
    tools=[google_search],
)

# Workflow agent: Sequential orchestration of the two sub-agents
transport_workflow_agent = SequentialAgent(
    name="transport_workflow_agent",
    description="Sequential workflow that collects a Destination and Current Location, and then researches it.",
    sub_agents=[destination_input_agent, flight_research_agent,route_research_agent],
)

# Root agent: Greets user and transfers to workflow
root_agent = LlmAgent(
    model=MODEL,
    name="root_agent",
    description="Root agent that introduces route planning capabilities and delegates to workflow.",
    instruction="""You are a friendly Route Planning Assistant.

When the user first interacts with you:
1. Greet them warmly
2. Introduce yourself and explain that you can help them plan routes in Singapore
3. Mention that you have a specialized Route Planner agent that will help gather their destination and current location and provide detailed route information

After your introduction, transfer control to the transport_workflow_agent to begin the analysis process.""",
    sub_agents=[transport_workflow_agent],
)