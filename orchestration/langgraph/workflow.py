"""
Investigation Workflow - LangGraph-based RCA pipeline.

Orchestrates the investigation workflow:
START → LogNode → MetricsNode → EvidenceNode → RCANode → END
"""

from pathlib import Path
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from .state import InvestigationState
from .nodes.log_node import log_node
from .nodes.metrics_node import metrics_node
from .nodes.evidence_node import evidence_node
from .nodes.rca_node import rca_node
from .nodes.trace_node import trace_node
from .observability import (
    PIPELINE_VERSION,
    build_run_config,
    configure_langsmith,
    langsmith_enabled,
)

def create_investigation_graph() -> StateGraph:
    """
    Create and configure the LangGraph workflow for incident investigation.
    
    Returns:
        Compiled StateGraph ready for invocation
    """
    configure_langsmith()

    # Create the graph
    workflow = StateGraph(InvestigationState)
    
    # Add nodes
    workflow.add_node("log_node", log_node)
    workflow.add_node("metrics_node", metrics_node)
    workflow.add_node("evidence_node", evidence_node)
    workflow.add_node("rca_node", rca_node)
    workflow.add_node("trace_node", trace_node)
    
    # Add edges (deterministic flow)
    workflow.set_entry_point("log_node")
    workflow.add_edge("log_node", "metrics_node")
    workflow.add_edge("metrics_node", "trace_node")
    workflow.add_edge("trace_node", "evidence_node")
    workflow.add_edge("evidence_node", "rca_node")
    workflow.add_edge("rca_node", END)
    
    # Compile
    graph = workflow.compile()
    
    return graph


def run_investigation(scenario: str, dataset_base_path: str = "datasets") -> Dict[str, Any]:
    """
    Execute the investigation workflow for a given scenario.
    
    Args:
        scenario: Scenario name (e.g., 'retry_storm', 'misleading_logs', 'memory_poisoning')
        dataset_base_path: Base path where datasets are located
        
    Returns:
        Final InvestigationState with complete RCA results
    """
    # Validate scenario
    dataset_path = Path(dataset_base_path) / scenario
    if not dataset_path.exists():
        raise ValueError(f"Dataset path not found: {dataset_path}")
    
    # Create initial state
    initial_state = InvestigationState(
        scenario=scenario,
        dataset_path=str(dataset_path),
        logs_analysis=None,
        metrics_analysis=None,
        evidence=None,
        rca_result=None,
        trace_analysis=None,
        
    )
    
    # Create and run graph
    graph = create_investigation_graph()
    final_state = graph.invoke(initial_state, config=build_run_config(scenario))
    
    return final_state


def format_results(final_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format final state into investigation report.
    
    Args:
        final_state: Final InvestigationState from workflow
        
    Returns:
        Formatted investigation report
    """
    rca_result = final_state.get('rca_result', {})
    evidence = final_state.get('evidence', {})
    
    report = {
        'scenario': final_state.get('scenario'),
        'root_cause': rca_result.get('root_cause', 'unknown'),
        'confidence': rca_result.get('confidence', 0.0),
        'reasoning': rca_result.get('reasoning', ''),
        'supporting_evidence': rca_result.get('supporting_evidence', []),
        'affected_services': rca_result.get('affected_services', []),
        'suspect_services': evidence.get('combined_candidates', []),
        'suspect_scores': evidence.get('suspect_scores', {}),
        'error_patterns': evidence.get('error_patterns', {}),
        'analysis_details': {
            'logs_analyzed': final_state.get('logs_analysis', {}).get('total_logs_analyzed', 0),
            'services_evaluated': evidence.get('service_count', 0),
            'latency_outliers': evidence.get('latency_outliers', []),
            'error_outliers': evidence.get('error_outliers', []),
            'traces_analyzed': final_state.get('trace_analysis', {}).get('total_traces_analyzed', 0),
            'trace_candidates': evidence.get('trace_candidates', []),
            'pipeline_version': PIPELINE_VERSION,
            'langsmith_tracing_configured': langsmith_enabled(),
        }
    }
    
    return report
