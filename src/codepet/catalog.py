"""Immutable gameplay catalog data.

Keeping item definitions here prevents the UI and reward system from inventing
their own prices or feeding rules.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Food:
    id: str
    name: str
    price: int
    hunger_restore: int
    bond_by_species: dict[str, tuple[int, int]]

    def bond_range(self, species: str) -> tuple[int, int]:
        return self.bond_by_species.get(species, (0, 0))


FOODS: dict[str, Food] = {
    "cat_food": Food("cat_food", "Cat Food", 15, 24, {"cat": (3, 5), "dog": (-2, 0)}),
    "dog_food": Food("dog_food", "Dog Food", 15, 24, {"dog": (3, 5), "cat": (-2, 0)}),
    "bone": Food("bone", "Chew Bone", 25, 18, {"dog": (5, 7), "cat": (-3, 0)}),
    "chicken": Food("chicken", "Cooked Chicken", 35, 30, {"cat": (4, 7), "dog": (4, 7)}),
    "salmon": Food("salmon", "Salmon", 45, 34, {"cat": (7, 10), "dog": (3, 6)}),
    "tuna": Food("tuna", "Tuna", 60, 38, {"cat": (9, 13), "dog": (1, 4)}),
    "feast": Food("feast", "Celebration Feast", 100, 55, {"cat": (10, 14), "dog": (10, 14)}),
}

FOOD_DROP_POOL = ("cat_food", "dog_food", "bone", "chicken", "salmon")
