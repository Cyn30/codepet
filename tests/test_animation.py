import unittest

from codepet.animation import Animator


class AnimatorTests(unittest.TestCase):
    def test_walk_animation_loops(self):
        animator = Animator("walking")
        animator.advance(105 * 8)
        self.assertEqual(animator.action, "walking")
        self.assertEqual(animator.frame_index, 0)

    def test_affection_returns_to_previous_action(self):
        animator = Animator("walking")
        animator.set_action("affection", return_action="walking")
        animator.advance(135 * 8)
        self.assertEqual(animator.action, "walking")
        self.assertEqual(animator.frame_index, 0)

    def test_follow_mode_does_not_interrupt_affection(self):
        animator = Animator("affection")
        animator.follow_mode("running")
        self.assertEqual(animator.action, "affection")
        animator.advance(135 * 8)
        self.assertEqual(animator.action, "running")

    def test_mode_change_waits_for_a_complete_animation_loop(self):
        animator = Animator("running")
        animator.advance(200)
        animator.follow_mode("resting")
        self.assertEqual(animator.action, "running")
        animator.advance(399)
        self.assertEqual(animator.action, "running")
        animator.advance(1)
        self.assertEqual(animator.action, "sleeping")
        self.assertEqual(animator.frame_index, 0)

    def test_latest_queued_action_replaces_an_obsolete_transition(self):
        animator = Animator("walking")
        animator.follow_mode("running")
        animator.follow_mode("free")
        animator.advance(105 * 8)
        self.assertEqual(animator.action, "idle")

    def test_large_tick_preserves_overflow_in_the_new_action(self):
        animator = Animator("running")
        animator.follow_mode("walking")
        animator.advance(600 + 210)
        self.assertEqual(animator.action, "walking")
        self.assertEqual(animator.frame_index, 2)

    def test_queued_affection_waits_for_boundary_then_returns_to_idle(self):
        animator = Animator("running")
        animator.advance(300)
        animator.queue_action("affection", return_action="idle")
        animator.follow_mode("free")
        animator.advance(299)
        self.assertEqual(animator.action, "running")
        animator.advance(1)
        self.assertEqual(animator.action, "affection")
        animator.advance(135 * 8)
        self.assertEqual(animator.action, "idle")

    def test_negative_time_is_rejected(self):
        with self.assertRaises(ValueError):
            Animator().advance(-1)


if __name__ == "__main__":
    unittest.main()
