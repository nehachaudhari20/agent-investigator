"""
TraceNode - Analyzes traces.json to identify service paths and downstream dependencies.
"""

import json
from pathlib import Path
from typing import Dict, Any
from collections import Counter, defaultdict


def analyze_traces(traces_path: Path) -> Dict[str, Any]:
    """
    Analyze traces.json to extract service path frequency, terminal services,
    and dependency edges.
    """
    with open(traces_path, 'r') as f:
        traces = json.load(f)

    service_counts = Counter()
    terminal_service_counts = Counter()
    edge_counts = Counter()
    path_counts = Counter()
    downstream_services = defaultdict(set)

    for trace in traces:
        path = trace.get('path', [])
        if not path:
            continue

        path_counts[tuple(path)] += 1
        terminal_service_counts[path[-1]] += 1

        for service in path:
            service_counts[service] += 1

        for source, target in zip(path, path[1:]):
            edge_counts[(source, target)] += 1
            downstream_services[source].add(target)

    ranked_services = service_counts.most_common()
    ranked_terminal_services = terminal_service_counts.most_common()
    ranked_edges = edge_counts.most_common()

    trace_suspects = [
        service for service, _ in ranked_terminal_services[:3]
    ]

    return {
        'total_traces_analyzed': len(traces),
        'service_trace_counts': dict(service_counts),
        'terminal_service_counts': dict(terminal_service_counts),
        'top_trace_candidates': trace_suspects,
        'most_common_paths': [
            {
                'path': list(path),
                'count': count
            }
            for path, count in path_counts.most_common(5)
        ],
        'dependency_edges': [
            {
                'source': source,
                'target': target,
                'count': count
            }
            for (source, target), count in ranked_edges
        ],
        'downstream_services': {
            service: sorted(list(children))
            for service, children in downstream_services.items()
        }
    }


def trace_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node function for trace analysis.
    """
    dataset_path = Path(state['dataset_path'])
    traces_path = dataset_path / 'traces.json'

    if not traces_path.exists():
        raise FileNotFoundError(f"Traces file not found at {traces_path}")

    trace_analysis = analyze_traces(traces_path)

    return {
        **state,
        'trace_analysis': trace_analysis
    }
