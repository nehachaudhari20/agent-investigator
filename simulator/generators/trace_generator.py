import json
import random


class TraceGenerator:

    def __init__(self):

        with open("services/service_map.json", "r") as f:
            self.service_map = json.load(f)

    def build_path(self, service):

        path = [service]

        while True:

            dependencies = (
                self.service_map["services"][service]
                ["depends_on"]
            )

            if not dependencies:
                break

            service = random.choice(
                dependencies
            )

            path.append(service)

        return path

    def generate_traces(
        self,
        scenario,
        count=100
    ):

        traces = []

        root_cause = scenario[
            "root_cause"
        ]

        for i in range(count):

            if root_cause == "risk-engine":

                path = [
                    "gateway-service",
                    "fraud-service",
                    "risk-engine"
                ]

            elif root_cause == "fraud-service":

                path = [
                    "gateway-service",
                    "fraud-service"
                ]

            else:

                path = self.build_path(
                    "gateway-service"
                )

            traces.append({

                "trace_id":
                    f"txn_{1000+i}",

                "scenario":
                    scenario[
                        "scenario_id"
                    ],

                "path": path

            })

        return traces