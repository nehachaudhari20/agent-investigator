"""
MetricsNode - Analyzes metrics.json to identify latency and error rate anomalies.
"""

import json
from pathlib import Path
from typing import Dict, List, Any


def analyze_metrics(metrics_path: Path) -> Dict[str, Any]:
    """
    Analyze metrics.json to extract:
    - Service latencies (identify outliers)
    - Error rates (identify anomalies)
    - Candidate root cause services
    
    Args:
        metrics_path: Path to metrics.json file
        
    Returns:
        Dictionary with analysis results
    """
    with open(metrics_path, 'r') as f:
        metrics = json.load(f)
    
    # Extract metrics by service
    service_metrics = {}
    latencies = []
    error_rates = []
    
    for metric in metrics:
        service = metric.get('service', 'unknown')
        latency = metric.get('latency_ms', 0)
        error_rate = metric.get('error_rate', 0)
        
        service_metrics[service] = {
            'latency_ms': latency,
            'error_rate': error_rate
        }
        latencies.append(latency)
        error_rates.append(error_rate)
    
    # Calculate statistics
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    max_latency = max(latencies) if latencies else 0
    min_latency = min(latencies) if latencies else 0
    
    avg_error_rate = sum(error_rates) / len(error_rates) if error_rates else 0
    max_error_rate = max(error_rates) if error_rates else 0
    
    # Identify latency outliers (> 1.5x average)
    latency_threshold = avg_latency * 1.5
    latency_outliers = [
        service for service, metrics_dict in service_metrics.items()
        if metrics_dict['latency_ms'] > latency_threshold
    ]
    
    # Identify error rate outliers (> 1.5x average)
    error_threshold = avg_error_rate * 1.5 if avg_error_rate > 0 else 0.1
    error_outliers = [
        service for service, metrics_dict in service_metrics.items()
        if metrics_dict['error_rate'] > error_threshold
    ]
    
    # Rank services by combined anomaly score
    service_scores = {}
    for service, metrics_dict in service_metrics.items():
        latency_score = (metrics_dict['latency_ms'] - min_latency) / (max_latency - min_latency + 1)
        error_score = metrics_dict['error_rate'] / (max_error_rate + 0.001)
        combined_score = 0.6 * latency_score + 0.4 * error_score
        service_scores[service] = combined_score
    
    # Rank services by anomaly score
    ranked_services = sorted(
        service_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    top_candidates = [service for service, _ in ranked_services[:3]]
    highest_latency_service = max(
        service_metrics.items(),
        key=lambda x: x[1]['latency_ms']
    )[0]
    
    return {
        'service_metrics': service_metrics,
        'highest_latency_service': highest_latency_service,
        'top_candidates': top_candidates,
        'latency_outliers': latency_outliers,
        'error_outliers': error_outliers,
        'statistics': {
            'avg_latency_ms': round(avg_latency, 2),
            'max_latency_ms': max_latency,
            'min_latency_ms': min_latency,
            'avg_error_rate': round(avg_error_rate, 4),
            'max_error_rate': round(max_error_rate, 4)
        },
        'anomaly_scores': {service: round(score, 3) for service, score in ranked_services}
    }


def metrics_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node function for MetricsAgent in LangGraph workflow.
    
    Args:
        state: InvestigationState dictionary (must have logs_analysis complete)
        
    Returns:
        Updated state with metrics_analysis field populated
    """
    dataset_path = Path(state['dataset_path'])
    metrics_path = dataset_path / 'metrics.json'
    
    if not metrics_path.exists():
        raise FileNotFoundError(f"Metrics file not found at {metrics_path}")
    
    metrics_analysis = analyze_metrics(metrics_path)
    
    return {
        **state,
        'metrics_analysis': metrics_analysis
    }
