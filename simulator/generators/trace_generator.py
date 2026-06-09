import json
import random


class TraceGenerator:

    def __init__(self):

        with open(
            "services/service_map.json",
            "r"
        ) as f:

            self.service_map = json.load(f)

    def build_path(
        self,
        current_service,
        path=None
    ):

        if path is None:
            path = []

        path.append(
            current_service
        )

        dependencies = (
            self.service_map["services"]
            [current_service]
            ["depends_on"]
        )

        if not dependencies:
            return path

        next_service = random.choice(
            dependencies
        )

        return self.build_path(
            next_service,
            path
        )

    def generate_traces(
        self,
        count=100
    ):

        traces = []

        for _ in range(count):

            traces.append({

                "trace_id":
                    f"txn_{random.randint(1000,9999)}",

                "path":
                    self.build_path(
                        "gateway-service"
                    )
            })

        return traces


if __name__ == "__main__":

    generator = TraceGenerator()

    traces = generator.generate_traces()

    output_file = (
        "datasets/traces/sample_traces.json"
    )

    with open(output_file, "w") as f:
        json.dump(traces, f, indent=4)

    print(
        f"{len(traces)} traces written to {output_file}"
    )