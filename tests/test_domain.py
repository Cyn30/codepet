import random
import unittest
from datetime import datetime, timedelta, timezone

from codepet.catalog import FOODS
from codepet.domain import BREEDS, Household, Pet, create_household, xp_required


class DomainTests(unittest.TestCase):
    def make_household(self) -> Household:
        return create_household("Byte", "cat", "Ragdoll", 365)

    def test_xp_curve_strictly_increases(self):
        requirements = [xp_required(level) for level in range(1, 30)]
        self.assertEqual(requirements, sorted(requirements))
        self.assertEqual(len(requirements), len(set(requirements)))

    def test_multiple_level_ups_keep_remaining_xp(self):
        pet = self.make_household().active_pet
        gained = pet.gain_xp(xp_required(1) + xp_required(2) + 7)
        self.assertEqual((gained, pet.level, pet.xp), (2, 3, 7))

    def test_lifespan_cannot_be_shorter_than_fourteen_days(self):
        with self.assertRaisesRegex(ValueError, "between 14"):
            create_household("Byte", "dog", "Golden Retriever", 2)

    def test_household_supports_at_most_two_pets(self):
        household = self.make_household()
        household.adopt("Patch", "dog", "Scottish Collie", 365)
        with self.assertRaisesRegex(ValueError, "at most 2"):
            household.adopt("Third", "cat", "Devon Rex", 365)

    def test_cursor_pet_increases_bond_by_one_or_two(self):
        pet = self.make_household().active_pet
        gained = pet.pet_with_cursor(random.Random(3))
        self.assertIn(gained, (1, 2))
        self.assertEqual(pet.bond, gained)

    def test_bond_rank_thresholds(self):
        pet = self.make_household().active_pet
        expected = {0: "New Friends", 100: "Familiar", 250: "Friends", 500: "Best Friends", 900: "Soulmates"}
        for bond, rank in expected.items():
            pet.bond = bond
            self.assertEqual(pet.bond_rank, rank)

    def test_species_food_preferences(self):
        cat = self.make_household().active_pet
        cat_bone_change = cat.feed("bone", random.Random(1))
        cat_salmon_change = cat.feed("salmon", random.Random(1))
        dog = create_household("Patch", "dog", "Golden Retriever", 365).active_pet
        dog_salmon_change = dog.feed("salmon", random.Random(1))
        self.assertLessEqual(cat_bone_change, 0)
        self.assertGreater(cat_salmon_change, dog_salmon_change)

    def test_shop_purchase_and_feed_consume_coins_and_inventory(self):
        household = self.make_household()
        household.coins = 100
        household.buy("salmon")
        self.assertEqual(household.coins, 100 - FOODS["salmon"].price)
        self.assertEqual(household.inventory["salmon"], 1)
        household.feed_active_pet("salmon", random.Random(1))
        self.assertEqual(household.inventory["salmon"], 0)

    def test_time_decay_is_capped_and_can_reduce_bond(self):
        household = self.make_household()
        household.active_pet.bond = 100
        household.active_pet.hunger = 79
        now = datetime.now(timezone.utc)
        household.last_tick_at = (now - timedelta(days=10)).isoformat()
        household.apply_time_decay(now)
        self.assertLess(household.active_pet.bond, 100)
        self.assertLessEqual(household.active_pet.hunger, 100)

    def test_all_breeds_are_valid(self):
        for species, breeds in BREEDS.items():
            for breed in breeds:
                household = create_household("Pet", species, breed, 30)
                self.assertIsInstance(household.active_pet, Pet)

    def test_expired_pet_retires_without_deleting_data(self):
        household = self.make_household()
        pet = household.active_pet
        pet.born_on = "2000-01-01"
        pet.lifespan_days = 14
        self.assertTrue(pet.is_retired)
        self.assertEqual(pet.stage, "Cherished Memory")
        self.assertEqual(pet.mood_emoji, "🌈")
        with self.assertRaisesRegex(ValueError, "memory book"):
            pet.play()

    def test_legacy_single_pet_save_is_migrated(self):
        household = Household.from_dict({
            "pet": {
                "name": "Old Byte",
                "species": "cat",
                "breed": "Ragdoll",
                "born_on": datetime.now().astimezone().date().isoformat(),
                "experience": 42,
                "inventory": {"food": 2},
            },
            "processed_commits": ["abc"],
        })
        self.assertEqual(household.active_pet.name, "Old Byte")
        self.assertEqual(household.active_pet.xp, 42)
        self.assertEqual(household.inventory["chicken"], 2)
        self.assertEqual(household.processed_events, ["abc"])


if __name__ == "__main__":
    unittest.main()
