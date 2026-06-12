# Quick Start - Phase 3 LangGraph Pipeline

Get started in 5 minutes.

---

## Prerequisites

```bash
# Ensure dependencies installed
pip install langgraph langchain langchain-openai

# Ensure OpenAI API key set
export OPENAI_API_KEY="sk-..."
```

---

## 1. Run Single Investigation

```bash
python run_investigation.py retry_storm
```

**Expected output**:
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
  risk-engine shows highest latency spike...

Suspect Services (ranked by anomaly score):
  - risk-engine: 0.876
  - fraud-service: 0.634
  - payment-service: 0.412

Ground Truth:
  - Root cause: risk-engine

Accuracy: ✓ CORRECT
```

---

## 2. Test All Scenarios

```bash
python test_investigation.py
```

**Expected**:
```
============================================================
LANGGRAPH INVESTIGATION WORKFLOW - TEST SUITE
============================================================

Testing scenario: retry_storm
✓ Root Cause: risk-engine
✓ Confidence: 0.84
✓ Suspect Services: risk-engine, fraud-service, payment-service
✓ PASS - Expected: risk-engine

Testing scenario: misleading_logs
✓ Root Cause: fraud-service
✓ Confidence: 0.72
✓ Suspect Services: fraud-service, payment-service, risk-engine
✓ PASS - Expected: fraud-service

Testing scenario: memory_poisoning
✓ Root Cause: risk-engine
✓ Confidence: 0.79
✓ Suspect Services: risk-engine, fraud-service, payment-service
✓ PASS - Expected: risk-engine

============================================================
TEST SUMMARY
============================================================

✓ retry_storm
✓ misleading_logs
✓ memory_poisoning

Total: 3/3 scenarios passed
```

---

## 3. Check Reports

Reports are saved to `outputs/{scenario}/`:

```bash
# List all reports
ls -la outputs/retry_storm/

# View latest report
cat outputs/retry_storm/report_*.json | python -m json.tool
```

---

## 4. Use Programmatically

```python
from orchestration.langgraph.workflow import run_investigation, format_results

# Run investigation
final_state = run_investigation('retry_storm')

# Get formatted report
report = format_results(final_state)

# Access results
print(f"Root Cause: {report['root_cause']}")
print(f"Confidence: {report['confidence']:.2%}")
print(f"Reasoning: {report['reasoning']}")
print(f"Affected Services: {report['affected_services']}")
```

---

## 5. Inspect Individual Node Outputs

```python
from orchestration.langgraph.workflow import run_investigation

# Run workflow
final_state = run_investigation('retry_storm')

# Inspect individual node outputs
print("\n=== LOG ANALYSIS ===")
print(final_state['logs_analysis'])

print("\n=== METRICS ANALYSIS ===")
print(final_state['metrics_analysis'])

print("\n=== AGGREGATED EVIDENCE ===")
print(final_state['evidence'])

print("\n=== RCA RESULT ===")
print(final_state['rca_result'])
```

---

## 6. Debug a Single Node

```python
from orchestration.langgraph.nodes.log_node import analyze_logs
from pathlib import Path

# Test log node in isolation
logs_analysis = analyze_logs(Path('datasets/retry_storm/logs.json'))
print(logs_analysis)

# Check what it found
print(f"Suspected services: {logs_analysis['suspected_services']}")
print(f"Error patterns: {logs_analysis['error_patterns']}")
print(f"Service error counts: {logs_analysis['service_error_counts']}")
```

---

## Workflow Diagram

```
INPUT: datasets/{scenario}/
  - logs.json
  - metrics.json
  - incident.json (ground truth)
       ↓
   [LogNode]
   ├─ Parse logs.json
   ├─ Extract error patterns
   ├─ Count errors per service
   └─ Output: suspected_services, error_cascade
       ↓
   [MetricsNode]
   ├─ Parse metrics.json
   ├─ Calculate latency/error outliers
   ├─ Compute anomaly scores
   └─ Output: top_candidates, anomaly_scores
       ↓
   [EvidenceNode]
   ├─ Combine logs + metrics
   ├─ Weight scoring (40% logs, 60% metrics)
   ├─ Structure evidence for LLM
   └─ Output: combined_candidates, suspect_scores
       ↓
   [RCANode]
   ├─ Format evidence into LLM prompt
   ├─ Call LLM with evidence
   ├─ Parse JSON response
   └─ Output: root_cause, confidence, reasoning
       ↓
OUTPUT: Investigation Report
  - root_cause
  - confidence
  - reasoning
  - supporting_evidence
  - affected_services
  - suspect_services (ranked)
```

---

## Output Structure

```json
{
  "scenario": "retry_storm",
  "root_cause": "risk-engine",
  "confidence": 0.84,
  "reasoning": "...",
  "supporting_evidence": [
    "risk-engine latency is 2.4x higher than average",
    "First error in cascade is from risk-engine",
    "Payment service timeouts begin after risk-engine delays"
  ],
  "affected_services": [
    "fraud-service",
    "payment-service",
    "gateway-service"
  ],
  "suspect_services": [
    "risk-engine",
    "fraud-service",
    "payment-service"
  ],
  "suspect_scores": {
    "risk-engine": 0.876,
    "fraud-service": 0.634,
    "payment-service": 0.412
  },
  "error_patterns": {
    "delayed": 6,
    "timeout": 3,
    "retry": 3,
    "unavailable": 3
  },
  "analysis_details": {
    "logs_analyzed": 24,
    "services_evaluated": 6,
    "latency_outliers": [
      "risk-engine",
      "fraud-service",
      "payment-service"
    ],
    "error_outliers": [
      "risk-engine",
      "fraud-service"
    ]
  }
}
```

---

## Troubleshooting

### Q: `ModuleNotFoundError: No module named 'langgraph'`
```bash
pip install langgraph
```

### Q: `openai.AuthenticationError: Invalid API key`
```bash
export OPENAI_API_KEY="sk-your-key-here"
```

### Q: `FileNotFoundError: datasets/retry_storm not found`
Ensure you're in the project root:
```bash
cd d:\PROJECTS\agent-investigator
python run_investigation.py retry_storm
```

### Q: LLM is slow
Use cheaper model (edit rca_node.py):
```python
llm = ChatOpenAI(model='gpt-3.5-turbo', temperature=0)
```

### Q: Want to disable LLM (use heuristic only)
The workflow already has fallback heuristics. If LLM fails, it uses anomaly scores.

---

## Next: What to Do After Testing

1. **Verify it works** (all 3 scenarios should pass)
2. **Check reports** in `outputs/` directory
3. **Read full docs**: `docs/PHASE_3_LANGGRAPH.md`
4. **Review extension guide**: `docs/LANGGRAPH_EXTENSION_GUIDE.md`
5. **Next phase**: Phase 4 - LangSmith integration (tracing & observability)

---

## Scenarios Tested

| Scenario | Ground Truth | Challenge | Expected |
|----------|--------------|-----------|----------|
| **retry_storm** | risk-engine | None | Easy pass |
| **misleading_logs** | fraud-service | Logs blame payment-service | Medium (metrics override logs) |
| **memory_poisoning** | risk-engine | Memory will be poisoned (Phase 5) | Currently passes; failing in Phase 5 is expected |

---

## Architecture at a Glance

```python
# Entry point
final_state = run_investigation('retry_storm')

# final_state contains:
# - scenario: 'retry_storm'
# - logs_analysis: {...}
# - metrics_analysis: {...}
# - evidence: {...}
# - rca_result: {root_cause, confidence, reasoning, ...}

# Get report
report = format_results(final_state)
# report contains formatted, human-readable output
```

---

## That's It!

You now have a working deterministic RCA pipeline. 

**Next**: Phase 4 will add LangSmith tracing for observability.

Questions? See `docs/PHASE_3_LANGGRAPH.md` for full details.
