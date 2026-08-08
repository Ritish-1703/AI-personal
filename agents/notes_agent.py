import os

from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq

from tools.notes_tools import (
    create_note_tool,
    get_notes_tool,
    search_notes_tool,
    update_note_tool,
    delete_note_tool,
)

from tools.memory_tools import (
    save_memory_tool,
    get_memory_tool,
    get_all_memories_tool,
    delete_memory_tool,
)

from tools.tasks_tools import (
    add_task_tool,
    get_tasks_tool,
    complete_task_tool,
    delete_task_tool,
)

load_dotenv()

SYSTEM_PROMPT = """
You are a personal AI assistant that manages Notes, Memory, and Tasks.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NOTES  (use notes tools)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Create a note   → create_note_tool
• Show all notes  → get_notes_tool
• Search notes    → search_notes_tool
• Update a note   → update_note_tool
• Delete a note   → delete_note_tool

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MEMORY  (use memory tools)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Triggers: "remember", "my name is", "I use", "my favorite", "save that"
• Save a fact      → save_memory_tool(key, value)
• Recall one fact  → get_memory_tool(key)
• Recall all facts → get_all_memories_tool()
• Forget a fact    → delete_memory_tool(key)

Key naming rules:
  "Remember that my preferred programming language is Java." → key="language", value="Java"
  "My name is Ritish."                                     → key="name",     value="Ritish"
  "Remember my college is MIT."                            → key="college",  value="MIT"

ALWAYS call a tool to save or retrieve — never claim you saved/retrieved without calling it.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TASKS / REMINDERS  (use task tools)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Triggers: "remind me", "add task", "to-do", "I need to", "show my tasks", "mark as done"
• Add a task        → add_task_tool(title)
• List tasks        → get_tasks_tool(include_done=True/False)
• Complete a task   → complete_task_tool(task_id)
• Delete a task     → delete_task_tool(task_id)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Always call the appropriate tool — never make up results.
• Keep responses concise and friendly.
• If unsure which key to use for memory retrieval, try the most obvious one
  (e.g. "language", "name", "college"). If not found, say so and ask the user
  to rephrase or use get_all_memories_tool to show everything saved.
"""


def _resolve_groq_api_key() -> str:
    # 1. Check environment variables
    for env_var in ["GROQ_API_KEY", "groq_api_key", "OPENROUTER_API_KEY", "OPENAI_API_KEY"]:
        val = os.getenv(env_var)
        if val and val.strip():
            return val.strip()

    # 2. Check Streamlit secrets
    try:
        import streamlit as st
        if hasattr(st, "secrets"):
            for secret_key in ["GROQ_API_KEY", "groq_api_key", "OPENROUTER_API_KEY", "OPENAI_API_KEY"]:
                if secret_key in st.secrets and isinstance(st.secrets[secret_key], str):
                    val = st.secrets[secret_key].strip()
                    if val:
                        return val
            # Fuzzy match any secret key containing GROQ or API_KEY
            for k in st.secrets:
                if "GROQ" in k.upper() or "API_KEY" in k.upper():
                    val = st.secrets[k]
                    if isinstance(val, str) and val.strip():
                        return val.strip()
    except Exception:
        pass

    raise ValueError(
        "GROQ_API_KEY is not configured!\n"
        "Please add GROQ_API_KEY to your Streamlit Cloud Secrets or local .env file:\n"
        "GROQ_API_KEY = \"gsk_...\""
    )


class DynamicNotesAgent:
    """Wrapper that resolves the Groq API key and initializes the agent dynamically per request."""

    def invoke(self, input_data, config=None, **kwargs):
        api_key = _resolve_groq_api_key()

        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=api_key,
            temperature=0.3,
        )

        agent = create_react_agent(
            model=llm,
            tools=[
                # Notes
                create_note_tool,
                get_notes_tool,
                search_notes_tool,
                update_note_tool,
                delete_note_tool,
                # Memory
                save_memory_tool,
                get_memory_tool,
                get_all_memories_tool,
                delete_memory_tool,
                # Tasks
                add_task_tool,
                get_tasks_tool,
                complete_task_tool,
                delete_task_tool,
            ],
            prompt=SYSTEM_PROMPT,
        )

        return agent.invoke(input_data, config=config, **kwargs)


notes_agent = DynamicNotesAgent()
