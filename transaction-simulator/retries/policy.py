from dataclasses import dataclass


@dataclass(slots=True)
class RetryDecision:
    should_retry: bool
    delay_seconds: int
    retry_count: int


class RetryPolicy:
    def __init__(self, backoff_schedule: list[int]):
        if not backoff_schedule:
            raise ValueError("Retry backoff schedule must not be empty")
        self.backoff_schedule = backoff_schedule

    def decide(self, current_retry_count: int) -> RetryDecision:
        next_retry_count = current_retry_count + 1
        if next_retry_count > len(self.backoff_schedule):
            return RetryDecision(should_retry=False, delay_seconds=0, retry_count=current_retry_count)

        delay_seconds = self.backoff_schedule[next_retry_count - 1]
        return RetryDecision(
            should_retry=True,
            delay_seconds=delay_seconds,
            retry_count=next_retry_count,
        )
