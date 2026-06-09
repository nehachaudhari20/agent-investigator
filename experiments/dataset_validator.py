import json
from pathlib import Path


class DatasetValidator:

    def __init__(self, dataset_path):

        self.dataset_path = Path(dataset_path)

        with open(
            self.dataset_path / "incident.json"
        ) as f:
            self.incident = json.load(f)

        with open(
            self.dataset_path / "metrics.json"
        ) as f:
            self.metrics = json.load(f)

        with open(
            self.dataset_path / "logs.json"
        ) as f:
            self.logs = json.load(f)

        with open(
            self.dataset_path / "traces.json"
        ) as f:
            self.traces = json.load(f)

    def validate_retry_storm(self):

        metric_map = {
            m["service"]: m["latency_ms"]
            for m in self.metrics
        }

        expected = [

            "risk-engine",

            "fraud-service",

            "payment-service",

            "gateway-service"
        ]

        latencies = [
            metric_map[s]
            for s in expected
        ]

        is_valid = (
            latencies ==
            sorted(
                latencies,
                reverse=True
            )
        )

        return {

            "scenario":
                "retry_storm",

            "valid":
                is_valid,

            "latencies":
                metric_map
        }

    def validate_logs_exist(self):

        return {

            "log_count":
                len(self.logs),

            "valid":
                len(self.logs) > 0
        }

    def validate_traces_exist(self):

        return {

            "trace_count":
                len(self.traces),

            "valid":
                len(self.traces) > 0
        }

    def run(self):

        scenario = self.incident[
            "scenario"
        ]

        results = []

        results.append(
            self.validate_logs_exist()
        )

        results.append(
            self.validate_traces_exist()
        )

        if scenario == "retry_storm":

            results.append(
                self.validate_retry_storm()
            )

        return results