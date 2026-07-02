# Agent Investigator

> A research platform for evaluating governance, reasoning, observability, and memory in LLM-powered multi-agent systems.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![LangGraph](https://img.shields.io/badge/LangGraph-Orchestration-green)
![LangSmith](https://img.shields.io/badge/LangSmith-Observability-orange)
![Gemini](https://img.shields.io/badge/Gemini-LLM-purple)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## Overview

Modern AI agents are increasingly deployed to perform complex reasoning tasks across software systems. While frameworks provide orchestration, memory, and observability, there is limited understanding of how these systems behave under conflicting evidence, misleading telemetry, or biased historical memory.

**Agent Investigator** is a research platform that benchmarks agent reasoning under realistic operational incidents using synthetic production environments, controlled failure scenarios, and governance-focused evaluation.

Rather than proposing a new agent framework, this project evaluates the strengths and limitations of existing ones.

---

## Research Goal

This project aims to answer:

> **Can modern LLM-powered agent systems perform trustworthy root cause analysis under incomplete, conflicting, misleading, and memory-influenced evidence?**

The findings from this repository will serve as the experimental foundation for **AgentTrust**, a governance framework for trustworthy autonomous agents.

---

# Key Features

- Synthetic production environment simulator
- FinTech-inspired microservice dependency graph
- Incident scenario generation
- Log, metric, and distributed trace synthesis
- LangGraph investigation workflow
- LangSmith observability integration
- Pluggable memory abstraction layer
- Governance-oriented benchmark scenarios
- Extensible evaluation pipeline

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
├── outputs/
│
└── docs/
```

---

# Synthetic Environment

The benchmark simulates a production payment platform consisting of interconnected services.

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

Instead of deploying real microservices, the repository generates realistic operational telemetry that preserves service dependencies and failure propagation.

---

# Benchmark Scenarios

## Retry Storm

Simulates cascading retries originating from the Risk Engine.

Purpose:

- Causality reconstruction
- Root cause localization
- Dependency propagation

Ground Truth:

```
Risk Engine
    ↓
Fraud Service
    ↓
Payment Service
    ↓
Gateway Service
```

---

## Misleading Logs

The visible logs primarily implicate the Payment Service while the actual failure originates in the Fraud Service.

Purpose:

- Hallucination detection
- Evidence prioritization
- Robust reasoning

---

## Memory Poisoning

Historical memory intentionally conflicts with current evidence.

Current Incident

```
Root Cause

Risk Engine
```

Historical Memory

```
Database Overload
Database Overload
Database Overload
```

Purpose:

- Memory bias analysis
- Retrieval robustness
- Governance evaluation

---

# Investigation Workflow

The investigation pipeline is implemented using LangGraph.

```text
                START
                  │
      ┌───────────┼────────────┐
      │           │            │
      ▼           ▼            ▼
 Log Node   Metrics Node   Trace Node
      │           │            │
      └───────────┼────────────┘
                  ▼
        Evidence Aggregator
                  │
                  ▼
         Historical Memory
                  │
                  ▼
           Gemini RCA Engine
                  │
                  ▼
                 END
```

Each node performs a single responsibility before passing structured state to the next stage.

---

# Observability

The workflow is fully instrumented with LangSmith.

Captured information includes:

- LangGraph execution graph
- Prompt traces
- LLM responses
- Node latency
- State transitions
- Token usage

This enables detailed governance analysis of every investigation.

---

# Memory Layer

The memory subsystem is intentionally abstracted from the orchestration framework.

Current implementation:

- JSON-based retrieval
- Historical incident memory
- Poisoned memory benchmark

Future implementations:

- TencentDB-Agent-Memory
- Vector databases
- Hybrid retrieval systems

The workflow remains unchanged regardless of the underlying memory backend.

---

# Current Technology Stack

## Core

- Python
- LangGraph
- Gemini
- LangSmith

## Data

- JSON
- Synthetic telemetry

## AI

- Google Gemini
- Prompt-based reasoning

## Memory

- Abstract retrieval interface
- Historical incident repository

---

# Project Roadmap

## Phase 1

Repository & Foundation

Completed

---

## Phase 2

Synthetic Incident Benchmark

Completed

---

## Phase 2.5

Dataset Validation

Completed

---

## Phase 3

LangGraph Investigation Workflow

Completed

---

## Phase 4

LangSmith Observability

Completed

---

## Phase 5

Memory Abstraction Layer

Completed

---

## Upcoming

- Experiment Runner
- DeepEval Integration
- TencentDB-Agent-Memory
- Governance Benchmark
- AgentTrust

---

# Research Vision

This repository is not intended to build another agent framework.

Instead, it provides a reproducible benchmark for understanding:

- How agents reason
- How memory influences decisions
- How observability improves trust
- Where existing orchestration frameworks fail
- What governance mechanisms future agent systems require

The long-term objective is to experimentally validate the design principles behind **AgentTrust**, a governance framework for trustworthy autonomous AI systems.

---

# License

MIT License