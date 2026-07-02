from memory.retriever import JSONMemoryRetriever

retriever = JSONMemoryRetriever()

results = retriever.retrieve(
    "payment timeout due to retries"
)

for r in results:

    print("=" * 50)
    print("Score:", r["score"])
    print("Root Cause:",
          r["memory"]["root_cause"])
    print("Summary:")
    print(r["memory"]["summary"])