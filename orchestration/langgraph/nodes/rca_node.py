"""
RCANode - Performs root cause analysis using Gemini (Google Generative AI).

This module loads `GOOGLE_API_KEY` from a `.env` file (via python-dotenv) and
attempts to call Gemini (e.g., `gemini-2.5-flash` or `gemini-1.5-flash`) using
`google.generativeai`. If that client is not available it falls back to a
heuristic ranking based on anomaly scores.
"""

import json
import os
import warnings
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


def _get_api_key() -> str | None:
    """Resolve the Gemini API key from the supported environment variable names."""
    load_dotenv()
    return (
        os.getenv('GOOGLE_API_KEY')
        or os.getenv('GEMINI_API_KEY')
        or os.getenv('GOOGLE_GEMINI_API_KEY')
    )


def format_evidence_for_llm(evidence: Dict[str, Any], 
                            logs_analysis: Dict[str, Any],
                            metrics_analysis: Dict[str, Any]) -> str:
    """
    Format aggregated evidence into a structured prompt for the LLM (Gemini).
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


def _extract_gemini_text(response: Any) -> str:
    """
    Extract text from the response shapes returned by Google Gemini SDKs.
    """
    text = getattr(response, 'text', None)
    if text:
        return text

    parts = []
    for candidate in getattr(response, 'candidates', []) or []:
        content = getattr(candidate, 'content', None)
        for part in getattr(content, 'parts', []) or []:
            part_text = getattr(part, 'text', None)
            if part_text:
                parts.append(part_text)

    return ''.join(parts)


def _call_gemini(prompt_text: str, model: str, api_key: str | None = None) -> str:
    """
    Call Gemini using the installed Google Generative AI SDK.
    """
    resolved_api_key = api_key or _get_api_key()
    if not resolved_api_key:
        raise RuntimeError('GOOGLE_API_KEY not set in environment')

    with warnings.catch_warnings():
        warnings.simplefilter('ignore', FutureWarning)
        try:
            import google.generativeai as genai
        except ImportError:
            from google import genai as google_genai
            client = google_genai.Client(api_key=resolved_api_key)
            response = client.models.generate_content(
                model=model,
                contents=prompt_text,
            )
            return _extract_gemini_text(response)

    genai.configure(api_key=resolved_api_key)
    gemini_model = genai.GenerativeModel(model)
    response = gemini_model.generate_content(prompt_text)
    return _extract_gemini_text(response)


def _format_gemini_error(error: Exception) -> str:
    """
    Keep report reasoning readable while preserving the actionable failure.
    """
    message = str(error)
    if 'API_KEY_INVALID' in message or 'API key not valid' in message:
        return 'invalid GOOGLE_API_KEY'
    if 'GOOGLE_API_KEY not set' in message:
        return 'GOOGLE_API_KEY not set in environment'
    return message


def perform_rca(evidence: Dict[str, Any],
                logs_analysis: Dict[str, Any],
                metrics_analysis: Dict[str, Any],
                model: str = 'gemini-2.5-flash') -> Dict[str, Any]:
    """
    Perform root cause analysis using Google Gemini. Defaults to `gemini-2.5-flash`.

    If the `google.generativeai` client is available and `GOOGLE_API_KEY` is set,
    the function will call Gemini. Otherwise it will fall back to a heuristic.
    """
    prompt_text = format_evidence_for_llm(evidence, logs_analysis, metrics_analysis)

    # Try to call Google Generative AI (Gemini)
    try:
        response_text = _call_gemini(prompt_text, model, _get_api_key())

        if not response_text:
            raise RuntimeError('Empty response from Gemini')

        rca_result = parse_rca_response(response_text)
        return rca_result

    except Exception as e:
        # Fallback: use heuristic-based RCA
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
            'reasoning': f'Gemini call failed ({_format_gemini_error(e)}). Using heuristic ranking: highest anomaly score.',
            'supporting_evidence': evidence.get('evidence_details', [])[:3],
            'affected_services': evidence.get('error_cascade_order', [])
        }


def rca_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node function for RCAAgent in LangGraph workflow.
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
