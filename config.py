# config.py
import os

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# if not GROQ_API_KEY:
#     GROQ_API_KEY = "YOUR_GROQ_API_KEY_HERE" # I have iintentionally left for user awareness

GROQ_MODEL_NAME = os.getenv("GROQ_MODEL_NAME", "llama3-8b-8192")
LLM_TEMPERATURE = 0.1
# AGENT_SYSTEM_PROMPT = "You are a helpful AI assistant..." # here is the example of a config option