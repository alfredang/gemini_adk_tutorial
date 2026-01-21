from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools import google_search

MODEL = "gemini-2.5-flash"

# Sub-agent 1: Greets user and asks for stock ticker
ticker_input_agent = LlmAgent(
    model=MODEL,
    name="ticker_input_agent",
    description="Agent that greets the user and collects a stock ticker symbol.",
    instruction="""You are the Stock Ticker agent.

Greet the user warmly and introduce yourself as the Stock Ticker agent.
Explain that you can help analyze stocks and provide insights.
Ask the user to provide a stock market ticker symbol (e.g., NVDA, GOOG, AAPL, MSFT).

Once the user provides a ticker, extract the stock symbol and confirm it with the user.
Store the ticker symbol in your response so it can be passed to the next agent.""",
)

# Sub-agent 2: Searches and synthesizes stock information
stock_research_agent = LlmAgent(
    model=MODEL,
    name="stock_research_agent",
    description="Agent that researches stock information and creates a detailed report.",
    instruction="""You are a Stock Research agent specialized in financial analysis.

Take the stock ticker provided by the previous agent and use the google_search tool to gather:
- Latest stock price and market data
- Recent news and headlines about the company
- Analyst reports and recommendations
- Key financial metrics and performance indicators
- Any significant events or announcements

After gathering information, synthesize everything into a comprehensive, well-formatted report that includes:
1. **Company Overview** - Brief description of the company
2. **Current Stock Price** - Latest trading information
3. **Recent News** - Key headlines and developments
4. **Analyst Insights** - Recommendations and price targets
5. **Key Takeaways** - Summary of important points for investors

Present the information in a clear, professional format that would be useful for an investor.""",
    tools=[google_search],
)

# Workflow agent: Sequential orchestration of the two sub-agents
stock_workflow_agent = SequentialAgent(
    name="stock_workflow_agent",
    description="Sequential workflow that collects a ticker and then researches it.",
    sub_agents=[ticker_input_agent, stock_research_agent],
)

# Root agent: Greets user and transfers to workflow
root_agent = LlmAgent(
    model=MODEL,
    name="root_agent",
    description="Root agent that introduces stock analysis capabilities and delegates to workflow.",
    instruction="""You are a friendly Stock Analysis Assistant.

When the user first interacts with you:
1. Greet them warmly
2. Introduce yourself and explain that you can help them analyze stocks
3. Mention that you have a specialized Stock Ticker agent that will help gather their stock of interest and provide detailed insights

After your introduction, transfer control to the stock_workflow_agent to begin the analysis process.""",
    sub_agents=[stock_workflow_agent],
)
