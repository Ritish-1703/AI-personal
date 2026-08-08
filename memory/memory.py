memory = {}


def save_memory(key, value):
    memory[key] = value
    return f"Memory saved: {key} = {value}"


def get_memory(key):
    return memory.get(key)