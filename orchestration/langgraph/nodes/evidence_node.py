"""
EvidenceNode - Aggregates evidence from logs and metrics to create unified analysis.
"""

from typing import Dict, List, Any
from collections import Counter


def aggregate_evidence(logs_analysis: Dict[str, Any], 
                      metrics_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Combine evidence from both logs and metrics to create a unified view.
    
    Args:
        logs_analysis: Output from LogNode
        metrics_analysis: Output from MetricsNode
        
    Returns:
        Dictionary with aggregated evidence
    """
    # Get suspects from both sources
    logs_suspects = logs_analysis.get('suspected_services', [])
    metrics_candidates = metrics_analysis.get('top_candidates', [])
    
    # Score each suspect
    suspect_scores = Counter()
    
    # Weight from logs (based on error frequency)
    service_error_counts = logs_analysis.get('service_error_counts', {})
    max_errors = max(service_error_counts.values()) if service_error_counts else 1
    for service in logs_suspects[:3]:  # Top 3 from logs
        score = service_error_counts.get(service, 0) / max_errors
        suspect_scores[service] += score * 0.4  # 40% weight on log errors
    
    # Weight from metrics anomalies (based on combined score)
    anomaly_scores = metrics_analysis.get('anomaly_scores', {})
    max_anomaly = max(anomaly_scores.values()) if anomaly_scores else 1
    for service in metrics_candidates[:3]:  # Top 3 from metrics
        score = anomaly_scores.get(service, 0) / max(max_anomaly, 1)
        suspect_scores[service] += score * 0.6  # 60% weight on metrics anomalies
    
    # Get unique suspects
    all_suspects = list(set(logs_suspects + metrics_candidates))
    
    # Sort by combined score
    ranked_suspects = sorted(
        [(service, suspect_scores.get(service, 0)) for service in all_suspects],
        key=lambda x: x[1],
        reverse=True
    )
    
    # Collect supporting evidence for top suspects
    evidence_details = []
    
    for service, _ in ranked_suspects[:5]:  # Top 5 suspects
        evidence = {
            'service': service,
            'evidence_items': []
        }
        
        # Log evidence
        if service in service_error_counts:
            evidence['evidence_items'].append({
                'source': 'logs',
                'type': 'error_count',
                'value': service_error_counts[service]
            })
        
        # Metric evidence
        if service in anomaly_scores:
            evidence['evidence_items'].append({
                'source': 'metrics',
                'type': 'anomaly_score',
                'value': round(anomaly_scores[service], 3)
            })
        
        service_metrics = metrics_analysis.get('service_metrics', {}).get(service, {})
        if service_metrics:
            evidence['evidence_items'].append({
                'source': 'metrics',
                'type': 'latency_ms',
                'value': service_metrics.get('latency_ms', 0)
            })
            evidence['evidence_items'].append({
                'source': 'metrics',
                'type': 'error_rate',
                'value': round(service_metrics.get('error_rate', 0), 4)
            })
        
        evidence_details.append(evidence)
    
    # Identify error patterns from logs
    error_patterns = logs_analysis.get('error_patterns', {})
    
    # Get error cascade information
    error_cascade = logs_analysis.get('error_cascade', [])
    cascade_order = [e['service'] for e in error_cascade[:10]]  # First 10 errors
    
    return {
        'combined_candidates': [service for service, _ in ranked_suspects],
        'suspect_scores': {service: round(score, 3) for service, score in ranked_suspects},
        'evidence_details': evidence_details,
        'error_patterns': error_patterns,
        'error_cascade_order': cascade_order,
        'highest_latency': metrics_analysis.get('highest_latency_service'),
        'latency_outliers': metrics_analysis.get('latency_outliers', []),
        'error_outliers': metrics_analysis.get('error_outliers', []),
        'total_logs': logs_analysis.get('total_logs_analyzed', 0),
        'service_count': len(all_suspects)
    }


def evidence_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node function for EvidenceAggregator in LangGraph workflow.
    
    Args:
        state: InvestigationState dictionary (must have logs_analysis and metrics_analysis complete)
        
    Returns:
        Updated state with evidence field populated
    """
    logs_analysis = state.get('logs_analysis')
    metrics_analysis = state.get('metrics_analysis')
    
    if logs_analysis is None:
        raise ValueError("logs_analysis not found in state - log_node must run first")
    if metrics_analysis is None:
        raise ValueError("metrics_analysis not found in state - metrics_node must run first")
    
    evidence = aggregate_evidence(logs_analysis, metrics_analysis)
    
    return {
        **state,
        'evidence': evidence
    }
