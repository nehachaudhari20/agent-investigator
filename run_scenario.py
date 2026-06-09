import json

from simulator.scenario_loader import (
    load_scenario
)

from simulator.generators.trace_generator import (
    TraceGenerator
)

from simulator.generators.metric_generator import (
    MetricGenerator
)

from simulator.generators.log_generator import (
    LogGenerator
)

from simulator.generators.incident_generator import (
    generate_incident
)


SCENARIO_PATH = (
    "simulator/scenarios/"
    "retry_storm.json"
)

scenario = load_scenario(
    SCENARIO_PATH
)

traces = TraceGenerator()\
    .generate_traces(
        scenario
    )

metrics = MetricGenerator()\
    .generate_metrics(
        scenario
    )

logs = LogGenerator()\
    .generate_logs(
        scenario
    )

incident = generate_incident(
    scenario
)

output_dir = (
    f"datasets/"
    f"{scenario['scenario_id']}"
)

import os

os.makedirs(
    output_dir,
    exist_ok=True
)

with open(
    f"{output_dir}/logs.json",
    "w"
) as f:
    json.dump(logs, f, indent=4)

with open(
    f"{output_dir}/metrics.json",
    "w"
) as f:
    json.dump(metrics, f, indent=4)

with open(
    f"{output_dir}/traces.json",
    "w"
) as f:
    json.dump(traces, f, indent=4)

with open(
    f"{output_dir}/incident.json",
    "w"
) as f:
    json.dump(
        incident,
        f,
        indent=4
    )

print(
    f"Generated "
    f"{scenario['scenario_id']}"
)
