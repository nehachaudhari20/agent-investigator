from typing import List, Dict
from difflib import SequenceMatcher

from memory.base import BaseMemoryRetriever
from memory.loader import MemoryLoader


class JSONMemoryRetriever(BaseMemoryRetriever):
    """
    Simple JSON-based memory retriever.

    Uses lightweight text similarity for retrieval.

    Later this class can be replaced with
    TencentDB-Agent-Memory without changing
    the LangGraph workflow.
    """

    def __init__(self):
        self.loader = MemoryLoader()
        self.memories = self.loader.load_all()

    def _similarity(
        self,
        text1: str,
        text2: str
    ) -> float:

        return SequenceMatcher(
            None,
            text1.lower(),
            text2.lower()
        ).ratio()

    def retrieve(
        self,
        query: str,
        top_k: int = 3
    ) -> List[Dict]:

        ranked = []

        for memory in self.memories:

            searchable_text = " ".join([

                memory.get("title", ""),

                memory.get("summary", ""),

                memory.get("root_cause", "")

            ])

            score = self._similarity(
                query,
                searchable_text
            )

            ranked.append({

                "score": round(score, 3),

                "memory": memory

            })

        ranked.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        return ranked[:top_k]