# Multi-Agent Tutor using Google ADK
import os
from dotenv import load_dotenv
from google.adk.agents import Agent

import warnings
warnings.filterwarnings("ignore")

import logging
logging.basicConfig(level=logging.ERROR)

# Load environment variables
load_dotenv()

# API Keys
google_api_key = os.environ.get("GOOGLE_API_KEY")

if not google_api_key:
    raise ValueError("GOOGLE_API_KEY is not set in the environment variables")

# Model constant
MODEL = "gemini-2.5-flash"


# ---------- SPECIALIZED SUB-AGENTS ----------

math_tutor_agent = Agent(
    name="math_tutor_agent",
    model=MODEL,
    description="Helps with mathematics questions including algebra, calculus, geometry, statistics, and arithmetic.",
    instruction=(
        "You are a patient and encouraging math tutor. Help students understand mathematical concepts clearly.\n"
        "- Break down problems into step-by-step solutions\n"
        "- Explain the reasoning behind each step\n"
        "- Use examples to illustrate concepts\n"
        "- Encourage students when they struggle\n"
        "- Provide practice problems when appropriate\n"
        "Respond concisely and focus on helping the student understand, not just giving answers."
    ),
)

physics_tutor_agent = Agent(
    name="physics_tutor_agent",
    model=MODEL,
    description="Helps with physics questions including mechanics, thermodynamics, electromagnetism, optics, and modern physics.",
    instruction=(
        "You are a knowledgeable and patient physics tutor. Help students understand physics concepts and solve problems.\n"
        "- Explain physical principles and laws clearly\n"
        "- Show how to apply formulas with proper units\n"
        "- Use real-world examples to make concepts relatable\n"
        "- Draw connections between different physics topics\n"
        "- Guide students through problem-solving strategies\n"
        "Respond concisely and help students build physical intuition."
    ),
)

history_tutor_agent = Agent(
    name="history_tutor_agent",
    model=MODEL,
    description="Helps with history questions including world history, ancient civilizations, modern history, and historical analysis.",
    instruction=(
        "You are an engaging and insightful history tutor. Help students understand historical events and their significance.\n"
        "- Provide context for historical events\n"
        "- Explain cause and effect relationships\n"
        "- Connect historical events to broader themes\n"
        "- Help students analyze primary and secondary sources\n"
        "- Encourage critical thinking about historical narratives\n"
        "Respond concisely and make history come alive for students."
    ),
)


# ---------- ROOT TUTOR AGENT (Orchestrator) ----------

root_agent = Agent(
    name="tutor_agent",
    model=MODEL,
    description="A friendly tutor that orchestrates specialized subject tutors to help students learn.",
    instruction=(
        "You are a friendly and supportive tutor coordinator. Your role is to help students by delegating to specialized tutors:\n"
        "1. math_tutor_agent - for mathematics questions (algebra, calculus, geometry, statistics, etc.)\n"
        "2. physics_tutor_agent - for physics questions (mechanics, thermodynamics, electromagnetism, etc.)\n"
        "3. history_tutor_agent - for history questions (world history, civilizations, historical analysis, etc.)\n\n"
        "IMPORTANT:\n"
        "- Identify the subject area from the student's question and delegate to the appropriate tutor\n"
        "- If a question spans multiple subjects, coordinate between tutors\n"
        "- If a question is outside these subjects, politely explain your areas of expertise\n"
        "- Be encouraging and supportive throughout the learning process\n\n"
        "After receiving the tutor's response, present it clearly to the student."
    ),
    sub_agents=[math_tutor_agent, physics_tutor_agent, history_tutor_agent],
)
