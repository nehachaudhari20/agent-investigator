"""
InvestigationState - Shared state for LangGraph investigation workflow.

Tracks the progression of RCA analysis through each node.
"""

from typing import TypedDict, Optional, List, Dict, Any


class InvestigationState(TypedDict):
    """
    Shared state passed through the investigation workflow.
    
    Fields:
        scenario: The incident scenario name (e.g., 'retry_storm')
        dataset_path: Path to the dataset directory containing logs/metrics/traces
        logs_analysis: Output from LogNode analyzing logs.json
        metrics_analysis: Output from MetricsNode analyzing metrics.json
        evidence: Combined evidence from both logs and metrics
        rca_result: Final RCA output with root_cause, confidence, reasoning
    """
    scenario: str
    dataset_path: str
    logs_analysis: Optional[Dict[str, Any]]
    metrics_analysis: Optional[Dict[str, Any]]
    trace_analysis: Optional[Dict[str, Any]]
    evidence: Optional[Dict[str, Any]]
    rca_result: Optional[Dict[str, Any]]

