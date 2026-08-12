import random
import unittest

from codepet.behavior import PROFILES, BehaviorScheduler


class BehaviorSchedulerTests(unittest.TestCase):
    def test_long_simulation_never_sticks_or_repeats_a_phase(self):
        scheduler = BehaviorScheduler("cat", "free", random.Random(42))
        phases = [scheduler.state]
        for _ in range(2_000):
            decision = scheduler.advance(scheduler.remaining_ms)
            self.assertTrue(decision.changed)
            self.assertNotEqual(phases[-1], decision.state)
            phases.append(decision.state)

        self.assertTrue({"idle", "walking", "running", "resting"}.issubset(phases))

    def test_every_natural_phase_has_a_bounded_duration(self):
        scheduler = BehaviorScheduler("dog", "free", random.Random(7))
        for _ in range(180):
            low, high = PROFILES["dog"].durations_ms[scheduler.state]
            self.assertGreaterEqual(scheduler.phase_duration_ms, low)
            self.assertLessEqual(scheduler.phase_duration_ms, high)
            scheduler.advance(scheduler.remaining_ms)

    def test_running_always_slows_to_walking(self):
        scheduler = BehaviorScheduler("dog", "running", random.Random(19))
        for _ in range(80):
            previous = scheduler.state
            scheduler.advance(scheduler.remaining_ms)
            if previous == "running":
                self.assertEqual(scheduler.state, "walking")

    def test_eating_is_followed_by_rest_and_blocks_immediate_running(self):
        scheduler = BehaviorScheduler("cat", "eating", random.Random(3))
        scheduler.advance(scheduler.remaining_ms)
        self.assertEqual(scheduler.state, "resting")
        self.assertGreater(scheduler.post_meal_run_block_ms, 0)
        decision = scheduler.force_state("running")
        self.assertEqual(decision.state, "walking")

    def test_cage_holds_until_the_user_releases_the_pet(self):
        scheduler = BehaviorScheduler("cat", "caged", random.Random(1))
        self.assertFalse(scheduler.advance(3_600_000).changed)
        self.assertEqual(scheduler.state, "caged")
        self.assertEqual(scheduler.force_state("idle").state, "idle")

    def test_a_run_cannot_cross_a_typical_desktop_in_one_phase(self):
        for profile in PROFILES.values():
            longest_run_ms = profile.durations_ms["running"][1]
            fastest_run_px_s = profile.run_speed_px_s[1]
            self.assertLess(fastest_run_px_s * longest_run_ms / 1000, 220)

    def test_negative_time_is_rejected(self):
        with self.assertRaises(ValueError):
            BehaviorScheduler("cat").advance(-1)


if __name__ == "__main__":
    unittest.main()
