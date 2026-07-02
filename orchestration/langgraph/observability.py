"""
LangSmith observability helpers for the investigation workflow.
"""

import os
from functools import wraps
from typing import Any, Callable, Dict

from dotenv import load_dotenv


PIPELINE_VERSION = "phase-4-langsmith-trace-node"
PIPELINE_NODES = [
    "log_node",
    "metrics_node",
    "trace_node",
    "evidence_node",
    "rca_node",
]


def configure_langsmith() -> None:
    """
    Normalize LangSmith/LangChain tracing environment variables.
    """
    load_dotenv()

    if os.getenv("LANGCHAIN_TRACING_V2") and not os.getenv("LANGSMITH_TRACING_V2"):
        os.environ["LANGSMITH_TRACING_V2"] = os.getenv("LANGCHAIN_TRACING_V2", "")

    if os.getenv("LANGCHAIN_API_KEY") and not os.getenv("LANGSMITH_API_KEY"):
        os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGCHAIN_API_KEY", "")


def langsmith_enabled() -> bool:
    """
    Return whether tracing appears configured for LangSmith.
    """
    configure_langsmith()
    tracing_value = (
        os.getenv("LANGSMITH_TRACING_V2")
        or os.getenv("LANGCHAIN_TRACING_V2")
        or ""
    )
    return tracing_value.lower() == "true" and bool(
        os.getenv("LANGSMITH_API_KEY") or os.getenv("LANGCHAIN_API_KEY")
    )


def build_run_config(scenario: str, model: str = "gemini-2.5-flash") -> Dict[str, Any]:
    """
    Build LangGraph/LangSmith run metadata for the top-level workflow run.
    """
    configure_langsmith()
    return {
        "run_name": f"agent-investigator:{scenario}",
        "tags": [
            "agent-investigator",
            "langgraph",
            "phase-4",
            scenario,
        ],
        "metadata": {
            "scenario": scenario,
            "pipeline_version": PIPELINE_VERSION,
            "pipeline_nodes": PIPELINE_NODES,
            "model": model,
            "logs_enabled": True,
            "metrics_enabled": True,
            "traces_enabled": True,
            "rca_enabled": True,
        },
    }


def _summarize_state(state: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "scenario": state.get("scenario"),
        "dataset_path": state.get("dataset_path"),
        "has_logs_analysis": state.get("logs_analysis") is not None,
        "has_metrics_analysis": state.get("metrics_analysis") is not None,
        "has_trace_analysis": state.get("trace_analysis") is not None,
        "has_evidence": state.get("evidence") is not None,
        "has_rca_result": state.get("rca_result") is not None,
    }


def _summarize_outputs(output: Dict[str, Any]) -> Dict[str, Any]:
    summary = _summarize_state(output)

    logs_analysis = output.get("logs_analysis") or {}
    metrics_analysis = output.get("metrics_analysis") or {}
    trace_analysis = output.get("trace_analysis") or {}
    evidence = output.get("evidence") or {}
    rca_result = output.get("rca_result") or {}

    summary.update({
        "logs_analyzed": logs_analysis.get("total_logs_analyzed"),
        "metric_candidates": metrics_analysis.get("top_candidates"),
        "traces_analyzed": trace_analysis.get("total_traces_analyzed"),
        "trace_candidates": trace_analysis.get("top_trace_candidates"),
        "suspect_services": evidence.get("combined_candidates"),
        "root_cause": rca_result.get("root_cause"),
        "confidence": rca_result.get("confidence"),
    })
    return summary


def trace_langgraph_node(name: str) -> Callable[[Callable[..., Dict[str, Any]]], Callable[..., Dict[str, Any]]]:
    """
    Decorate a LangGraph node so it appears as a named LangSmith child run.
    """
    def decorator(func: Callable[..., Dict[str, Any]]) -> Callable[..., Dict[str, Any]]:
        try:
            from langsmith import traceable
        except ImportError:
            return func

        traced_func = traceable(
            run_type="chain",
            name=name,
            tags=["agent-investigator", "langgraph-node", name],
            metadata={
                "pipeline_version": PIPELINE_VERSION,
                "node": name,
            },
            process_inputs=lambda inputs: {
                "state": _summarize_state(inputs.get("state", {}))
            },
            process_outputs=_summarize_outputs,
        )(func)

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Dict[str, Any]:
            configure_langsmith()
            return traced_func(*args, **kwargs)

        return wrapper

    return decorator
