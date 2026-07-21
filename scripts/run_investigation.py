"""
Entry point - Run investigation workflow on a scenario dataset.

Usage:
    python scripts/run_investigation.py retry_storm
    python scripts/run_investigation.py misleading_logs
    python scripts/run_investigation.py memory_poisoning
"""

import json
import sys
from datetime import datetime
from pathlib import Path

from _paths import PROJECT_ROOT
from orchestration.langgraph.workflow import format_results, run_investigation


def main():
    """Run investigation on specified scenario."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/run_investigation.py <scenario>")
        print("  Scenarios: retry_storm, misleading_logs, memory_poisoning")
        sys.exit(1)

    scenario = sys.argv[1]

    valid_scenarios = ["retry_storm", "misleading_logs", "memory_poisoning"]
    if scenario not in valid_scenarios:
        print(f"Invalid scenario: {scenario}")
        print(f"Valid scenarios: {', '.join(valid_scenarios)}")
        sys.exit(1)

    print(f"\n{'=' * 60}")
    print(f"Starting Investigation: {scenario}")
    print(f"{'=' * 60}\n")

    try:
        print("[1/4] Analyzing logs...")
        print("[2/4] Analyzing metrics...")
        print("[3/4] Aggregating evidence...")
        print("[4/4] Performing root cause analysis...")
        print()

        final_state = run_investigation(scenario)
        report = format_results(final_state)

        print(f"\n{'=' * 60}")
        print("INVESTIGATION REPORT")
        print(f"{'=' * 60}\n")

        print(f"Scenario: {report['scenario']}")
        print(f"Root Cause: {report['root_cause']}")
        print(f"Confidence: {report['confidence']:.2%}\n")

        print("Reasoning:")
        print(f"  {report['reasoning']}\n")

        print("Suspect Services (ranked by anomaly score):")
        for service, score in report["suspect_scores"].items():
            print(f"  - {service}: {score:.3f}")
        print()

        print("Error Patterns:")
        for pattern, count in report["error_patterns"].items():
            if count > 0:
                print(f"  - {pattern}: {count} occurrences")
        print()

        print("Analysis Details:")
        print(f"  - Logs analyzed: {report['analysis_details']['logs_analyzed']}")
        print(f"  - Services evaluated: {report['analysis_details']['services_evaluated']}")
        print(
            f"  - Latency outliers: {', '.join(report['analysis_details']['latency_outliers']) or 'none'}"
        )
        print(
            f"  - Error outliers: {', '.join(report['analysis_details']['error_outliers']) or 'none'}"
        )

        print(f"\n{'=' * 60}\n")

        report_path = (
            PROJECT_ROOT
            / "outputs"
            / scenario
            / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        print(f"Report saved to: {report_path}\n")

        dataset_path = PROJECT_ROOT / "datasets" / scenario
        incident_path = dataset_path / "incident.json"

        if incident_path.exists():
            with open(incident_path, "r") as f:
                ground_truth = json.load(f)

            print("Ground Truth:")
            print(f"  - Root cause: {ground_truth['root_cause']}")
            print(f"  - Failure type: {ground_truth['failure_type']}")

            accuracy = report["root_cause"] == ground_truth["root_cause"]
            print(f"\nAccuracy: {'CORRECT' if accuracy else 'INCORRECT'}")
            print()

    except Exception as e:
        print(f"\nInvestigation failed: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
