"""
LogNode - Analyzes logs.json to identify error patterns and suspect services.
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict, Counter


def analyze_logs(logs_path: Path) -> Dict[str, Any]:
    """
    Analyze logs.json to extract:
    - Error patterns (timeouts, retries, etc.)
    - Services mentioned in errors
    - Temporal ordering of failure cascade
    
    Args:
        logs_path: Path to logs.json file
        
    Returns:
        Dictionary with analysis results
    """
    with open(logs_path, 'r') as f:
        logs = json.load(f)
    
    # Track error messages by service
    service_errors = defaultdict(list)
    error_patterns = Counter()
    error_by_level = defaultdict(list)
    
    # Track cascade order (first service to show error)
    first_error_time = None
    error_cascade = []
    
    for log_entry in logs:
        service = log_entry.get('service', 'unknown')
        level = log_entry.get('level', 'INFO')
        message = log_entry.get('message', '')
        timestamp = log_entry.get('timestamp', '')
        
        # Only track ERROR and WARN
        if level in ['ERROR', 'WARN']:
            service_errors[service].append({
                'level': level,
                'message': message,
                'timestamp': timestamp
            })
            error_by_level[level].append(service)
            
            # Extract error patterns
            if 'timeout' in message.lower():
                error_patterns['timeout'] += 1
            if 'retry' in message.lower():
                error_patterns['retry'] += 1
            if 'unavailable' in message.lower():
                error_patterns['unavailable'] += 1
            if 'delayed' in message.lower():
                error_patterns['delayed'] += 1
            
            # Track cascade
            if first_error_time is None:
                first_error_time = timestamp
            error_cascade.append({
                'service': service,
                'timestamp': timestamp,
                'message': message
            })
    
    # Identify most problematic services by error count
    service_error_counts = {
        service: len(errors) 
        for service, errors in service_errors.items()
    }
    
    suspected_services = sorted(
        service_error_counts.keys(),
        key=lambda x: service_error_counts[x],
        reverse=True
    )
    
    return {
        'suspected_services': suspected_services,
        'service_error_counts': service_error_counts,
        'error_patterns': dict(error_patterns),
        'error_cascade': error_cascade,
        'service_errors': {
            k: len(v) for k, v in service_errors.items()
        },
        'error_levels_distribution': {
            level: [s for s in services] 
            for level, services in error_by_level.items()
        },
        'total_logs_analyzed': len(logs)
    }


def log_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node function for LogAgent in LangGraph workflow.
    
    Args:
        state: InvestigationState dictionary
        
    Returns:
        Updated state with logs_analysis field populated
    """
    dataset_path = Path(state['dataset_path'])
    logs_path = dataset_path / 'logs.json'
    
    if not logs_path.exists():
        raise FileNotFoundError(f"Logs file not found at {logs_path}")
    
    logs_analysis = analyze_logs(logs_path)
    
    return {
        **state,
        'logs_analysis': logs_analysis
    }
