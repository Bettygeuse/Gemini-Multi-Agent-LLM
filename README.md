Multi Agent LLM project using Google's Gemini-1.5-pro model. Memory of past conversations is stored in a database using sqlite3, a custom web user interface is built using streamlit. The agents will do their best to answer your coding questions.

AGENTS:
- PlannerAgent: breaks down user's queries into steps
- ContextAgent: provides knowledge/context for steps
- CoderAgent: converts plan and context into python code

HOW TO RUN:
1. Change [YOUR KEY HERE] in .env to your own Google API Key
2. In your environment, run: streamlit run c:/...(where your file is located).../agents.py
