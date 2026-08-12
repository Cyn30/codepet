"""Deterministic mapping from GitHub activity to household rewards."""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass
from datetime import date

from .catalog import FOOD_DROP_POOL
from .domain import Household, local_today, utc_now


@dataclass(frozen=True)
class ActivityEvent:
    id: str
    kind: str


@dataclass(frozen=True)
class EventReward:
    event_id: str
    kind: str
    xp: int
    coins: int
    bond: int
    food_id: str | None = None


def _event_rng(event_id: str) -> random.Random:
    digest = hashlib.sha256(event_id.encode("utf-8")).hexdigest()
    return random.Random(int(digest[:16], 16))


def reward_event(event: ActivityEvent) -> EventReward:
    rng = _event_rng(event.id)
    if event.kind == "commit":
        food = rng.choice(FOOD_DROP_POOL) if rng.random() < 0.20 else None
        return EventReward(event.id, event.kind, rng.randint(8, 15), rng.randint(5, 10), rng.randint(1, 5), food)
    if event.kind == "pull_request":
        return EventReward(event.id, event.kind, rng.randint(12, 20), rng.randint(5, 10), rng.randint(2, 5))
    if event.kind == "repository":
        return EventReward(event.id, event.kind, rng.randint(5, 8), rng.randint(1, 3), rng.randint(1, 2))
    raise ValueError(f"Unsupported GitHub activity: {event.kind}")


def apply_activity(
    household: Household,
    events: list[ActivityEvent],
    day: date | None = None,
) -> list[EventReward]:
    known = set(household.processed_events)
    rewards: list[EventReward] = []
    for event in {item.id: item for item in events if item.id}.values():
        if event.id in known:
            continue
        reward = reward_event(event)
        if not household.active_pet.is_retired:
            household.active_pet.gain_xp(reward.xp)
            household.active_pet.change_bond(reward.bond)
        household.coins += reward.coins
        if reward.food_id:
            household.inventory[reward.food_id] = household.inventory.get(reward.food_id, 0) + 1
        household.processed_events.append(event.id)
        known.add(event.id)
        rewards.append(reward)
    household.processed_events = household.processed_events[-10000:]
    if rewards:
        today = (day or local_today()).isoformat()
        if today not in household.active_days:
            household.active_days.append(today)
    household.last_sync_at = utc_now().isoformat()
    return rewards
