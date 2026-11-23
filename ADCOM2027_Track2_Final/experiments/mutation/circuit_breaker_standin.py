"""RECONSTRUCTED STAND-IN for agents/orchestrator/circuit_breaker.py, which is absent from every ref of this repository.
Interface inferred from its use in agents/multiagent/coordinator.py: CircuitBreaker(threshold, cooldown_s, clock=...),
allow(), record_failure(), record_success(). Semantics: opens after `threshold` consecutive failures, stays open for
`cooldown_s`, then allows a trial call. Used ONLY in the scratch export for protocol MA-MUT v2; not part of the repository."""
import time


class CircuitBreaker:
    def __init__(self, threshold=2, cooldown_s=60.0, clock=time.monotonic):
        self.threshold, self.cooldown_s, self.clock = int(threshold), float(cooldown_s), clock
        self.failures, self.opened_at = 0, None

    def allow(self):
        if self.opened_at is None:
            return True
        if self.clock() - self.opened_at >= self.cooldown_s:
            self.opened_at, self.failures = None, self.threshold - 1   # half-open: one trial call
            return True
        return False

    def record_failure(self):
        self.failures += 1
        if self.failures >= self.threshold:
            self.opened_at = self.clock()

    def record_success(self):
        self.failures, self.opened_at = 0, None
