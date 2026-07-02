from memory.retriever import JSONMemoryRetriever
from memory.formatter import MemoryFormatter


class MemoryNode:
    """
    Retrieves relevant historical memories based on the
    current evidence summary and stores a formatted context
    in the LangGraph state.
    """

    def __init__(self):
        self.retriever = JSONMemoryRetriever()

    def __call__(self, state):

        # Get the evidence produced by EvidenceNode
        evidence = state.get("evidence", {})

        # Build a search query
        query = ""

        if isinstance(evidence, dict):

            if "combined_summary" in evidence:
                query = evidence["combined_summary"]

            elif "summary" in evidence:
                query = evidence["summary"]

            else:
                query = str(evidence)

        else:
            query = str(evidence)

        # Retrieve relevant memories
        retrieved = self.retriever.retrieve(
            query=query,
            top_k=3
        )

        # Convert them into LLM-friendly text
        formatted_context = MemoryFormatter.format(
            retrieved
        )

        # Store in graph state
        state["memory_context"] = formatted_context

        return state