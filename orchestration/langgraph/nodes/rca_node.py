"""
RCANode - Performs root cause analysis using LLM with evidence from logs and metrics.
"""

import json
from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage


def format_evidence_for_llm(evidence: Dict[str, Any], 
                            logs_analysis: Dict[str, Any],
                            metrics_analysis: Dict[str, Any]) -> str:
    """
    Format aggregated evidence into a structured prompt for the LLM.
    
    Args:
        evidence: Aggregated evidence from evidence_node
        logs_analysis: Original logs analysis
        metrics_analysis: Original metrics analysis
        
    Returns:
        Formatted prompt string
    """
    prompt = """You are an expert SRE investigating a production incident. 

## INCIDENT DATA

### Error Cascade (in order):
"""
    
    for i, service in enumerate(evidence.get('error_cascade_order', [])[:5], 1):
        prompt += f"{i}. {service}\n"
    
    prompt += "\n### Service Metrics (latency & error rates):\n"
    for service, metrics in metrics_analysis.get('service_metrics', {}).items():
        prompt += f"- {service}: {metrics['latency_ms']}ms latency, {metrics['error_rate']:.4f} error rate\n"
    
    prompt += "\n### Evidence Summary:\n"
    for service_evidence in evidence.get('evidence_details', [])[:5]:
        service = service_evidence['service']
        prompt += f"\n**{service}**:\n"
        for item in service_evidence.get('evidence_items', [])[:3]:
            prompt += f"  - {item['source']}: {item['type']} = {item['value']}\n"
    
    prompt += "\n### Error Patterns Detected:\n"
    for pattern, count in evidence.get('error_patterns', {}).items():
        if count > 0:
            prompt += f"- {pattern}: {count} occurrences\n"
    
    prompt += f"\n### Highest Latency Service: {evidence.get('highest_latency')}\n"
    
    prompt += f"\n### Latency Outliers (>1.5x average): {', '.join(evidence.get('latency_outliers', []) or ['none'])}\n"
    
    prompt += f"\n### Services Ranked by Anomaly Score:\n"
    for service, score in list(evidence.get('suspect_scores', {}).items())[:5]:
        prompt += f"- {service}: {score:.3f}\n"
    
    prompt += """
## TASK

Based on the incident data above, provide your root cause analysis:

1. **Root Cause Service**: Which service is the PRIMARY ROOT CAUSE?
2. **Confidence**: How confident are you (0.0-1.0)?
3. **Reasoning**: Why? Reference the specific evidence.
4. **Supporting Evidence**: List 2-3 key data points.
5. **Affected Services**: Which services were impacted by this root cause?

IMPORTANT: Use only evidence provided. Do not speculate.

Respond in JSON format ONLY:
```json
{
    "root_cause": "service-name",
    "confidence": 0.85,
    "reasoning": "...",
    "supporting_evidence": ["item1", "item2", "item3"],
    "affected_services": ["service1", "service2"]
}
```
"""
    
    return prompt


def parse_rca_response(response_text: str) -> Dict[str, Any]:
    """
    Parse LLM response to extract JSON RCA result.
    
    Args:
        response_text: Raw text response from LLM
        
    Returns:
        Parsed RCA result dictionary
    """
    try:
        # Try to extract JSON from response
        if '```json' in response_text:
            json_str = response_text.split('```json')[1].split('```')[0].strip()
        elif '```' in response_text:
            json_str = response_text.split('```')[1].split('```')[0].strip()
        else:
            json_str = response_text
        
        result = json.loads(json_str)
        return result
    except (json.JSONDecodeError, IndexError) as e:
        # Fallback if parsing fails
        return {
            'root_cause': 'unknown',
            'confidence': 0.0,
            'reasoning': f'Failed to parse LLM response: {response_text[:200]}',
            'supporting_evidence': [],
            'affected_services': []
        }


def perform_rca(evidence: Dict[str, Any],
                logs_analysis: Dict[str, Any],
                metrics_analysis: Dict[str, Any],
                model: str = 'gpt-4o-mini') -> Dict[str, Any]:
    """
    Perform root cause analysis using LLM.
    
    Args:
        evidence: Aggregated evidence from evidence_node
        logs_analysis: Original logs analysis
        metrics_analysis: Original metrics analysis
        model: LLM model to use (default: gpt-4o-mini for cost efficiency)
        
    Returns:
        RCA result with root_cause, confidence, reasoning, evidence
    """
    try:
        # Initialize LLM
        llm = ChatOpenAI(model=model, temperature=0)
        
        # Format prompt
        prompt_text = format_evidence_for_llm(evidence, logs_analysis, metrics_analysis)
        
        # Call LLM
        message = HumanMessage(content=prompt_text)
        response = llm.invoke([message])
        
        # Parse response
        rca_result = parse_rca_response(response.content)
        
        return rca_result
    
    except Exception as e:
        # Fallback: use heuristic-based RCA if LLM fails
        combined_candidates = evidence.get('combined_candidates', [])
        suspect_scores = evidence.get('suspect_scores', {})
        
        if combined_candidates:
            root_cause = combined_candidates[0]
            confidence = suspect_scores.get(root_cause, 0.5)
        else:
            root_cause = 'unknown'
            confidence = 0.0
        
        return {
            'root_cause': root_cause,
            'confidence': float(confidence),
            'reasoning': f'LLM call failed ({str(e)}). Using heuristic ranking: highest anomaly score.',
            'supporting_evidence': evidence.get('evidence_details', [])[:3],
            'affected_services': evidence.get('error_cascade_order', [])
        }


def rca_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node function for RCAAgent in LangGraph workflow.
    
    Args:
        state: InvestigationState dictionary (must have evidence complete)
        
    Returns:
        Updated state with rca_result field populated
    """
    evidence = state.get('evidence')
    logs_analysis = state.get('logs_analysis')
    metrics_analysis = state.get('metrics_analysis')
    
    if evidence is None:
        raise ValueError("evidence not found in state - evidence_node must run first")
    if logs_analysis is None:
        raise ValueError("logs_analysis not found in state - log_node must run first")
    if metrics_analysis is None:
        raise ValueError("metrics_analysis not found in state - metrics_node must run first")
    
    # Perform RCA
    rca_result = perform_rca(evidence, logs_analysis, metrics_analysis)
    
    return {
        **state,
        'rca_result': rca_result
    }
