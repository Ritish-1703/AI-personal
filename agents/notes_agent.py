import os

from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
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


def _get_api_keys():
    """Retrieve Groq and OpenRouter keys from env or st.secrets."""
    groq_key = os.getenv("GROQ_API_KEY") or os.getenv("GROQ") or os.getenv("groq_api_key")
    openrouter_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("openrouter_api_key")

    try:
        import streamlit as st
        if hasattr(st, "secrets"):
            if not groq_key:
                for k in ["GROQ_API_KEY", "GROQ", "groq_api_key"]:
                    if k in st.secrets and isinstance(st.secrets[k], str) and st.secrets[k].strip():
                        groq_key = st.secrets[k].strip()
                        break
            if not openrouter_key:
                for k in ["OPENROUTER_API_KEY", "openrouter_api_key"]:
                    if k in st.secrets and isinstance(st.secrets[k], str) and st.secrets[k].strip():
                        openrouter_key = st.secrets[k].strip()
                        break
            # Fallback scan for keys starting with gsk_ or sk-or-
            for k in st.secrets:
                val = st.secrets[k]
                if isinstance(val, str):
                    if not groq_key and (val.startswith("gsk_") or "GROQ" in k.upper()):
                        groq_key = val.strip()
                    elif not openrouter_key and (val.startswith("sk-or-") or "OPENROUTER" in k.upper()):
                        openrouter_key = val.strip()
    except Exception:
        pass

    return groq_key, openrouter_key


class DynamicNotesAgent:
    """Wrapper that tries Groq first, falls back to OpenRouter, and handles errors gracefully."""

    def invoke(self, input_data, config=None, **kwargs):
        groq_key, openrouter_key = _get_api_keys()

        tools = [
            create_note_tool,
            get_notes_tool,
            search_notes_tool,
            update_note_tool,
            delete_note_tool,
            save_memory_tool,
            get_memory_tool,
            get_all_memories_tool,
            delete_memory_tool,
            add_task_tool,
            get_tasks_tool,
            complete_task_tool,
            delete_task_tool,
        ]

        errors = []

        # 1. Try Groq if key exists
        if groq_key:
            try:
                llm = ChatGroq(
                    model="llama-3.3-70b-versatile",
                    api_key=groq_key,
                    temperature=0.3,
                )
                agent = create_react_agent(model=llm, tools=tools, prompt=SYSTEM_PROMPT)
                return agent.invoke(input_data, config=config, **kwargs)
            except Exception as e:
                errors.append(f"Groq API Error: {str(e)}")

        # 2. Try OpenRouter as fallback if key exists
        if openrouter_key:
            try:
                llm = ChatOpenAI(
                    model="openrouter/free",
                    api_key=openrouter_key,
                    base_url="https://openrouter.ai/api/v1",
                    temperature=0.3,
                )
                agent = create_react_agent(model=llm, tools=tools, prompt=SYSTEM_PROMPT)
                return agent.invoke(input_data, config=config, **kwargs)
            except Exception as e:
                errors.append(f"OpenRouter API Error: {str(e)}")

        # 3. If neither worked, raise informative error
        if not groq_key and not openrouter_key:
            raise ValueError(
                "No API Key found! Please add GROQ_API_KEY (gsk_...) or OPENROUTER_API_KEY in Streamlit Cloud Secrets (Manage app ➔ Settings ➔ Secrets)."
            )
        else:
            raise RuntimeError(
                "API Request Failed:\n" + "\n".join(errors) + "\n\nPlease check your API key validity or rate limit."
            )


notes_agent = DynamicNotesAgent()
