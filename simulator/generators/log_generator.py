import json
import random
from datetime import datetime, timedelta
from pathlib import Path


class LogGenerator:

    def __init__(self):

        with open("services/service_map.json", "r") as f:
            self.service_map = json.load(f)

        self.log_templates = {
            "gateway-service": [
                "Request routed successfully",
                "Downstream service unavailable",
                "API request timeout"
            ],
            "payment-service": [
                "Transaction processed",
                "Transaction timeout",
                "Retry triggered"
            ],
            "fraud-service": [
                "Fraud score calculated",
                "Risk evaluation delayed",
                "Cache lookup failed"
            ],
            "ledger-service": [
                "Ledger entry committed",
                "Database write timeout"
            ],
            "risk-engine": [
                "Risk score generated",
                "Rule execution delayed"
            ],
            "notification-service": [
                "Notification sent",
                "Email delivery failed"
            ]
        }

    def generate_logs(self, count=300):

        logs = []

        start_time = datetime.utcnow()

        services = list(
            self.service_map["services"].keys()
        )

        for i in range(count):

            service = random.choice(services)

            logs.append({
                "timestamp":
                    (start_time + timedelta(seconds=i))
                    .isoformat(),

                "service": service,

                "level": random.choice(
                    ["INFO", "WARN", "ERROR"]
                ),

                "message": random.choice(
                    self.log_templates[service]
                ),

                "trace_id":
                    f"txn_{random.randint(1000,9999)}"
            })

        return logs


if __name__ == "__main__":

    generator = LogGenerator()

    logs = generator.generate_logs()

    output_file = (
        "datasets/logs/sample_logs.json"
    )

    with open(output_file, "w") as f:
        json.dump(logs, f, indent=4)

    print(
        f"{len(logs)} logs written to {output_file}"
    )