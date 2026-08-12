"""Frame-based animation state that is independent from the desktop UI."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AnimationClip:
    name: str
    frame_count: int
    frame_duration_ms: int
    loops: bool = True

    @property
    def duration_ms(self) -> int:
        return self.frame_count * self.frame_duration_ms


CLIPS: dict[str, AnimationClip] = {
    "idle": AnimationClip("idle", 8, 180),
    "walking": AnimationClip("walking", 8, 105),
    "running": AnimationClip("running", 8, 75),
    "eating": AnimationClip("eating", 8, 130),
    "affection": AnimationClip("affection", 8, 135, loops=False),
    "sleeping": AnimationClip("sleeping", 8, 240),
}

MODE_ACTIONS = {
    "free": "idle",
    "resting": "sleeping",
    "walking": "walking",
    "running": "running",
    "eating": "eating",
    "caged": "idle",
}


class Animator:
    """Advance animation deterministically from elapsed milliseconds."""

    def __init__(self, action: str = "idle") -> None:
        self.action = self._validate(action)
        self.elapsed_ms = 0
        self.return_action = "idle"
        self.pending_action: str | None = None
        self.pending_return_action = "idle"

    @property
    def frame_index(self) -> int:
        clip = CLIPS[self.action]
        raw_frame = self.elapsed_ms // clip.frame_duration_ms
        if clip.loops:
            return raw_frame % clip.frame_count
        return min(raw_frame, clip.frame_count - 1)

    def set_action(self, action: str, *, return_action: str = "idle") -> None:
        """Switch immediately, for direct interactions such as petting."""
        action = self._validate(action)
        return_action = self._validate(return_action)
        if action == self.action:
            self.return_action = return_action
            self.pending_action = None
            if not CLIPS[action].loops:
                self.elapsed_ms = 0
            return
        self.action = action
        self.return_action = return_action
        self.elapsed_ms = 0
        self.pending_action = None

    def queue_action(self, action: str, *, return_action: str = "idle") -> None:
        """Change on the current loop boundary so no pose is cut in half."""
        action = self._validate(action)
        return_action = self._validate(return_action)
        if self.action == "affection":
            if action == "affection":
                self.elapsed_ms = 0
                self.return_action = return_action
            else:
                self.return_action = action
            return
        if self.pending_action == "affection" and action != "affection":
            self.pending_return_action = action
            return
        if action == self.action:
            self.pending_action = None
            return
        self.pending_action = action
        self.pending_return_action = return_action

    def follow_mode(self, mode: str) -> None:
        self.queue_action(MODE_ACTIONS.get(mode, "idle"))

    def advance(self, delta_ms: int) -> bool:
        if delta_ms < 0:
            raise ValueError("Animation time cannot move backwards")
        previous = (self.action, self.frame_index)
        remaining_ms = delta_ms
        while remaining_ms:
            clip = CLIPS[self.action]
            until_boundary = clip.duration_ms - self.elapsed_ms
            if remaining_ms < until_boundary:
                self.elapsed_ms += remaining_ms
                break

            remaining_ms -= until_boundary
            self.elapsed_ms = 0
            if not clip.loops:
                self.action = self.return_action
            elif self.pending_action is not None:
                self.action = self.pending_action
                self.return_action = self.pending_return_action
                self.pending_action = None
        return previous != (self.action, self.frame_index)

    @staticmethod
    def _validate(action: str) -> str:
        if action not in CLIPS:
            raise ValueError(f"Unknown animation action: {action}")
        return action
