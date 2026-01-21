# Gemini ADK Tutorial

A collection of example agents built with [Google's Agent Development Kit (ADK)](https://google.github.io/adk-docs/).

## Prerequisites

- Python 3.13+
- Google API Key (for Gemini models)
- Optional: OpenAI API Key (for OpenAI model examples)
- Optional: Tavily API Key (for travel agent)

## Installation

```bash
# Clone the repository
git clone https://github.com/alfredang/gemini-adk-tutorial.git
cd gemini-adk-tutorial

# Install dependencies using uv
uv sync

# Or using pip
pip install -e .
```

## Configuration

Create a `.env` file in each agent directory with your API keys:

```env
GOOGLE_GENAI_USE_VERTEXAI=0
GOOGLE_API_KEY=your-google-api-key
OPENAI_API_KEY=your-openai-api-key  # Optional, for OpenAI examples
TAVILY_API_KEY=your-tavily-api-key  # Optional, for travel_agent
```

## Running Agents

Use the ADK CLI to run any agent:

```bash
adk run <agent_directory>
```

For example:

```bash
adk run my_agent
adk run stock_agent
adk run travel_agent
```

## Agent Examples

### my_agent
A basic "Hello World" agent using Gemini.

```python
from google.adk.agents import Agent

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge',
)
```

### my_agent_model
Demonstrates using OpenAI models via LiteLlm integration.

```python
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

root_agent = Agent(
    model=LiteLlm(model="openai/gpt-4.1-mini"),
    ...
)
```

### my_agent_tools
Shows how to add tools (like Google Search) to an agent.

```python
from google.adk.agents import Agent
from google.adk.tools import google_search

root_agent = Agent(
    model='gemini-2.5-flash',
    tools=[google_search],
    ...
)
```

### my_agent_session
Demonstrates session management with `InMemorySessionService` and `Runner`.

### stock_agent
A hierarchical multi-agent system for stock analysis:

- **root_agent** - Greets user and introduces capabilities
- **stock_workflow_agent** (SequentialAgent) - Orchestrates the workflow
  - **ticker_input_agent** - Collects stock ticker from user
  - **stock_research_agent** - Researches and generates a detailed report

### travel_agent
A multi-agent travel planner with specialized sub-agents:

- **planner_agent** - Creates day-by-day itineraries
- **budget_agent** - Estimates travel costs
- **local_guide_agent** - Provides food and cultural tips
- **research_agent** - Searches for current travel information (uses Tavily)

### tutor_agent
A multi-agent tutoring system with subject-specific tutors:

- **math_tutor_agent** - Helps with mathematics
- **physics_tutor_agent** - Helps with physics
- **history_tutor_agent** - Helps with history

## Key Concepts

### Agent Types

| Agent Type | Description |
|------------|-------------|
| `Agent` / `LlmAgent` | Basic LLM-powered agent |
| `SequentialAgent` | Runs sub-agents in sequence |
| `ParallelAgent` | Runs sub-agents in parallel |
| `LoopAgent` | Runs sub-agents in a loop |

### Using Different Models

```python
# Gemini (default)
model='gemini-2.5-flash'

# OpenAI via LiteLlm
from google.adk.models.lite_llm import LiteLlm
model=LiteLlm(model="openai/gpt-4o-mini")

# Claude via LiteLlm
model=LiteLlm(model="anthropic/claude-3-5-sonnet-20241022")
```

### Adding Tools

```python
from google.adk.tools import google_search

# Built-in tools
tools=[google_search]

# Custom function tools
def my_tool(query: str) -> dict:
    return {"result": "..."}

tools=[my_tool]
```

### Sub-agents

```python
root_agent = Agent(
    name="root_agent",
    sub_agents=[agent1, agent2, agent3],
    ...
)
```

## Resources

- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [Google ADK GitHub](https://github.com/google/adk-python)
- [LiteLlm Documentation](https://docs.litellm.ai/)

## License

MIT
