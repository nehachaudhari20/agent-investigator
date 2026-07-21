import json
import os
import sys

from _paths import PROJECT_ROOT
from simulator.generators.incident_generator import generate_incident
from simulator.generators.log_generator import LogGenerator
from simulator.generators.metric_generator import MetricGenerator
from simulator.generators.trace_generator import TraceGenerator
from simulator.scenario_loader import load_scenario

if len(sys.argv) != 2:
    print("Usage: python scripts/run_scenario.py <scenario_name>")
    sys.exit(1)

scenario_name = sys.argv[1]

scenario_path = PROJECT_ROOT / "simulator" / "scenarios" / f"{scenario_name}.json"
scenario = load_scenario(str(scenario_path))

traces = TraceGenerator().generate_traces(scenario)
metrics = MetricGenerator().generate_metrics(scenario)
logs = LogGenerator().generate_logs(scenario)
incident = generate_incident(scenario)

output_dir = PROJECT_ROOT / "datasets" / scenario["scenario_id"]
os.makedirs(output_dir, exist_ok=True)

with open(output_dir / "logs.json", "w") as f:
    json.dump(logs, f, indent=4)

with open(output_dir / "metrics.json", "w") as f:
    json.dump(metrics, f, indent=4)

with open(output_dir / "traces.json", "w") as f:
    json.dump(traces, f, indent=4)

with open(output_dir / "incident.json", "w") as f:
    json.dump(incident, f, indent=4)

print(f"Generated {scenario['scenario_id']}")
