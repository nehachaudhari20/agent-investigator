from abc import ABC, abstractmethod
from typing import List, Dict


class BaseMemoryRetriever(ABC):
    """
    Abstract interface for all memory retrieval backends.

    Implementations:
    - JSONMemoryRetriever
    - TencentMemoryRetriever
    - Future vector DBs
    """

    @abstractmethod
    def retrieve(
        self,
        query: str,
        top_k: int = 3
    ) -> List[Dict]:
        """
        Retrieve the most relevant historical memories.

        Args:
            query: Current incident summary.
            top_k: Number of memories to retrieve.

        Returns:
            List of memory records.
        """
        pass