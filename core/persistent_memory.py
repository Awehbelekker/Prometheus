import json
from typing import Any, Dict

class PersistentMemory:
    """
    Simple persistent memory for agent learning and experience.
    """
    def __init__(self, filepath: str = "memory.json"):
        self.filepath = filepath
        self.memory: Dict[str, Any] = self.load()

    def load(self) -> Dict[str, Any]:
        try:
            with open(self.filepath, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save(self):
        with open(self.filepath, "w") as f:
            json.dump(self.memory, f, indent=2)

    def get(self, key: str, default=None):
        return self.memory.get(key, default)

    def set(self, key: str, value: Any):
        self.memory[key] = value
        self.save()
