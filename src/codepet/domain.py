"""Pure, deterministic domain model for CodePet."""

from __future__ import annotations

import math
import random
import uuid
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timezone

from .catalog import FOODS

MIN_LIFESPAN_DAYS = 14
MAX_LIFESPAN_DAYS = 3650
MAX_PETS = 2

BREEDS: dict[str, tuple[str, ...]] = {
    "cat": ("Ragdoll", "Devon Rex", "Golden Shaded"),
    "dog": ("Golden Retriever", "German Shepherd", "Scottish Collie"),
}

BOND_RANKS = (
    (900, "Soulmates"),
    (500, "Best Friends"),
    (250, "Friends"),
    (100, "Familiar"),
    (0, "New Friends"),
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def local_today() -> date:
    return datetime.now().astimezone().date()


def xp_required(level: int) -> int:
    if level < 1:
        raise ValueError("Level must be at least 1")
    return int(80 * math.pow(level, 1.55))


def clamp(value: int, minimum: int = 0, maximum: int = 100) -> int:
    return max(minimum, min(maximum, value))


@dataclass
class Pet:
    id: str
    name: str
    species: str
    breed: str
    born_on: str
    lifespan_days: int = 365
    level: int = 1
    xp: int = 0
    total_xp: int = 0
    hunger: int = 20
    happiness: int = 70
    energy: int = 75
    bond: int = 0
    mode: str = "resting"
    last_fed_at: str | None = None
    last_played_at: str | None = None

    def __post_init__(self) -> None:
        if self.species not in BREEDS:
            raise ValueError(f"Unsupported species: {self.species}")
        if self.breed not in BREEDS[self.species]:
            raise ValueError(f"Unsupported {self.species} breed: {self.breed}")
        if not MIN_LIFESPAN_DAYS <= self.lifespan_days <= MAX_LIFESPAN_DAYS:
            raise ValueError(
                f"Lifespan must be between {MIN_LIFESPAN_DAYS} and {MAX_LIFESPAN_DAYS} days"
            )

    @property
    def stage(self) -> str:
        if self.is_retired:
            return "Cherished Memory"
        if self.level >= 20:
            return "Legend"
        if self.level >= 10:
            return "Companion"
        if self.level >= 4:
            return "Explorer"
        return "Tiny Sprout"

    @property
    def next_level_xp(self) -> int:
        return xp_required(self.level)

    @property
    def bond_rank(self) -> str:
        return next(name for threshold, name in BOND_RANKS if self.bond >= threshold)

    @property
    def mood_emoji(self) -> str:
        if self.is_retired:
            return "🌈"
        if self.hunger >= 85 or self.happiness <= 20:
            return "😿" if self.species == "cat" else "🥺"
        if self.hunger >= 65 or self.happiness <= 40:
            return "😟"
        if self.energy <= 20:
            return "😴"
        if self.happiness >= 85 and self.bond >= 250:
            return "🥰"
        if self.happiness >= 70:
            return "😊"
        return "🙂"

    @property
    def needs_attention(self) -> bool:
        return not self.is_retired and (
            self.hunger >= 65 or self.happiness <= 40 or self.energy <= 20
        )

    @property
    def is_retired(self) -> bool:
        return self.days_remaining() == 0

    def age_days(self, today: date | None = None) -> int:
        return max(0, ((today or local_today()) - date.fromisoformat(self.born_on)).days)

    def days_remaining(self, today: date | None = None) -> int:
        return max(0, self.lifespan_days - self.age_days(today))

    def gain_xp(self, amount: int) -> int:
        if amount < 0:
            raise ValueError("XP cannot be negative")
        levels_gained = 0
        self.xp += amount
        self.total_xp += amount
        while self.xp >= self.next_level_xp:
            self.xp -= self.next_level_xp
            self.level += 1
            levels_gained += 1
        return levels_gained

    def change_bond(self, amount: int) -> int:
        previous = self.bond
        self.bond = clamp(self.bond + amount, 0, 9999)
        return self.bond - previous

    def pet_with_cursor(self, rng: random.Random | None = None) -> int:
        self._require_active()
        gained = (rng or random).randint(1, 2)
        self.change_bond(gained)
        self.happiness = clamp(self.happiness + 3)
        return gained

    def play(self, rng: random.Random | None = None) -> int:
        self._require_active()
        if self.energy < 10:
            raise ValueError("Your pet is too tired to play")
        gained = (rng or random).randint(2, 4)
        self.change_bond(gained)
        self.energy = clamp(self.energy - 10)
        self.hunger = clamp(self.hunger + 8)
        self.happiness = clamp(self.happiness + 12)
        self.last_played_at = utc_now().isoformat()
        return gained

    def feed(self, food_id: str, rng: random.Random | None = None) -> int:
        self._require_active()
        food = FOODS[food_id]
        low, high = food.bond_range(self.species)
        bond_change = (rng or random).randint(low, high)
        self.change_bond(bond_change)
        self.hunger = clamp(self.hunger - food.hunger_restore)
        self.happiness = clamp(self.happiness + max(0, bond_change))
        self.last_fed_at = utc_now().isoformat()
        self.mode = "eating"
        return bond_change

    def apply_elapsed_hours(self, hours: int) -> None:
        if self.is_retired:
            return
        periods = max(0, min(hours // 6, 28))
        if periods == 0:
            return
        self.hunger = clamp(self.hunger + periods * 4)
        self.happiness = clamp(self.happiness - periods * 2)
        self.energy = clamp(self.energy + periods * 5)
        if self.hunger >= 80:
            self.change_bond(-min(8, periods))

    def _require_active(self) -> None:
        if self.is_retired:
            raise ValueError("This pet has retired to the memory book")


@dataclass
class Household:
    pets: list[Pet] = field(default_factory=list)
    active_pet_id: str | None = None
    coins: int = 0
    inventory: dict[str, int] = field(default_factory=dict)
    processed_events: list[str] = field(default_factory=list)
    active_days: list[str] = field(default_factory=list)
    last_sync_at: str | None = None
    last_tick_at: str = field(default_factory=lambda: utc_now().isoformat())
    visible: bool = True

    @property
    def active_pet(self) -> Pet:
        if not self.pets:
            raise ValueError("Adopt a pet first")
        pet = next((item for item in self.pets if item.id == self.active_pet_id), None)
        return pet or self.pets[0]

    @property
    def streak(self) -> int:
        unique_days = {date.fromisoformat(item) for item in self.active_days}
        if not unique_days:
            return 0
        cursor = local_today()
        if cursor not in unique_days:
            cursor = date.fromordinal(cursor.toordinal() - 1)
        streak = 0
        while cursor in unique_days:
            streak += 1
            cursor = date.fromordinal(cursor.toordinal() - 1)
        return streak

    def adopt(self, name: str, species: str, breed: str, lifespan_days: int) -> Pet:
        if len(self.pets) >= MAX_PETS:
            raise ValueError(f"A household can have at most {MAX_PETS} pets")
        clean_name = name.strip()
        if not clean_name or len(clean_name) > 24:
            raise ValueError("Pet name must contain 1 to 24 characters")
        pet = Pet(
            id=uuid.uuid4().hex,
            name=clean_name,
            species=species,
            breed=breed,
            born_on=local_today().isoformat(),
            lifespan_days=lifespan_days,
        )
        self.pets.append(pet)
        self.active_pet_id = pet.id
        return pet

    def select_pet(self, pet_id: str) -> None:
        if not any(pet.id == pet_id for pet in self.pets):
            raise ValueError("Pet does not belong to this household")
        self.active_pet_id = pet_id

    def buy(self, food_id: str, quantity: int = 1) -> None:
        if food_id not in FOODS or quantity < 1:
            raise ValueError("Invalid shop purchase")
        cost = FOODS[food_id].price * quantity
        if self.coins < cost:
            raise ValueError("Not enough coins")
        self.coins -= cost
        self.inventory[food_id] = self.inventory.get(food_id, 0) + quantity

    def feed_active_pet(self, food_id: str, rng: random.Random | None = None) -> int:
        if self.inventory.get(food_id, 0) < 1:
            raise ValueError("This food is not in your inventory")
        change = self.active_pet.feed(food_id, rng)
        self.inventory[food_id] -= 1
        return change

    def apply_time_decay(self, now: datetime | None = None) -> None:
        now = now or utc_now()
        previous = datetime.fromisoformat(self.last_tick_at)
        hours = int(max(0, (now - previous).total_seconds()) // 3600)
        if hours:
            for pet in self.pets:
                pet.apply_elapsed_hours(hours)
            self.last_tick_at = now.isoformat()

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, raw: dict) -> Household:
        if "pets" not in raw:
            return cls._migrate_legacy(raw)
        return cls(
            pets=[Pet(**item) for item in raw.get("pets", [])],
            active_pet_id=raw.get("active_pet_id"),
            coins=int(raw.get("coins", 0)),
            inventory={key: int(value) for key, value in raw.get("inventory", {}).items()},
            processed_events=list(raw.get("processed_events", [])),
            active_days=list(raw.get("active_days", [])),
            last_sync_at=raw.get("last_sync_at"),
            last_tick_at=raw.get("last_tick_at", utc_now().isoformat()),
            visible=bool(raw.get("visible", True)),
        )

    @classmethod
    def _migrate_legacy(cls, raw: dict) -> Household:
        pet_raw = dict(raw.get("pet", {}))
        legacy_inventory = pet_raw.pop("inventory", {})
        pet = Pet(
            id=uuid.uuid4().hex,
            name=pet_raw.get("name", "Byte"),
            species=pet_raw.get("species", "cat"),
            breed=pet_raw.get("breed", "Ragdoll"),
            born_on=pet_raw.get("born_on", local_today().isoformat()),
            lifespan_days=int(pet_raw.get("lifespan_days", 365)),
            level=int(pet_raw.get("level", 1)),
            xp=int(pet_raw.get("xp", pet_raw.get("experience", 0))),
            total_xp=int(pet_raw.get("total_xp", pet_raw.get("experience", 0))),
            hunger=int(pet_raw.get("hunger", 20)),
            happiness=int(pet_raw.get("happiness", 70)),
            energy=int(pet_raw.get("energy", 75)),
            mode=pet_raw.get("mode", "resting"),
        )
        inventory: dict[str, int] = {}
        legacy_food = int(legacy_inventory.get("food", 0)) if isinstance(legacy_inventory, dict) else 0
        if legacy_food:
            inventory["chicken"] = legacy_food
        return cls(
            pets=[pet],
            active_pet_id=pet.id,
            inventory=inventory,
            processed_events=list(raw.get("processed_commits", [])),
            active_days=list(raw.get("active_days", [])),
            last_sync_at=raw.get("last_sync_at"),
            visible=bool(raw.get("visible", True)),
        )


def create_household(
    name: str, species: str, breed: str, lifespan_days: int
) -> Household:
    household = Household()
    household.adopt(name, species, breed, lifespan_days)
    return household
