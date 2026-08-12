"""Terminal fallback for machines without a graphical environment."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from .domain import BREEDS, create_household
from .github import GitHubError, fetch_recent_activity
from .rewards import apply_activity
from .storage import load, write


def main() -> None:
    household = load()
    if household is None:
        print("Welcome to CodePet.")
        name = input("Pet name [Byte]: ").strip() or "Byte"
        species = input("Species (cat/dog) [cat]: ").strip().lower() or "cat"
        if species not in BREEDS:
            print("Species must be cat or dog.")
            return
        household = create_household(name, species, BREEDS[species][0], 365)
        write(household)

    pet = household.active_pet
    print(f"\n{pet.name} - Level {pet.level} {pet.stage}")
    print(
        f"XP {pet.xp}/{pet.next_level_xp} | Bond {pet.bond} ({pet.bond_rank}) | "
        f"Coins {household.coins} | Streak {household.streak}"
    )
    if input("Sync GitHub activity now? [y/N] ").strip().lower() != "y":
        return

    since = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    try:
        username, events = fetch_recent_activity(since)
        rewards = apply_activity(household, events)
        write(household)
        print(
            f"Synced @{username}: {len(rewards)} new event(s), "
            f"{sum(item.xp for item in rewards)} XP, "
            f"{sum(item.coins for item in rewards)} coins."
        )
    except GitHubError as exc:
        print(f"Sync failed: {exc}")


if __name__ == "__main__":
    main()
