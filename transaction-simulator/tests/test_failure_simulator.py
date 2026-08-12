from simulator.failure import FailureProfile, FailureSimulator


def test_failure_simulator_timeout_priority() -> None:
    simulator = FailureSimulator(
        FailureProfile(
            success_rate=0.7,
            failure_rate=0.2,
            timeout_rate=1.0,
            delay_rate=0.0,
            duplicate_rate=0.0,
            provider_unavailable_rate=0.0,
            db_failure_rate=0.0,
        )
    )
    assert simulator.outcome() == "timeout"


def test_failure_simulator_failure_outcome() -> None:
    simulator = FailureSimulator(
        FailureProfile(
            success_rate=0.0,
            failure_rate=1.0,
            timeout_rate=0.0,
            delay_rate=0.0,
            duplicate_rate=0.0,
            provider_unavailable_rate=0.0,
            db_failure_rate=0.0,
        )
    )
    assert simulator.outcome() == "failure"
