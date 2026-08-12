"""Deterministic, species-aware scheduling for natural desktop pet behavior."""

from __future__ import annotations

import random
from collections import deque
from dataclasses import dataclass

NATURAL_STATES = frozenset({"idle", "walking", "running", "resting", "eating"})
ALL_STATES = NATURAL_STATES | {"caged"}

MODE_TO_STATE = {
    "free": "idle",
    "resting": "resting",
    "walking": "walking",
    "running": "running",
    "eating": "eating",
    "caged": "caged",
}
STATE_TO_MODE = {
    "idle": "free",
    "resting": "resting",
    "walking": "walking",
    "running": "running",
    "eating": "eating",
    "caged": "caged",
}


@dataclass(frozen=True)
class SpeciesProfile:
    durations_ms: dict[str, tuple[int, int]]
    walk_speed_px_s: tuple[float, float]
    run_speed_px_s: tuple[float, float]
    transitions: dict[str, tuple[tuple[str, float], ...]]


PROFILES = {
    "cat": SpeciesProfile(
        durations_ms={
            "idle": (4_500, 9_000),
            "walking": (6_000, 14_000),
            "running": (2_400, 5_000),
            "resting": (12_000, 28_000),
            "eating": (5_000, 6_200),
        },
        walk_speed_px_s=(10.0, 15.0),
        run_speed_px_s=(29.0, 38.0),
        transitions={
            "idle": (("resting", 0.42), ("walking", 0.45), ("running", 0.13)),
            "walking": (("idle", 0.68), ("running", 0.32)),
            "running": (("walking", 1.0),),
            "resting": (("idle", 0.72), ("walking", 0.28)),
            "eating": (("resting", 1.0),),
        },
    ),
    "dog": SpeciesProfile(
        durations_ms={
            "idle": (4_000, 8_000),
            "walking": (7_000, 16_000),
            "running": (2_800, 5_600),
            "resting": (10_000, 24_000),
            "eating": (5_000, 6_200),
        },
        walk_speed_px_s=(11.0, 16.0),
        run_speed_px_s=(27.0, 36.0),
        transitions={
            "idle": (("resting", 0.30), ("walking", 0.53), ("running", 0.17)),
            "walking": (("idle", 0.62), ("running", 0.38)),
            "running": (("walking", 1.0),),
            "resting": (("idle", 0.62), ("walking", 0.38)),
            "eating": (("resting", 1.0),),
        },
    ),
}


@dataclass(frozen=True)
class BehaviorDecision:
    state: str
    mode: str
    changed: bool
    target_speed_px_s: float


def mode_to_state(mode: str) -> str:
    """Convert a persisted UI mode into an internal behavior state."""
    return MODE_TO_STATE.get(mode, "idle")


class BehaviorScheduler:
    """Choose bounded, non-repeating behavior sequences using an injected RNG."""

    def __init__(
        self,
        species: str,
        initial_mode: str = "free",
        rng: random.Random | None = None,
    ) -> None:
        if species not in PROFILES:
            raise ValueError(f"Unsupported species behavior profile: {species}")
        self.profile = PROFILES[species]
        self.rng = rng or random.Random()
        self.state = mode_to_state(initial_mode)
        self.remaining_ms = 0
        self.phase_duration_ms = 0
        self.target_speed_px_s = 0.0
        self.post_meal_run_block_ms = 0
        self.recent_states: deque[str] = deque(maxlen=5)
        self._enter(self.state)

    @property
    def mode(self) -> str:
        return STATE_TO_MODE[self.state]

    @property
    def walk_speed_px_s(self) -> float:
        return sum(self.profile.walk_speed_px_s) / 2

    def sync_external_mode(self, mode: str) -> BehaviorDecision:
        """Apply a user or domain action, resetting its full minimum duration."""
        state = mode_to_state(mode)
        changed = state != self.state
        if self.state == "eating" and state != "eating":
            self._start_post_meal_cooldown()
        self._enter(state)
        return self._decision(changed)

    def force_state(
        self,
        state: str,
        *,
        duration_ms: int | None = None,
    ) -> BehaviorDecision:
        """Start a behavior immediately; used by explicit overlay controls."""
        if state not in ALL_STATES:
            raise ValueError(f"Unknown behavior state: {state}")
        if state == "running" and self.state == "eating":
            state = "resting"
        elif state == "running" and self.post_meal_run_block_ms:
            state = "walking"
        changed = state != self.state
        if self.state == "eating" and state != "eating":
            self._start_post_meal_cooldown()
        self._enter(state, duration_ms)
        return self._decision(changed)

    def keep_resting(self) -> BehaviorDecision:
        """Hold a retired pet in a quiet state without restarting its animation."""
        changed = self.state != "resting"
        if changed:
            self._enter("resting")
        return self._decision(changed)

    def advance(self, delta_ms: int) -> BehaviorDecision:
        if delta_ms < 0:
            raise ValueError("Behavior time cannot move backwards")
        self.post_meal_run_block_ms = max(0, self.post_meal_run_block_ms - delta_ms)
        if self.state == "caged" or delta_ms == 0:
            return self._decision(False)

        self.remaining_ms -= delta_ms
        changed = False
        transition_guard = 0
        while self.remaining_ms <= 0 and transition_guard < 8:
            overflow_ms = -self.remaining_ms
            previous = self.state
            next_state = self._choose_next_state()
            if previous == "eating":
                self._start_post_meal_cooldown()
            self._enter(next_state)
            self.remaining_ms -= overflow_ms
            changed = True
            transition_guard += 1
        return self._decision(changed)

    def _choose_next_state(self) -> str:
        candidates = list(self.profile.transitions[self.state])
        if self.post_meal_run_block_ms:
            candidates = [(state, weight) for state, weight in candidates if state != "running"]
        if not candidates:
            return "idle"

        recent = tuple(self.recent_states)
        adjusted: list[tuple[str, float]] = []
        for candidate, weight in candidates:
            if recent and candidate == recent[-1]:
                weight *= 0.12
            elif candidate in recent[-3:]:
                weight *= 0.45
            adjusted.append((candidate, weight))
        states, weights = zip(*adjusted, strict=True)
        return self.rng.choices(states, weights=weights, k=1)[0]

    def _enter(self, state: str, duration_ms: int | None = None) -> None:
        if state not in ALL_STATES:
            raise ValueError(f"Unknown behavior state: {state}")
        self.state = state
        self.recent_states.append(state)
        if state == "caged":
            self.phase_duration_ms = 0
            self.remaining_ms = 0
            self.target_speed_px_s = 0.0
            return

        low, high = self.profile.durations_ms[state]
        selected_duration = duration_ms if duration_ms is not None else self.rng.randint(low, high)
        if selected_duration <= 0:
            raise ValueError("Behavior duration must be positive")
        self.phase_duration_ms = selected_duration
        self.remaining_ms = selected_duration
        if state == "walking":
            self.target_speed_px_s = self.rng.uniform(*self.profile.walk_speed_px_s)
        elif state == "running":
            self.target_speed_px_s = self.rng.uniform(*self.profile.run_speed_px_s)
        else:
            self.target_speed_px_s = 0.0

    def _start_post_meal_cooldown(self) -> None:
        self.post_meal_run_block_ms = max(
            self.post_meal_run_block_ms,
            self.rng.randint(18_000, 32_000),
        )

    def _decision(self, changed: bool) -> BehaviorDecision:
        return BehaviorDecision(
            state=self.state,
            mode=self.mode,
            changed=changed,
            target_speed_px_s=self.target_speed_px_s,
        )
