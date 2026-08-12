import unittest

from codepet.domain import create_household
from codepet.rewards import ActivityEvent, apply_activity, reward_event


class RewardTests(unittest.TestCase):
    def make_household(self):
        return create_household("Byte", "cat", "Ragdoll", 365)

    def test_commit_and_pull_request_drop_five_to_ten_coins(self):
        for kind in ("commit", "pull_request"):
            for index in range(100):
                reward = reward_event(ActivityEvent(f"{kind}:{index}", kind))
                self.assertTrue(5 <= reward.coins <= 10)

    def test_repository_drops_one_to_three_coins(self):
        for index in range(100):
            reward = reward_event(ActivityEvent(f"repository:{index}", "repository"))
            self.assertTrue(1 <= reward.coins <= 3)

    def test_commit_food_drop_rate_is_twenty_percent(self):
        rewards = [reward_event(ActivityEvent(f"commit:{index}", "commit")) for index in range(5000)]
        rate = sum(reward.food_id is not None for reward in rewards) / len(rewards)
        self.assertAlmostEqual(rate, 0.20, delta=0.025)

    def test_rewards_are_deterministic(self):
        event = ActivityEvent("commit:same", "commit")
        self.assertEqual(reward_event(event), reward_event(event))

    def test_duplicate_events_are_not_rewarded_twice(self):
        household = self.make_household()
        event = ActivityEvent("commit:abc", "commit")
        first = apply_activity(household, [event, event])
        second = apply_activity(household, [event])
        self.assertEqual(len(first), 1)
        self.assertEqual(second, [])

    def test_reward_goes_only_to_active_pet(self):
        household = self.make_household()
        first_pet = household.active_pet
        second_pet = household.adopt("Patch", "dog", "German Shepherd", 365)
        household.select_pet(second_pet.id)
        apply_activity(household, [ActivityEvent("commit:one", "commit")])
        self.assertEqual(first_pet.total_xp, 0)
        self.assertGreater(second_pet.total_xp, 0)


if __name__ == "__main__":
    unittest.main()
