from _paths import PROJECT_ROOT  # noqa: F401 — ensures repo root is on sys.path

from memory.loader import MemoryLoader

loader = MemoryLoader()

print("Historical:", len(loader.load_historical()))
print("Poisoned:", len(loader.load_poisoned()))
print("All:", len(loader.load_all()))
