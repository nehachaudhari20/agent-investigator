from datetime import datetime, timedelta


class LogGenerator:

    def generate_logs(
        self,
        scenario,
        count=500
    ):

        logs = []

        start = datetime.utcnow()

        if scenario[
            "scenario_id"
        ] == "retry_storm":

            messages = [

                (
                    "risk-engine",
                    "WARN",
                    "Rule execution delayed"
                ),

                (
                    "fraud-service",
                    "WARN",
                    "Risk evaluation delayed"
                ),

                (
                    "payment-service",
                    "ERROR",
                    "Transaction timeout"
                ),

                (
                    "payment-service",
                    "WARN",
                    "Retry triggered"
                ),

                (
                    "gateway-service",
                    "ERROR",
                    "Downstream service unavailable"
                )
            ]

        elif scenario[
            "scenario_id"
        ] == "misleading_logs":

            messages = [

                (
                    "payment-service",
                    "ERROR",
                    "Transaction timeout"
                ),

                (
                    "gateway-service",
                    "ERROR",
                    "API request timeout"
                ),

                (
                    "fraud-service",
                    "WARN",
                    "Cache lookup failed"
                )
            ]

        else:

            messages = [

                (
                    "fraud-service",
                    "WARN",
                    "Historical pattern matched"
                ),

                (
                    "payment-service",
                    "ERROR",
                    "Transaction timeout"
                )
            ]

        for i in range(count):

            service, level, message = (
                messages[
                    i % len(messages)
                ]
            )

            logs.append({

                "timestamp":
                    (
                        start +
                        timedelta(
                            seconds=i
                        )
                    ).isoformat(),

                "service":
                    service,

                "level":
                    level,

                "message":
                    message,

                "trace_id":
                    f"txn_{1000+(i%100)}"
            })

        return logs