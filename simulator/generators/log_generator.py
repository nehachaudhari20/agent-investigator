import random
from datetime import datetime


class LogGenerator:

    def generate_log(
        self,
        service,
        level="INFO",
        message="Operation completed"
    ):
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "service": service,
            "level": level,
            "message": message,
            "trace_id": f"txn_{random.randint(1000,9999)}"
        }


if __name__ == "__main__":

    generator = LogGenerator()

    sample_log = generator.generate_log(
        service="payment-service",
        level="ERROR",
        message="Transaction timeout"
    )

    print(sample_log)