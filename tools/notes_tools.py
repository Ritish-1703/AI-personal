from langchain_core.tools import tool

from database.notes import (
    create_note,
    get_notes,
    search_notes,
    update_note,
    delete_note,
)


@tool
def create_note_tool(title: str, content: str) -> str:
    """Create and save a personal note with a title and content."""

    note_id = create_note(title, content)

    return f"Note created successfully. Note ID: {note_id}"


@tool
def get_notes_tool() -> str:
    """Get all saved personal notes."""

    notes = get_notes()

    if not notes:
        return "No notes found."

    return "\n".join(
        f"ID: {note[0]} | Title: {note[1]} | Content: {note[2]}"
        for note in notes
    )


@tool
def search_notes_tool(keyword: str) -> str:
    """Search personal notes by keyword in the title or content."""

    notes = search_notes(keyword)

    if not notes:
        return f"No notes found for '{keyword}'."

    return "\n".join(
        f"ID: {note[0]} | Title: {note[1]} | Content: {note[2]}"
        for note in notes
    )


@tool
def update_note_tool(note_id: int, title: str, content: str) -> str:
    """Update an existing personal note using its note ID."""

    updated = update_note(note_id, title, content)

    if updated:
        return f"Note {note_id} updated successfully."

    return f"Note {note_id} was not found."


@tool
def delete_note_tool(note_id: int) -> str:
    """Delete a personal note using its note ID."""

    deleted = delete_note(note_id)

    if deleted:
        return f"Note {note_id} deleted successfully."

    return f"Note {note_id} was not found."