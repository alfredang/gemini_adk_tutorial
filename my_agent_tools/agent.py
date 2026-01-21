from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import google_search

root_agent = Agent(
    model=LiteLlm(model="openai/gpt-4o-mini"),
    name="interactions_test_agent",
    instruction='Answer user questions to the best of your knowledge',
    description="A helpful assistant for user questions.",
    tools=[google_search],
)