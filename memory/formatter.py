from typing import List, Dict


class MemoryFormatter:
    """
    Formats retrieved memories into a prompt-friendly string.
    """

    @staticmethod
    def format(memories: List[Dict]) -> str:

        if not memories:
            return "No relevant historical memories found."

        sections = [
            "Retrieved Historical Context\n"
        ]

        for idx, item in enumerate(memories, start=1):

            score = item["score"]
            memory = item["memory"]

            sections.append(
                f"""
Memory {idx}
Similarity Score: {score}

Title:
{memory.get("title", "N/A")}

Summary:
{memory.get("summary", "N/A")}

Historical Root Cause:
{memory.get("root_cause", "Unknown")}

Severity:
{memory.get("severity", "Unknown")}
""".strip()
            )

        return "\n\n" + ("\n\n" + "-" * 60 + "\n\n").join(sections)