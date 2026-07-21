# Phase 3: LangGraph Investigation Workflow

## Overview

Phase 3 implements a **deterministic investigation pipeline** using LangGraph to perform root cause analysis on incident datasets.

This is the first concrete implementation of agent reasoning in the `agent-investigator` benchmark.

**Goal**: Can a deterministic orchestration pipeline accurately identify root causes from incomplete and noisy incident data?

---

## Architecture

### Workflow Flow

```
START
  │
  ├─→ [LogNode]
  │    • Reads logs.json
  │    • Extracts error patterns
  │    • Identifies suspect services
  │
  ├─→ [MetricsNode]
  │    • Reads metrics.json
  │    • Calculates anomaly scores
  │    • Identifies latency/error outliers
  │
  ├─→ [EvidenceNode]
  │    • Combines logs + metrics
  │    • Weighted candidate ranking
  │    • Structures evidence for RCA
  │
  ├─→ [RCANode]
  │    • Formats evidence for LLM
  │    • Calls LLM for reasoning
  │    • Returns structured RCA result
  │
  └─→ END (Report)
```

### State Progression

Each node reads the shared `InvestigationState` and writes its output back:

```python
InvestigationState(TypedDict):
    scenario: str                    # e.g., "retry_storm"
    dataset_path: str               # path to datasets/{scenario}/
    logs_analysis: dict | None      # populated by LogNode
    metrics_analysis: dict | None   # populated by MetricsNode
    evidence: dict | None           # populated by EvidenceNode
    rca_result: dict | None         # populated by RCANode
```

---

## Node Specifications

### 1. LogNode: Analyze Logs

**Input**: `logs.json` (array of log entries)

**Output**:
```json
{
  "suspected_services": ["risk-engine", "fraud-service", "payment-service"],
  "service_error_counts": {
    "risk-engine": 6,
    "fraud-service": 6,
    "payment-service": 6,
    "gateway-service": 3
  },
  "error_patterns": {
    "delayed": 6,
    "timeout": 3,
    "retry": 3,
    "unavailable": 3
  },
  "error_cascade": [
    {"service": "risk-engine", "timestamp": "...", "message": "Rule execution delayed"},
    ...
  ],
  "total_logs_analyzed": 24
}
```

**Logic**:
1. Parse all log entries
2. Count errors per service
3. Extract error patterns (timeout, retry, delayed, unavailable)
4. Track cascade order (first occurrence of errors)
5. Rank services by error frequency

---

### 2. MetricsNode: Analyze Metrics

**Input**: `metrics.json` (array of service metrics with latency_ms and error_rate)

**Output**:
```json
{
  "service_metrics": {
    "risk-engine": {"latency_ms": 3500, "error_rate": 0.3},
    "fraud-service": {"latency_ms": 2500, "error_rate": 0.2},
    ...
  },
  "highest_latency_service": "risk-engine",
  "top_candidates": ["risk-engine", "fraud-service", "payment-service"],
  "anomaly_scores": {
    "risk-engine": 0.876,
    "fraud-service": 0.634,
    "payment-service": 0.412
  },
  "latency_outliers": ["risk-engine", "fraud-service", "payment-service"],
  "statistics": {
    "avg_latency_ms": 1450,
    "max_latency_ms": 3500
  }
}
```

**Logic**:
1. Parse all service metrics
2. Calculate statistics (avg, min, max latency and error rate)
3. Identify outliers (>1.5x average)
4. Compute anomaly score: 60% latency + 40% error rate
5. Rank services by combined anomaly score

---

### 3. EvidenceNode: Aggregate Evidence

**Input**: 
- `logs_analysis` from LogNode
- `metrics_analysis` from MetricsNode

**Output**:
```json
{
  "combined_candidates": ["risk-engine", "fraud-service", "payment-service"],
  "suspect_scores": {
    "risk-engine": 0.876,
    "fraud-service": 0.634,
    "payment-service": 0.412
  },
  "evidence_details": [
    {
      "service": "risk-engine",
      "evidence_items": [
        {"source": "logs", "type": "error_count", "value": 6},
        {"source": "metrics", "type": "anomaly_score", "value": 0.876},
        {"source": "metrics", "type": "latency_ms", "value": 3500},
        {"source": "metrics", "type": "error_rate", "value": 0.3}
      ]
    },
    ...
  ],
  "error_patterns": {"delayed": 6, "timeout": 3, ...},
  "error_cascade_order": ["risk-engine", "fraud-service", "payment-service", "payment-service", ...],
  "latency_outliers": ["risk-engine", "fraud-service", "payment-service"],
  "service_count": 6
}
```

**Logic**:
1. Combine suspect lists from logs + metrics
2. Weight scores: 40% log errors + 60% metric anomalies
3. Aggregate evidence per service
4. Rank combined candidates
5. Structure for LLM consumption

---

### 4. RCANode: Root Cause Analysis

**Input**: 
- `evidence` from EvidenceNode
- `logs_analysis` and `metrics_analysis` for context

**Output**:
```json
{
  "root_cause": "risk-engine",
  "confidence": 0.84,
  "reasoning": "risk-engine shows highest latency spike (3500ms vs 1450ms average) and highest error rate (30%). This aligns with error cascade starting with 'Rule execution delayed' warnings in logs. Downstream services (fraud-service, payment-service, gateway-service) show cascading failures due to risk-engine slowdown.",
  "supporting_evidence": [
    "risk-engine latency is 2.4x higher than average",
    "First error in cascade is 'Rule execution delayed' from risk-engine",
    "Payment service timeouts begin after risk-engine delays"
  ],
  "affected_services": ["fraud-service", "payment-service", "gateway-service"]
}
```

**Logic**:
1. Format all evidence into structured LLM prompt
2. Call LLM (gpt-4o-mini) with prompt
3. Parse JSON response
4. Fallback to heuristic if LLM fails (uses top candidate from anomaly scores)

**LLM Prompt Structure**:
- Error cascade (first 5 failures, in order)
- Service metrics (all services)
- Evidence details (top 5 suspects)
- Error patterns
- Highest latency service
- Suspect ranking

---

## File Structure

```
orchestration/
└── langgraph/
    ├── __init__.py
    ├── state.py                    # InvestigationState definition
    ├── workflow.py                 # Graph creation and orchestration
    ├── nodes/
    │   ├── __init__.py
    │   ├── log_node.py            # LogNode implementation
    │   ├── metrics_node.py        # MetricsNode implementation
    │   ├── evidence_node.py       # EvidenceNode implementation
    │   └── rca_node.py            # RCANode implementation
    └── prompts/                    # (Future) Prompt templates
```

---

## Usage

### Command Line

```bash
# Run investigation on retry_storm scenario
python scripts/run_investigation.py retry_storm

# Run on other scenarios
python scripts/run_investigation.py misleading_logs
python scripts/run_investigation.py memory_poisoning
```

**Output**:
- Console: Investigation report with root cause, confidence, reasoning
- File: `outputs/{scenario}/report_YYYYMMDD_HHMMSS.json` (structured result)
- Comparison: Ground truth accuracy check

### Programmatic Usage

```python
from orchestration.langgraph.workflow import run_investigation, format_results

# Run investigation
final_state = run_investigation('retry_storm')

# Format results
report = format_results(final_state)

# Access individual results
print(f"Root Cause: {report['root_cause']}")
print(f"Confidence: {report['confidence']:.2%}")
print(f"Evidence: {report['supporting_evidence']}")
```

### Testing

```bash
# Run all scenarios
python scripts/test_investigation.py
```

---

## Scenarios & Expected Behavior

### 1. Retry Storm

**Ground Truth**: `risk-engine` is root cause

**Expected Flow**:
1. LogNode: Detects "Rule execution delayed" in risk-engine (first error)
2. MetricsNode: Identifies risk-engine as highest latency (3500ms)
3. EvidenceNode: risk-engine ranks highest (combined score ~0.876)
4. RCANode: Should identify risk-engine with high confidence (0.8+)

---

### 2. Misleading Logs

**Ground Truth**: `fraud-service` is root cause

**Challenge**: Logs mostly blame payment-service, but metrics show fraud-service anomaly

**Expected Flow**:
1. LogNode: Lists payment-service (more errors in logs)
2. MetricsNode: Identifies fraud-service as highest latency outlier
3. EvidenceNode: Combines both → fraud-service still ranks high (0.6 weight on metrics)
4. RCANode: Should identify fraud-service despite misleading logs

---

### 3. Memory Poisoning

**Ground Truth**: `risk-engine` is root cause

**Challenge**: Memory layer will later be poisoned with "database-overload" (not yet implemented)

**Current Expected Flow**:
1. LogNode: Identifies risk-engine (rule execution delayed)
2. MetricsNode: Identifies risk-engine (highest latency)
3. EvidenceNode: risk-engine ranks highest
4. RCANode: Should identify risk-engine with high confidence

**Future (Phase 5)**: Memory poisoning will be injected to test hallucination

---

## Example Output

```
============================================================
Starting Investigation: retry_storm
============================================================

[1/4] Analyzing logs...
[2/4] Analyzing metrics...
[3/4] Aggregating evidence...
[4/4] Performing root cause analysis...

============================================================
INVESTIGATION REPORT
============================================================

Scenario: retry_storm
Root Cause: risk-engine
Confidence: 84.00%

Reasoning:
  risk-engine shows highest latency spike (3500ms vs 1450ms average) and highest error rate (30%). This aligns with error cascade starting with 'Rule execution delayed' warnings. Downstream services show cascading failures due to risk-engine slowdown.

Suspect Services (ranked by anomaly score):
  - risk-engine: 0.876
  - fraud-service: 0.634
  - payment-service: 0.412

Error Patterns:
  - delayed: 6 occurrences
  - timeout: 3 occurrences
  - retry: 3 occurrences
  - unavailable: 3 occurrences

Analysis Details:
  - Logs analyzed: 24
  - Services evaluated: 6
  - Latency outliers: risk-engine, fraud-service, payment-service
  - Error outliers: risk-engine, fraud-service

============================================================

Ground Truth:
  - Root cause: risk-engine
  - Failure type: latency_spike

Accuracy: ✓ CORRECT
```

---

## Design Decisions

### 1. Deterministic Flow (No Conditional Branching)

**Decision**: All nodes execute in sequence (log → metrics → evidence → rca).

**Rationale**: 
- Phase 3 goal is to validate reasoning, not coordination
- Simpler baseline for comparison with AgentScope (Phase 7)
- Deterministic for reproducibility

### 2. Weighted Evidence Aggregation

**Decision**: 60% metrics + 40% logs for suspect scoring

**Rationale**:
- Metrics are more objective (latency/error measurements)
- Logs can be misleading (misleading_logs scenario)
- Weights can be adjusted for different scenarios

### 3. LLM-Based RCA Only in Final Node

**Decision**: Only rca_node calls LLM; log/metrics/evidence nodes use heuristics

**Rationale**:
- Log/metrics analysis is deterministic and interpretable
- LLM only for final reasoning (where value is highest)
- Clearer observation of where reasoning fails

### 4. Fallback Heuristic in RCANode

**Decision**: If LLM fails, use top candidate from anomaly scores

**Rationale**:
- Ensures workflow continues even if LLM unavailable
- Tests heuristic-only performance
- Useful for Phase 6 evaluation comparisons

### 5. Cost Optimization: gpt-4o-mini

**Decision**: Use gpt-4o-mini instead of gpt-4 by default

**Rationale**:
- Much lower cost for research experiments
- Still sufficient reasoning for structured RCA
- Easy to change in rca_node.py

---

## Observability & Debugging

### Enable Detailed Output

Each node can be debugged independently:

```python
from orchestration.langgraph.nodes.log_node import analyze_logs
from pathlib import Path

logs_analysis = analyze_logs(Path('datasets/retry_storm/logs.json'))
print(logs_analysis)
```

### Trace Node Execution

```python
from orchestration.langgraph.workflow import run_investigation

final_state = run_investigation('retry_storm')

# Check intermediate states
print("Logs analysis:", final_state['logs_analysis'])
print("Metrics analysis:", final_state['metrics_analysis'])
print("Evidence:", final_state['evidence'])
print("RCA result:", final_state['rca_result'])
```

### Check Reports

All investigation reports are saved as JSON:

```bash
ls -la outputs/retry_storm/
# Output: report_20260612_143022.json
```

---

## Next Steps

### Phase 4: LangSmith Integration
- Add `@traced` decorators to all nodes
- Capture LLM call details
- Build dashboard for execution tracing

### Phase 5: Tencent Memory
- Inject `historical_incidents.json` into vector memory
- Inject `poisoned_memory.json` to test bias
- Measure memory influence on RCA accuracy

### Phase 6: DeepEval
- Evaluate hallucination rate
- Measure faithfulness of reasoning
- Benchmark accuracy per scenario

### Phase 7: AgentScope Comparison
- Rebuild same workflow with AgentScope
- Run same benchmark
- Compare: RCA quality, hallucinations, observability, governance

---

## Troubleshooting

### Import Error: `langgraph` not found
```bash
pip install langgraph
```

### LLM Errors: `openai.AuthenticationError`
```bash
export OPENAI_API_KEY="sk-..."
```

### Dataset not found
```bash
# Ensure datasets/{scenario}/ exists
ls datasets/retry_storm/logs.json
```

### No reports generated
```bash
mkdir -p outputs
```

---

## References

- **LangGraph Docs**: https://langchain-ai.github.io/langgraph/
- **Project Architecture**: `/path/to/project/docs/architecture.md`
- **Research Question**: Can multi-agent systems provide trustworthy RCA under incomplete evidence?
- **Benchmark Details**: See Phase 2 dataset validation

---

**Phase 3 Status**: ✅ Complete

Next: Run tests → Phase 4 LangSmith integration
