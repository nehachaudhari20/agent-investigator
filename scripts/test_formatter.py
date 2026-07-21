from _paths import PROJECT_ROOT  # noqa: F401 — ensures repo root is on sys.path

from memory.formatter import MemoryFormatter
from memory.retriever import JSONMemoryRetriever

retriever = JSONMemoryRetriever()

memories = retriever.retrieve("payment timeout due to retries")

print(MemoryFormatter.format(memories))
