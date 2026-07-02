import json
from pathlib import Path
from typing import List, Dict


class MemoryLoader:
    """
    Loads memory datasets from disk.

    Current sources:
    - historical_incidents.json
    - poisoned_memory.json
    """

    def __init__(self, memory_dir: str = "memory"):
        self.memory_dir = Path(memory_dir)

    def _load_json(self, filename: str) -> List[Dict]:
        file_path = self.memory_dir / filename

        if not file_path.exists():
            raise FileNotFoundError(
                f"Memory file not found: {file_path}"
            )

        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_historical(self) -> List[Dict]:
        """
        Load historical incidents.
        """
        return self._load_json(
            "historical_incidents.json"
        )

    def load_poisoned(self) -> List[Dict]:
        """
        Load poisoned memory entries.
        """
        return self._load_json(
            "poisoned_memory.json"
        )

    def load_all(self) -> List[Dict]:
        """
        Combine historical + poisoned memory.
        """
        historical = self.load_historical()
        poisoned = self.load_poisoned()

        return historical + poisoned