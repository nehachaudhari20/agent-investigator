class MetricGenerator:

    BASELINE = {

        "gateway-service": {
            "latency_ms": 120,
            "error_rate": 0.01
        },

        "payment-service": {
            "latency_ms": 200,
            "error_rate": 0.02
        },

        "fraud-service": {
            "latency_ms": 250,
            "error_rate": 0.03
        },

        "risk-engine": {
            "latency_ms": 180,
            "error_rate": 0.02
        },

        "ledger-service": {
            "latency_ms": 90,
            "error_rate": 0.005
        },

        "notification-service": {
            "latency_ms": 100,
            "error_rate": 0.01
        }
    }

    def generate_metrics(
        self,
        scenario
    ):

        metrics = []

        root = scenario[
            "root_cause"
        ]

        for service, values in (
            self.BASELINE.items()
        ):

            latency = values[
                "latency_ms"
            ]

            error_rate = values[
                "error_rate"
            ]

            if scenario[
                "scenario_id"
            ] == "retry_storm":

                if service == "risk-engine":
                    latency = 3500
                    error_rate = 0.30

                elif service == "fraud-service":
                    latency = 2500
                    error_rate = 0.20

                elif service == "payment-service":
                    latency = 1800
                    error_rate = 0.15

                elif service == "gateway-service":
                    latency = 1200
                    error_rate = 0.10

            metrics.append({

                "service": service,

                "latency_ms":
                    latency,

                "error_rate":
                    error_rate

            })

        return metrics