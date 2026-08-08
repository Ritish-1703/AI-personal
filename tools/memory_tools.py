from langchain_core.tools import tool

from database.memory import save_memory, get_memory, get_all_memories, delete_memory


@tool
def save_memory_tool(key: str, value: str) -> str:
    """
    Save an important piece of information about the user to persistent storage.
    Use this when the user says things like:
    - "Remember that I use Java."
    - "My favorite language is Python."
    - "Remember my college is MIT."
    - "Save that my name is Ritish."
    Choose a short, descriptive key (e.g. 'language', 'college', 'name').
    """
    return save_memory(key, value)


@tool
def get_memory_tool(key: str) -> str:
    """
    Retrieve a saved piece of information about the user from persistent storage.
    Use this when the user asks about something that may have been saved, e.g.:
    - "What is my preferred language?"
    - "What do you know about my college?"
    - "What is my name?"
    """
    result = get_memory(key)
    if result is None:
        return f"No memory found for '{key}'."
    return result


@tool
def get_all_memories_tool() -> str:
    """
    Retrieve ALL saved memories about the user.
    Use this when the user asks:
    - "What do you remember about me?"
    - "Show everything you know about me."
    - "List my saved information."
    """
    rows = get_all_memories()
    if not rows:
        return "No memories saved yet."
    return "\n".join(f"{key}: {value}" for key, value in rows)


@tool
def delete_memory_tool(key: str) -> str:
    """
    Delete a saved piece of information about the user.
    Use when the user asks to forget something, e.g.:
    - "Forget my preferred language."
    - "Delete the memory for college."
    """
    deleted = delete_memory(key)
    if deleted:
        return f"Memory for '{key}' deleted."
    return f"No memory found for '{key}'."