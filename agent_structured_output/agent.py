from pydantic import BaseModel
from google.adk.agents import Agent


# --- Pydantic Model for Structured Output ---
class Recipe(BaseModel):
    title: str
    ingredients: list[str]
    cooking_time: int  # in minutes
    servings: int
    instructions: list[str]


# --- Agent with Structured Output ---
root_agent = Agent(
    name="recipe_agent",
    model="gemini-2.0-flash",
    description="An agent that creates detailed recipes in structured format.",
    instruction=(
        "You are an agent for creating recipes. You will be given the name of a food and your job "
        "is to output that as an actual detailed recipe. The cooking time should be in minutes. "
        "Always respond with a valid JSON object matching this schema:\n"
        "{\n"
        '  "title": "Recipe name",\n'
        '  "ingredients": ["ingredient 1", "ingredient 2", ...],\n'
        '  "cooking_time": number (in minutes),\n'
        '  "servings": number,\n'
        '  "instructions": ["step 1", "step 2", ...]\n'
        "}"
    ),
    output_schema=Recipe,
)
