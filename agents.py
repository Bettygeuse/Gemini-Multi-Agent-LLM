import os
import google.generativeai as genai
import streamlit as st
import sqlite3
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-pro") 

# Constants
MEMORY_LIMIT = 6    # Amount of previous responses to display from memory

# Define agents
agents = {
    "PlannerAgent": "You are a Planner Agent. Break down the user's goal into clear, logical steps.",
    "ContextAgent": "You are a Context Agent. Given a step or question, provide relevant knowledge and context.",
    "CoderAgent": "You are a Coding Agent. Based on the plan and context, write or explain Python code."
}

# Ask agent
def ask_gemini(agent_name, role_description, user_message):
    prompt = f"""You are {agent_name}. {role_description} User Input: {user_message}"""
    print(f"\n--- {agent_name} is responding ---")
    response = model.generate_content(prompt)
    reply = response.text.strip()
    print(reply)
    return reply

# Store output into memory
def store_agent_output(agent_name, user_goal, output):
    conn = sqlite3.connect("agent_memory.db")
    c = conn.cursor()
    c.execute('''
        INSERT INTO memory (agent, user_goal, output, timestamp)
        VALUES (?, ?, ?, ?)
    ''', (agent_name, user_goal, output, datetime.now(timezone.utc).isoformat()))
    conn.commit()
    conn.close()

# Retrieve memory
def get_recent_outputs(limit=MEMORY_LIMIT):
    conn = sqlite3.connect("agent_memory.db")
    c = conn.cursor()
    c.execute('SELECT agent, user_goal, output, timestamp FROM memory ORDER BY id DESC LIMIT ?', (limit,))
    rows = c.fetchall()
    conn.close()
    return rows

# Create memory table
conn = sqlite3.connect("agent_memory.db")
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS memory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        agent TEXT,
        user_goal TEXT,
        output TEXT,
        timestamp TEXT
    )
''')
conn.commit()
conn.close()

# Streamlit Main code
st.title("Multi-Agent LLM Simulation (Gemini)")

if "user_goal" not in st.session_state:
    st.session_state.user_goal = "Build a Python script to create an AI assistant using Google Gemini"

if "expander_open" not in st.session_state:
    st.session_state.expander_open = False

if "memory_loaded" not in st.session_state:
    st.session_state.memory_loaded = False

user_goal = st.text_input("Enter your coding related goal:", value=st.session_state.user_goal)
st.session_state.user_goal = user_goal

if st.button("Run Simulation"):
    with st.spinner("Planning Agent thinking..."):
        plan = ask_gemini("PlannerAgent", agents["PlannerAgent"], st.session_state.user_goal)
        store_agent_output("PlannerAgent", user_goal, plan)
        st.session_state.plan = plan
    with st.spinner("Context Agent thinking..."):
        context = ask_gemini("ContextAgent", agents["ContextAgent"], st.session_state.plan)
        store_agent_output("ContextAgent", user_goal, context)
        st.session_state.context = context
    with st.spinner("Coding Agent thinking..."):
        code = ask_gemini("CoderAgent", agents["CoderAgent"], st.session_state.context)
        store_agent_output("CoderAgent", user_goal, code)
        st.session_state.code = code

if "plan" in st.session_state:
    st.subheader("Plan")
    st.code(st.session_state.plan, language="markdown")

if "context" in st.session_state:
    st.subheader("Context")
    st.code(st.session_state.context, language="markdown")

if "code" in st.session_state:
    st.subheader("Code")
    st.code(st.session_state.code, language="python")

if st.button("Load Memory"):
        st.session_state.memory_loaded = True
        st.session_state.expander_open = True
        
with st.expander("View Agent Memory", expanded=st.session_state.expander_open):
    if st.session_state.memory_loaded:
        past_outputs = get_recent_outputs()
        for agent, goal, output, time in past_outputs:
            st.markdown(f"**{agent}** @ {time[:19]}")   # truncate off microseconds
            st.markdown(f"**Goal:** {goal}")
            st.code(output, language="markdown")