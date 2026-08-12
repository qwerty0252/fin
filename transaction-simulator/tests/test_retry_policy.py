from retries.policy import RetryPolicy


def test_retry_policy_progression() -> None:
    policy = RetryPolicy([5, 15, 30])

    first = policy.decide(0)
    assert first.should_retry is True
    assert first.delay_seconds == 5
    assert first.retry_count == 1

    second = policy.decide(1)
    assert second.should_retry is True
    assert second.delay_seconds == 15
    assert second.retry_count == 2

    third = policy.decide(2)
    assert third.should_retry is True
    assert third.delay_seconds == 30
    assert third.retry_count == 3

    exhausted = policy.decide(3)
    assert exhausted.should_retry is False
