import json
import random


class MetricGenerator:

    def __init__(self):

        with open(
            "services/service_map.json",
            "r"
        ) as f:

            self.service_map = json.load(f)

    def generate_metrics(
        self,
        snapshots=100
    ):

        metrics = []

        services = list(
            self.service_map["services"].keys()
        )

        for _ in range(snapshots):

            service = random.choice(
                services
            )

            metrics.append({

                "service": service,

                "cpu_usage":
                    round(
                        random.uniform(10, 90),
                        2
                    ),

                "memory_usage":
                    round(
                        random.uniform(20, 95),
                        2
                    ),

                "latency_ms":
                    random.randint(
                        50,
                        5000
                    ),

                "error_rate":
                    round(
                        random.uniform(
                            0,
                            0.4
                        ),
                        3
                    )
            })

        return metrics


if __name__ == "__main__":

    generator = MetricGenerator()

    metrics = generator.generate_metrics()

    output_file = (
        "datasets/metrics/sample_metrics.json"
    )

    with open(output_file, "w") as f:
        json.dump(metrics, f, indent=4)

    print(
        f"{len(metrics)} metrics written to {output_file}"
    )