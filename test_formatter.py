from memory.retriever import JSONMemoryRetriever
from memory.formatter import MemoryFormatter

retriever = JSONMemoryRetriever()

memories = retriever.retrieve(
    "payment timeout due to retries"
)

print(
    MemoryFormatter.format(memories)
)