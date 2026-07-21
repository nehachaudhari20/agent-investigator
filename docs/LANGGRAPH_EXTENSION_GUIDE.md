# LangGraph Workflow Extension Guide

Quick reference for extending Phase 3 workflow.

---

## How to Add a New Node

### 1. Create Node File

Create `orchestration/langgraph/nodes/new_node.py`:

```python
"""
NewNode - Description of what this node does.
"""

from typing import Dict, Any

def analyze_something(data_path):
    """
    Analyze data and extract insights.
    
    Returns:
        Dictionary with analysis results
    """
    # Your logic here
    return {
        'key1': value1,
        'key2': value2
    }

def new_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node function for LangGraph workflow.
    
    Args:
        state: InvestigationState dictionary
        
    Returns:
        Updated state with new field populated
    """
    result = analyze_something(...)
    
    return {
        **state,
        'new_field': result
    }
```

### 2. Update State

Edit `orchestration/langgraph/state.py`:

```python
class InvestigationState(TypedDict):
    # ... existing fields ...
    new_field: Optional[Dict[str, Any]]  # Add your new field
```

### 3. Update Workflow

Edit `orchestration/langgraph/workflow.py`:

```python
from .nodes.new_node import new_node

def create_investigation_graph():
    workflow = StateGraph(InvestigationState)
    
    # ... existing nodes ...
    workflow.add_node("new_node", new_node)
    
    # Add edges
    workflow.add_edge("evidence_node", "new_node")  # Insert where appropriate
    workflow.add_edge("new_node", "rca_node")
    
    return workflow.compile()
```

### 4. Update __init__.py

Edit `orchestration/langgraph/nodes/__init__.py`:

```python
from .new_node import new_node, analyze_something

__all__ = [
    # ... existing exports ...
    'new_node',
    'analyze_something'
]
```

---

## How to Add Tracing (LangSmith)

### 1. Import Tracing Decorator

In any node file:

```python
from langsmith import traced

@traced
def analyze_something(data):
    # Function will be automatically traced
    pass

@traced
def your_node(state: Dict[str, Any]) -> Dict[str, Any]:
    # Node execution will be traced
    return {...}
```

### 2. Set LangSmith Project

In your script:

```python
import os
os.environ['LANGSMITH_PROJECT'] = 'agent-investigator'
os.environ['LANGSMITH_API_KEY'] = 'your-key'

# Now run workflow - all calls will be traced
final_state = run_investigation('retry_storm')
```

### 3. View Traces

- Dashboard: https://smith.langchain.com/
- Filter by project name: agent-investigator

---

## How to Modify Evidence Scoring

Edit `orchestration/langgraph/nodes/evidence_node.py`:

```python
def aggregate_evidence(logs_analysis, metrics_analysis):
    # Change weights here:
    suspect_scores[service] += score * 0.3  # Was 0.4 (logs weight)
    suspect_scores[service] += score * 0.7  # Was 0.6 (metrics weight)
    
    # Or adjust outlier detection:
    latency_threshold = avg_latency * 2.0  # Was 1.5
    
    return {...}
```

---

## How to Change LLM Model

Edit `orchestration/langgraph/nodes/rca_node.py`:

```python
def perform_rca(evidence, logs_analysis, metrics_analysis, 
                model: str = 'gpt-4'):  # Change default here
    llm = ChatOpenAI(model=model, temperature=0)
    # ... rest of function
```

Or pass at runtime:

```python
# Not yet implemented, would need to pass through state
# Future enhancement
```

---

## How to Customize Output Format

Edit `orchestration/langgraph/workflow.py`:

```python
def format_results(final_state):
    # Add custom fields here
    report = {
        # ... existing fields ...
        'custom_field': value,
        'nested': {
            'key': value
        }
    }
    return report
```

---

## How to Add Conditional Branching

For Phase 7 (AgentScope comparison):

```python
# In workflow.py
def create_investigation_graph():
    workflow = StateGraph(InvestigationState)
    
    # ... add nodes ...
    
    # Define conditional function
    def should_verify(state):
        confidence = state['rca_result']['confidence']
        if confidence < 0.7:
            return "verification_node"
        return "rca_node"
    
    # Add conditional edge
    workflow.add_conditional_edges(
        "evidence_node",
        should_verify
    )
    
    return workflow.compile()
```

---

## How to Add Memory Integration

For Phase 5 (Tencent Memory):

```python
# New file: orchestration/langgraph/nodes/memory_node.py
from tencentdb_agent_memory import AgentMemory

def memory_node(state: Dict[str, Any]) -> Dict[str, Any]:
    memory = AgentMemory()
    
    # Retrieve relevant incidents from memory
    similar_incidents = memory.retrieve(
        state['evidence']['combined_candidates']
    )
    
    return {
        **state,
        'memory_context': similar_incidents
    }

# Then insert into workflow between evidence_node and rca_node
workflow.add_node("memory_node", memory_node)
workflow.add_edge("evidence_node", "memory_node")
workflow.add_edge("memory_node", "rca_node")
```

---

## How to Add Evaluation Metrics

For Phase 6 (DeepEval):

```python
# In scripts/run_investigation.py
from deepeval.metrics import Hallucination, Faithfulness
from deepeval.test_case import LLMTestCase

def evaluate_results(report, ground_truth):
    test_case = LLMTestCase(
        input=report['reasoning'],
        actual_output=report['root_cause'],
        expected_output=ground_truth['root_cause']
    )
    
    # Evaluate metrics
    hallucination_metric = Hallucination()
    faithfulness_metric = Faithfulness()
    
    hallucination_metric.measure(test_case)
    faithfulness_metric.measure(test_case)
    
    return {
        'hallucination_score': hallucination_metric.score,
        'faithfulness_score': faithfulness_metric.score
    }
```

---

## How to Run Individual Nodes

For testing/debugging:

```python
from orchestration.langgraph.nodes.log_node import analyze_logs
from pathlib import Path

# Test log analysis standalone
logs_analysis = analyze_logs(Path('datasets/retry_storm/logs.json'))
print(logs_analysis)

# Test metrics analysis
from orchestration.langgraph.nodes.metrics_node import analyze_metrics
metrics_analysis = analyze_metrics(Path('datasets/retry_storm/metrics.json'))
print(metrics_analysis)

# Test evidence aggregation
from orchestration.langgraph.nodes.evidence_node import aggregate_evidence
evidence = aggregate_evidence(logs_analysis, metrics_analysis)
print(evidence)
```

---

## Common Customizations

### Adjust Error Pattern Detection
```python
# In log_node.py
if 'timeout' in message.lower():
    error_patterns['timeout'] += 1
if 'critical' in level.lower():  # Add custom pattern
    error_patterns['critical'] += 1
```

### Change Anomaly Score Formula
```python
# In metrics_node.py
# Current: 0.6 * latency_score + 0.4 * error_score
# Change to:
combined_score = 0.7 * latency_score + 0.3 * error_score  # More weight on latency
```

### Filter Services
```python
# In evidence_node.py
all_suspects = list(set(logs_suspects + metrics_candidates))

# Filter out irrelevant services
filtered_suspects = [s for s in all_suspects if s not in ['notification-service']]
```

### Change Number of Top Candidates
```python
# In workflow.py format_results()
'suspect_services': evidence.get('combined_candidates', [])[:5]  # Show top 5 instead of all
```

---

## Testing Your Changes

After modifying:

```bash
# Test individual node
python -c "from orchestration.langgraph.nodes.log_node import analyze_logs; ..."

# Test full workflow
python scripts/test_investigation.py

# Test specific scenario
python scripts/run_investigation.py retry_storm
```

---

## Debugging Tips

1. **Print state at each node**: Add `print(state)` at node start
2. **Save intermediate results**: Write to JSON at each node
3. **Use test datasets**: Create small test datasets for quick iteration
4. **Check LLM prompt**: Print prompt before sending to LLM
5. **Verify imports**: Use `python -c "from orchestration.langgraph import ..."`

---

## Performance Optimization

- **Parallel nodes**: Use conditional edges to run nodes in parallel
- **Cache results**: Save analysis results to disk, skip if unchanged
- **Batch LLM calls**: Group multiple analyses into single LLM call
- **Use cheaper models**: Switch gpt-4o-mini to gpt-3.5-turbo for cost

---

## Phase Roadmap Integration

This workflow will be extended in:

- **Phase 4**: Add LangSmith tracing
- **Phase 5**: Add Tencent Memory layer
- **Phase 6**: Add DeepEval metrics
- **Phase 7**: Compare with AgentScope version

Each phase builds on this foundation without breaking existing code.
