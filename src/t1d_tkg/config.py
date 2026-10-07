"""Versioned defaults for the frozen benchmark contract."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True, slots=True)
class BenchmarkConfig:
    """Protocol parameters recorded alongside every benchmark artifact."""

    version: str = "protocol-v0.2"
    history_minutes: int = 120
    primary_horizon_minutes: int = 30
    secondary_horizon_minutes: int = 60
    step_minutes: int = 5
    low_threshold_mg_dl: float = 70.0
    recovery_readings: int = 3
    max_consecutive_missing: int = 2
    refractory_minutes: int = 30
    alert_budget_unmatched_per_day: float = 1.0

    def validate(self) -> None:
        if not self.version:
            raise ValueError("version is required")
        if self.history_minutes <= 0 or self.step_minutes <= 0:
            raise ValueError("history and step must be positive")
        if self.history_minutes % self.step_minutes:
            raise ValueError("history must be divisible by step")
        if self.primary_horizon_minutes <= 0 or self.primary_horizon_minutes % self.step_minutes:
            raise ValueError("primary horizon must be positive and divisible by step")
        if self.secondary_horizon_minutes <= 0 or self.secondary_horizon_minutes % self.step_minutes:
            raise ValueError("secondary horizon must be positive and divisible by step")
        if self.low_threshold_mg_dl <= 0 or self.recovery_readings < 1 or self.max_consecutive_missing < 0:
            raise ValueError("threshold must be positive; recovery must be >=1; missing limit cannot be negative")
        if self.refractory_minutes < 0 or self.alert_budget_unmatched_per_day < 0:
            raise ValueError("refractory and alert budget cannot be negative")

    def as_dict(self) -> dict[str, object]:
        self.validate()
        return asdict(self)


DEFAULT_CONFIG = BenchmarkConfig()

