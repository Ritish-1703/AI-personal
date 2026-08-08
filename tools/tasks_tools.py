from langchain_core.tools import tool

from database.tasks import add_task, get_tasks, complete_task, delete_task


@tool
def add_task_tool(title: str) -> str:
    """
    Add a new task or reminder for the user.
    Use when the user says things like:
    - "Remind me to practice Java tomorrow."
    - "Add a task: buy groceries."
    - "I need to call the bank."
    - "Add to my to-do list: finish the project."
    """
    task_id = add_task(title)
    return f"Task added: '{title}' (ID: {task_id})"


@tool
def get_tasks_tool(include_done: bool = True) -> str:
    """
    List the user's tasks/reminders.
    Use when the user says:
    - "Show my tasks."
    - "What are my reminders?"
    - "What do I need to do?"
    - "List my to-do items."
    Set include_done=False to show only pending tasks.
    """
    tasks = get_tasks(include_done=include_done)
    if not tasks:
        return "No tasks found."

    lines = []
    for task_id, title, done, created_at in tasks:
        status = "✅" if done else "⏳"
        lines.append(f"{status} [{task_id}] {title}")
    return "\n".join(lines)


@tool
def complete_task_tool(task_id: int) -> str:
    """
    Mark a task as completed.
    Use when the user says things like:
    - "Mark task 3 as done."
    - "I completed the Java practice task."
    - "Mark Java practice as completed." (find the ID from the task list first)
    """
    updated = complete_task(task_id)
    if updated:
        return f"Task {task_id} marked as completed."
    return f"Task {task_id} not found."


@tool
def delete_task_tool(task_id: int) -> str:
    """
    Delete a task permanently.
    Use when the user says:
    - "Delete task 3."
    - "Remove that reminder."
    """
    deleted = delete_task(task_id)
    if deleted:
        return f"Task {task_id} deleted."
    return f"Task {task_id} not found."
