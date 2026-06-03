import random


class MetricGenerator:

    def generate_metric(self, service):

        return {
            "service": service,
            "cpu_usage": round(random.uniform(20, 90), 2),
            "memory_usage": round(random.uniform(30, 95), 2),
            "latency_ms": random.randint(50, 5000),
            "error_rate": round(random.uniform(0, 0.5), 3)
        }


if __name__ == "__main__":

    generator = MetricGenerator()

    metric = generator.generate_metric(
        "fraud-service"
    )

    print(metric)