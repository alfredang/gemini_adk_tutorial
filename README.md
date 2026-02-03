# Gemini ADK Tutorial

A collection of example agents built with [Google's Agent Development Kit (ADK)](https://google.github.io/adk-docs/).

## Prerequisites

- Python 3.13+
- Google API Key (for Gemini models)
- Optional: OpenWeather API Key (for weather tools)
- Optional: Tavily API Key (for web search)

## Installation

```bash
# Clone the repository
git clone https://github.com/alfredang/gemini_tutorial.git
cd gemini_tutorial

# Install dependencies using uv
uv sync

# Or using pip
pip install google-adk python-dotenv requests tavily-python streamlit
```

## Configuration

Create a `.env` file in each agent directory with your API keys:

```env
GOOGLE_GENAI_USE_VERTEXAI=0
GOOGLE_API_KEY=your-google-api-key
OPENWEATHER_API_KEY=your-openweather-key
TAVILY_API_KEY=your-tavily-key
```

## Running Agents

Use the ADK CLI to run any agent:

```bash
# Terminal mode
adk run <agent_directory>

# Web UI mode
adk web <agent_directory>
```

## Agent Examples

| Agent | Description |
|-------|-------------|
| `basic_agent` | Simple banking assistant agent |
| `multi_tools_agent` | Agent with OpenWeather and Tavily search tools |
| `agent_session` | Demonstrates session management with Runner |
| `agent_interact` | Shows agent interaction patterns with event handling |
| `agent_handoff` | Multi-agent handoff between joke generator and translator |
| `agent_guardrail` | Agent with `before_model_callback` guardrail to block keywords |
| `agent_structured_output` | Pydantic-based structured output (Recipe example) |
| `agent_mcp` | MCP (Model Context Protocol) with StreamableHTTP |
| `agent_mcp_sse` | MCP with SSE (Server-Sent Events) standard |
| `agent_model` | Agent with different model configurations |
| `transport_agent` | Sequential workflow for Singapore transport planning |
| `transport_agent_yaml` | YAML-based agent configuration (experimental) |
| `transport_agent_streamlit` | Streamlit web interface for transport agent |
| `stock_agent` | Hierarchical multi-agent system for stock analysis |
| `travel_agent` | Multi-agent travel planner with specialized sub-agents |
| `tutor_agent` | Multi-agent tutoring system with subject-specific tutors |

## Key Concepts

### Agent Types

| Agent Type | Description |
|------------|-------------|
| `Agent` / `LlmAgent` | Basic LLM-powered agent |
| `SequentialAgent` | Runs sub-agents in sequence |
| `ParallelAgent` | Runs sub-agents in parallel |

### Using Different Models

```python
# Gemini (default)
model='gemini-2.0-flash'

# OpenAI via LiteLlm
from google.adk.models.lite_llm import LiteLlm
model=LiteLlm(model="openai/gpt-4o-mini")
```

### Adding Tools

```python
from google.adk.tools import google_search

# Built-in tools
tools=[google_search]

# Custom function tools
def get_weather(city: str) -> dict:
    return {"status": "success", "report": "..."}

tools=[get_weather]
```

### Sub-agents & Handoff

```python
root_agent = Agent(
    name="root_agent",
    sub_agents=[agent1, agent2],
    instruction="Transfer to agent1 for task A, agent2 for task B"
)
```

### Guardrails

```python
def block_keyword_guardrail(callback_context, llm_request):
    # Block requests containing certain keywords
    if "BLOCK" in user_message.upper():
        return LlmResponse(content=...)
    return None

agent = Agent(
    before_model_callback=block_keyword_guardrail,
    ...
)
```

### Structured Output

```python
from pydantic import BaseModel

class Recipe(BaseModel):
    title: str
    ingredients: list[str]

agent = Agent(
    output_schema=Recipe,
    ...
)
```

## Running with Streamlit

```bash
cd transport_agent_streamlit
streamlit run app.py
```

## Resources

- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [Google ADK GitHub](https://github.com/google/adk-python)

## License

MIT
