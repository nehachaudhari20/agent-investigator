# 🔎 Agent Investigator

> **A research platform for evaluating governance, reasoning, observability, and memory in LLM-powered multi-agent systems.**

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![LangGraph](https://img.shields.io/badge/LangGraph-Orchestration-green)
![LangSmith](https://img.shields.io/badge/LangSmith-Observability-orange)
![Gemini](https://img.shields.io/badge/Gemini-LLM-purple)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

# Overview

Modern AI agents are increasingly deployed to perform complex reasoning tasks across software systems. While agent frameworks provide orchestration, memory, and observability, there is still limited understanding of how these systems behave under conflicting evidence, misleading telemetry, or biased historical memory.

**Agent Investigator** is a research platform that benchmarks agent reasoning under realistic operational incidents using synthetic production environments, controlled failure scenarios, and governance-focused evaluation.

Rather than proposing another agent framework, this project experimentally evaluates the strengths, limitations, and trustworthiness of existing approaches.

---

# Research Goal

This project aims to answer the following question:

> **Can modern LLM-powered agent systems perform trustworthy root cause analysis under incomplete, conflicting, misleading, and memory-influenced evidence?**

The insights obtained from these experiments form the experimental foundation for **AgentTrust**, a governance framework for trustworthy autonomous AI systems.

---

# Key Features

- Synthetic production environment simulator
- FinTech-inspired service dependency graph
- Incident scenario generation
- Log, metric, and distributed trace synthesis
- LangGraph-based investigation workflow
- LangSmith observability and execution tracing
- Pluggable memory abstraction layer
- Governance-oriented benchmark scenarios
- Extensible experimentation framework
- Automated investigation report generation

---

# Repository Structure

```text
agent-investigator/

├── datasets/
│   ├── retry_storm/
│   ├── misleading_logs/
│   └── memory_poisoning/
│
├── simulator/
│   ├── scenarios/
│   ├── generators/
│   └── outputs/
│
├── services/
│   └── service_map.json
│
├── orchestration/
│   └── langgraph/
│       ├── nodes/
│       ├── workflow.py
│       ├── state.py
│       └── observability.py
│
├── memory/
│   ├── base.py
│   ├── loader.py
│   ├── retriever.py
│   ├── formatter.py
│   ├── historical_incidents.json
│   └── poisoned_memory.json
│
├── experiments/
│
├── scripts/
│   ├── run_investigation.py
│   ├── run_scenario.py
│   ├── validate_dataset.py
│   ├── test_investigation.py
│   └── test_*.py
│
├── outputs/
│
├── docs/
│
├── requirements.txt
└── README.md
```

---

# Synthetic Environment

The benchmark simulates a production-grade payment platform consisting of interconnected services.

```text
Gateway Service
        │
        ├──────────────┐
        ▼              ▼
Payment Service   Fraud Service
        │              │
        ▼              ▼
 Ledger Service   Risk Engine

Notification Service
```

Instead of deploying real microservices, the repository generates realistic operational telemetry that preserves service dependencies, causal relationships, and failure propagation.

---

# Benchmark Scenarios

## 🔥 Retry Storm

Simulates cascading retries originating from downstream service degradation.

**Research Focus**

- Causality reconstruction
- Root cause localization
- Dependency propagation

---

## 🎭 Misleading Logs

Operational logs intentionally implicate the wrong service while the actual failure originates elsewhere.

**Research Focus**

- Hallucination resistance
- Evidence prioritization
- Robust reasoning

---

## 🧠 Memory Poisoning

Historical incident memory intentionally conflicts with the current operational evidence.

**Research Focus**

- Memory bias
- Retrieval influence
- Governance analysis

---

# Investigation Workflow

The investigation pipeline is implemented using LangGraph.

```text
                         Incident
                             │
      ┌──────────────────────┼──────────────────────┐
      ▼                      ▼                      ▼
   Logs                  Metrics                Traces
      │                      │                      │
      └──────────────────────┼──────────────────────┘
                             ▼
                 Evidence Aggregation Layer
                             │
                             ▼
                  Historical Memory Retrieval
                             │
                             ▼
                 LangGraph Investigation Engine
                             │
                             ▼
                    Gemini Root Cause Analysis
                             │
                             ▼
                  LangSmith Observability Layer
                             │
                             ▼
                   Structured Investigation Report
```

Each stage performs a specialized task before passing structured context to the next stage, enabling transparent and reproducible investigations.

---

# Observability

The investigation workflow is fully instrumented using LangSmith.

Captured information includes:

- Execution graph
- Prompt traces
- LLM responses
- Node execution latency
- State transitions
- Token usage
- Investigation lineage

This enables detailed inspection of agent reasoning throughout the investigation process.

---

# Memory Layer

The memory subsystem is abstracted behind a common retrieval interface, allowing different memory implementations to be evaluated under identical investigation workflows.

The platform supports:

- Historical incident retrieval
- Memory-based contextual reasoning
- Memory poisoning benchmarks
- Pluggable retrieval backends

This architecture enables systematic evaluation of how memory influences autonomous agent reasoning.

---

# Research Ecosystem

Agent Investigator is designed to evaluate and integrate modern AI agent technologies within a unified benchmarking environment.

| Framework | Purpose |
|-----------|---------|
| LangGraph | Workflow orchestration |
| LangSmith | Observability & tracing |
| Google Gemini | Root cause reasoning |
| DeepEval | Evaluation & benchmarking |
| TencentDB-Agent-Memory | Memory backend |
| JSON Memory | Baseline retrieval layer |

Useful resources:

- LangGraph — https://langchain-ai.github.io/langgraph/
- LangSmith — https://smith.langchain.com/
- Google Gemini — https://ai.google.dev/
- DeepEval — https://github.com/confident-ai/deepeval
- TencentDB-Agent-Memory — https://github.com/Tencent/TencentDB-Agent-Memory

---

# Technology Stack

### AI & Orchestration

- LangGraph
- Google Gemini
- LangSmith

### Programming

- Python 3.11+

### Data

- Synthetic Operational Telemetry
- JSON Datasets

### Memory

- Abstract Retrieval Interface
- Historical Incident Repository

### Evaluation

- DeepEval
- Governance-focused Benchmarks

---

# Installation

Clone the repository

```bash
git clone https://github.com/<your-username>/agent-investigator.git

cd agent-investigator
```

Create a virtual environment

```bash
python -m venv venv
```

Activate the environment

```bash
# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Create a `.env` file

```env
GOOGLE_API_KEY=YOUR_API_KEY

LANGCHAIN_API_KEY=YOUR_API_KEY

LANGCHAIN_TRACING_V2=true

LANGCHAIN_PROJECT=agent-investigator
```

---

# Usage

Run all commands from the repository root.

Generate a benchmark dataset

```bash
python scripts/run_scenario.py retry_storm
python scripts/run_scenario.py misleading_logs
python scripts/run_scenario.py memory_poisoning
```

Validate generated datasets

```bash
python scripts/validate_dataset.py retry_storm
```

Run an investigation

```bash
python scripts/run_investigation.py retry_storm
```

Execute the benchmark suite

```bash
python scripts/test_investigation.py
```

Run unit tests

```bash
python scripts/test_rca_node.py
```

---

# Contributing

Contributions are welcome.

Feel free to open an issue for bug reports, feature requests, or research discussions. Pull requests improving benchmark scenarios, evaluation methodologies, or investigation workflows are always appreciated.

---

# Citation

If you use this repository in your research, please consider citing it.

```bibtex
@software{agentinvestigator,
  title={Agent Investigator},
  author={Neha Chaudhari},
  year={2026},
  url={https://github.com/<your-username>/agent-investigator}
}
```

---

# License

Released under the **MIT License**.