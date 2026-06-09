def generate_incident(
    scenario
):

    return {

        "incident_id":
            f"INC_{scenario['scenario_id']}",

        "scenario":
            scenario[
                "scenario_id"
            ],

        "root_cause":
            scenario[
                "root_cause"
            ],

        "failure_type":
            scenario[
                "failure_type"
            ],

        "affected_services":
            scenario[
                "affected_services"
            ],

        "severity":
            scenario[
                "severity"
            ]
    }