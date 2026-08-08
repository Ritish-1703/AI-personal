import secrets_setup  # must be first — bridges Streamlit secrets → os.environ
import streamlit as st
from dotenv import load_dotenv

from agents.notes_agent import notes_agent
from database.notes import get_notes, delete_note
from database.memory import get_all_memories, delete_memory
from database.tasks import get_tasks, delete_task, complete_task

load_dotenv()

st.set_page_config(
    page_title="AI Personal Bot",
    page_icon="🤖",
    layout="wide",
)

# ── Session state ─────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SIDEBAR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with st.sidebar:
    st.title("🗂️ Bot Manager")

    col_r, col_c = st.columns(2)
    with col_r:
        if st.button("🔄 Refresh", use_container_width=True, key="sidebar_refresh"):
            st.rerun()
    with col_c:
        if st.button("🗑️ Clear chat", use_container_width=True, key="clear_chat"):
            st.session_state.messages = []
            st.rerun()

    st.divider()

    # ── Notes panel ───────────────────────────────────────────────────────
    notes = get_notes()
    with st.expander(f"📋 Notes  ({len(notes)})", expanded=True):
        if not notes:
            st.caption("No notes yet. Ask the bot to create one!")
        else:
            for note in notes:
                note_id, title, content = note[0], note[1], note[2]
                st.markdown(f"**[{note_id}] {title}**")
                st.caption(content[:120] + ("…" if len(content) > 120 else ""))
                if st.button(
                    "🗑️ Delete",
                    key=f"del_note_{note_id}",
                    use_container_width=True,
                ):
                    delete_note(note_id)
                    st.success(f"Note {note_id} deleted.")
                    st.rerun()
                st.markdown("---")

    # ── Memory panel ──────────────────────────────────────────────────────
    memories = get_all_memories()
    with st.expander(f"🧠 Memory  ({len(memories)})", expanded=False):
        if not memories:
            st.caption("Nothing remembered yet. Ask the bot to remember something!")
        else:
            for key, value in memories:
                col_kv, col_del = st.columns([4, 1])
                with col_kv:
                    st.markdown(f"**{key}:** {value}")
                with col_del:
                    if st.button("✕", key=f"del_mem_{key}", help=f"Forget {key}"):
                        delete_memory(key)
                        st.rerun()

    # ── Tasks panel ───────────────────────────────────────────────────────
    tasks = get_tasks(include_done=True)
    pending = sum(1 for t in tasks if not t[2])
    with st.expander(f"✅ Tasks  ({pending} pending)", expanded=False):
        if not tasks:
            st.caption("No tasks yet. Ask the bot to add a reminder!")
        else:
            for task_id, title, done, _ in tasks:
                col_t, col_done, col_del = st.columns([5, 1, 1])
                with col_t:
                    label = f"~~{title}~~" if done else title
                    st.markdown(f"**[{task_id}]** {label}")
                with col_done:
                    if not done:
                        if st.button("✔", key=f"done_task_{task_id}", help="Mark done"):
                            complete_task(task_id)
                            st.rerun()
                with col_del:
                    if st.button("✕", key=f"del_task_{task_id}", help="Delete task"):
                        delete_task(task_id)
                        st.rerun()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MAIN CHAT AREA
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.title("🤖 AI Personal Bot")
st.caption("Your personal Notes · Memory · Tasks assistant — powered by Groq & OpenRouter")

# Render conversation history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Chat input
user_input = st.chat_input("Ask me anything…")

if user_input:
    # Add and display user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # Full history → agent
    agent_messages = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
    ]

    try:
        with st.chat_message("assistant"):
            with st.spinner("Thinking…"):
                result = notes_agent.invoke({"messages": agent_messages})

        response = result["messages"][-1].content

        # Handle structured (list) content
        if isinstance(response, list):
            response = "".join(
                item.get("text", "")
                for item in response
                if isinstance(item, dict)
            )

        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.write(response)

        # Auto-refresh sidebar after agent modifies data
        st.rerun()

    except Exception as e:
        error_message = str(e)
        with st.chat_message("assistant"):
            if "429" in error_message or "quota" in error_message.lower() or "rate limit" in error_message.lower():
                msg = (
                    "⚠️ **API Rate Limit / Quota Exceeded**\n\n"
                    "The LLM provider returned a rate limit or quota error. "
                    "Please wait a moment and try again, or check your API key credits."
                )
                st.warning(msg)
                st.session_state.messages.append({"role": "assistant", "content": msg})
            elif "401" in error_message or "Invalid API Key" in error_message or "missing" in error_message.lower():
                msg = (
                    "⚠️ **Invalid or Missing API Key**\n\n"
                    "Please configure a valid API key in your **Streamlit Secrets**:\n"
                    "1. Click **Manage app** (bottom right) ➔ **Settings** ➔ **Secrets**\n"
                    "2. Add a valid Groq or OpenRouter key:\n"
                    "```toml\nGROQ_API_KEY = \"gsk_your_groq_key_here\"\n# OR\nOPENROUTER_API_KEY = \"sk-or-v1-your_openrouter_key_here\"\n```"
                )
                st.error(msg)
                st.session_state.messages.append({"role": "assistant", "content": msg})
            else:
                msg = f"⚠️ **Service Notice:**\n{error_message}"
                st.error(msg)
                st.session_state.messages.append({"role": "assistant", "content": msg})