from _paths import PROJECT_ROOT  # noqa: F401 — ensures repo root is on sys.path

from orchestration.langgraph.nodes.memory_node import MemoryNode

state = {
    "evidence": {
        "combined_summary": "payment timeout caused by retry storm and gateway latency"
    }
}

node = MemoryNode()

updated = node(state)

print(updated["memory_context"])
