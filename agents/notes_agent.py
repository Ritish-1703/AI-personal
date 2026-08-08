import os

from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

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

def _resolve_api_key() -> str:
    key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not key:
        try:
            import streamlit as st
            if hasattr(st, "secrets"):
                key = st.secrets.get("OPENROUTER_API_KEY") or st.secrets.get("OPENAI_API_KEY")
        except Exception:
            pass
    if not key:
        raise ValueError(
            "OPENROUTER_API_KEY is missing! Please add OPENROUTER_API_KEY to your Streamlit Cloud Secrets or local .env file."
        )
    return key


class DynamicNotesAgent:
    """Wrapper that resolves the API key and initializes the agent dynamically per request."""

    def invoke(self, input_data, config=None, **kwargs):
        api_key = _resolve_api_key()

        llm = ChatOpenAI(
            model="openrouter/free",
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
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
