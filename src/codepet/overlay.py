"""Transparent, interactive pet overlay window."""

from __future__ import annotations

import random
from collections.abc import Callable

from PySide6.QtCore import QElapsedTimer, QPoint, QRect, Qt, QTimer
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QTransform
from PySide6.QtWidgets import QApplication, QMenu, QWidget

from .animation import MODE_ACTIONS, Animator
from .behavior import BehaviorDecision, BehaviorScheduler
from .domain import Household, Pet
from .sprites import SpriteSheet

TICK_INTERVAL_MS = 40
MAX_TICK_MS = 200
ACCELERATION_PX_S2 = 28.0
DECELERATION_PX_S2 = 38.0


class PetOverlay(QWidget):
    def __init__(
        self,
        household: Household,
        pet: Pet,
        sprites: SpriteSheet,
        on_change: Callable[[], None],
        on_dashboard: Callable[[], None],
        on_sync: Callable[[], None],
        index: int,
    ) -> None:
        super().__init__()
        self.household = household
        self.pet = pet
        self.sprites = sprites
        self.on_change = on_change
        self.on_dashboard = on_dashboard
        self.on_sync = on_sync
        self.index = index
        self.drag_offset: QPoint | None = None
        self.direction = -1
        self.rng = random.Random()
        self.behavior = BehaviorScheduler(pet.species, pet.mode, self.rng)
        self.animator = Animator(MODE_ACTIONS.get(self.behavior.mode, "idle"))
        self.bubble = ""
        self.position_x = 0.0
        self.current_speed_px_s = 0.0
        self.motion_target_px_s = self.behavior.target_speed_px_s
        self.turn_pending = False
        self.affection_pending = False

        # A 128-pixel square keeps the atlas crisp and the desktop footprint modest.
        self.setFixedSize(196, 174)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self._animate)
        self.animation_timer.start(TICK_INTERVAL_MS)
        self.elapsed_timer = QElapsedTimer()
        self.elapsed_timer.start()
        self.mood_timer = QTimer(self)
        self.mood_timer.timeout.connect(self._show_contextual_mood)
        self.mood_timer.start(15_000)
        self.move_to_rest_position()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        if self.pet.mode == "caged":
            self._draw_cage(painter)
        sprite = self.sprites.frame(self.pet, self.animator.action, self.animator.frame_index)
        if self.direction < 0:
            sprite = sprite.transformed(QTransform().scale(-1, 1))
        painter.drawPixmap(QRect(28, 40, 128, 128), sprite)
        if self.bubble:
            self._draw_mood_bubble(painter)

    def _draw_cage(self, painter: QPainter) -> None:
        painter.setPen(QPen(QColor("#775c45"), 4))
        painter.drawRoundedRect(12, 33, 171, 137, 12, 12)
        for x in range(33, 176, 24):
            painter.drawLine(x, 37, x, 166)

    def _draw_mood_bubble(self, painter: QPainter) -> None:
        painter.setPen(QPen(QColor("#9b8d80"), 2))
        painter.setBrush(QColor(255, 253, 248, 245))
        painter.drawEllipse(QRect(127, 3, 58, 48))
        painter.drawEllipse(QRect(122, 46, 11, 9))
        painter.setPen(QColor("#292522"))
        painter.setFont(QFont("Apple Color Emoji", 20))
        painter.drawText(QRect(130, 6, 52, 40), Qt.AlignmentFlag.AlignCenter, self.bubble)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.household.select_pet(self.pet.id)
            self.drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.pet.pet_with_cursor()
            decision = self.behavior.force_state("idle")
            self._apply_behavior(decision)
            self.affection_pending = True
            self.motion_target_px_s = 0.0
            self.show_bubble("🥰")
            self.on_change()

    def mouseMoveEvent(self, event) -> None:
        if self.drag_offset and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_offset)
            self.position_x = float(self.x())

    def mouseReleaseEvent(self, event) -> None:
        self.drag_offset = None
        self.position_x = float(self.x())
        self.on_change()

    def contextMenuEvent(self, event) -> None:
        menu = QMenu(self)
        menu.addAction("Open CodePet Home", self.on_dashboard)
        menu.addAction("Sync GitHub", self.on_sync)
        menu.addSeparator()
        menu.addAction("Rest here", self.rest)
        menu.addAction("Take a walk", self.walk)
        menu.addAction("Run for a while", self.run)
        menu.addAction("Resume natural behavior", self.free_roam)
        menu.addAction("Return to cage", self.cage)
        menu.addSeparator()
        menu.addAction("Hide pets", self.hide_household)
        menu.exec(event.globalPos())

    def show_bubble(self, emoji: str, duration_ms: int = 2600) -> None:
        self.bubble = emoji
        self.update()
        QTimer.singleShot(duration_ms, self.clear_bubble)

    def clear_bubble(self) -> None:
        self.bubble = ""
        self.update()

    def _show_contextual_mood(self) -> None:
        if self.pet.needs_attention or self.rng.random() < 0.25:
            self.show_bubble(self.pet.mood_emoji, 4200 if self.pet.needs_attention else 2200)

    def cage(self) -> None:
        self._apply_behavior(self.behavior.force_state("caged"))
        self.show_bubble("🏠")
        self.on_change()

    def rest(self) -> None:
        self._apply_behavior(self.behavior.force_state("resting"))
        self.show_bubble("💤")
        self.on_change()

    def walk(self) -> None:
        self._apply_behavior(self.behavior.force_state("walking"))
        self.show_bubble("✨")
        self.on_change()

    def run(self) -> None:
        self._apply_behavior(self.behavior.force_state("running"))
        self.show_bubble("⚡")
        self.on_change()

    def free_roam(self) -> None:
        self._apply_behavior(self.behavior.force_state("idle"))
        self.show_bubble("🌿")
        self.on_change()

    def move_to_rest_position(self) -> None:
        screen = QApplication.primaryScreen().availableGeometry()
        offset = self.index * (self.width() - 36)
        self.move(screen.right() - self.width() - 25 - offset, screen.top() + 4)
        self.position_x = float(self.x())

    def _animate(self) -> None:
        delta_ms = max(0, min(self.elapsed_timer.restart(), MAX_TICK_MS))
        if self.pet.is_retired:
            decision = self.behavior.keep_resting()
            self._apply_behavior(decision)
        elif self.pet.mode != self.behavior.mode:
            decision = self.behavior.sync_external_mode(self.pet.mode)
            self._apply_behavior(decision)
        else:
            expected_action = MODE_ACTIONS.get(self.behavior.mode, "idle")
            behavior_delta_ms = delta_ms if self.animator.action == expected_action else 0
            decision = self.behavior.advance(behavior_delta_ms)
            self._apply_behavior(decision)

        self._request_animation(decision.mode)
        requested_speed = decision.target_speed_px_s
        self.motion_target_px_s = min(requested_speed, self.motion_target_px_s)

        previous_action = self.animator.action
        frame_changed = self.animator.advance(delta_ms)
        if self.animator.action != previous_action:
            self._activate_motion_for_current_action(decision)

        moved = self._advance_movement(delta_ms)
        if frame_changed or moved:
            self.update()

    def _apply_behavior(self, decision: BehaviorDecision) -> None:
        self.pet.mode = decision.mode
        self.motion_target_px_s = min(decision.target_speed_px_s, self.motion_target_px_s)

    def _activate_motion_for_current_action(self, decision: BehaviorDecision) -> None:
        if self.animator.action == "walking":
            self.motion_target_px_s = (
                decision.target_speed_px_s
                if decision.state == "walking"
                else self.behavior.walk_speed_px_s
            )
        elif self.animator.action == "running":
            self.motion_target_px_s = (
                decision.target_speed_px_s
                if decision.state == "running"
                else self.current_speed_px_s
            )
        else:
            self.motion_target_px_s = 0.0

    def _request_animation(self, mode: str) -> None:
        target_action = MODE_ACTIONS.get(mode, "idle")
        locomotion = {"walking", "running"}
        if self.animator.action in locomotion and target_action not in locomotion:
            if self.current_speed_px_s > 0.05:
                return
            if self.affection_pending:
                self.animator.queue_action("affection", return_action=target_action)
                self.affection_pending = False
                return
            self.animator.queue_action("idle")
            return
        if self.affection_pending and self.current_speed_px_s <= 0.05:
            self.animator.queue_action("affection", return_action=target_action)
            self.affection_pending = False
        self.animator.follow_mode(mode)

    def _advance_movement(self, delta_ms: int) -> bool:
        if self.drag_offset is not None or delta_ms == 0:
            return False
        screen = QApplication.screenAt(self.frameGeometry().center()) or QApplication.primaryScreen()
        bounds = screen.availableGeometry()
        left = float(bounds.left())
        right = float(bounds.right() - self.width() + 1)
        distance_to_edge = (
            right - self.position_x if self.direction > 0 else self.position_x - left
        )
        braking_distance = self.current_speed_px_s**2 / (2 * DECELERATION_PX_S2) + 2
        if (
            not self.turn_pending
            and self.current_speed_px_s > 0
            and distance_to_edge <= braking_distance
        ):
            self.turn_pending = True
            pause_ms = self.rng.randint(1_200, 2_600)
            self._apply_behavior(self.behavior.force_state("idle", duration_ms=pause_ms))
            self._request_animation(self.pet.mode)
            self.motion_target_px_s = 0.0

        acceleration = (
            ACCELERATION_PX_S2
            if self.motion_target_px_s > self.current_speed_px_s
            else DECELERATION_PX_S2
        )
        max_change = acceleration * delta_ms / 1000
        self.current_speed_px_s = _approach(
            self.current_speed_px_s,
            self.motion_target_px_s,
            max_change,
        )
        if self.current_speed_px_s < 0.05:
            self.current_speed_px_s = 0.0
            if self.turn_pending:
                self.direction *= -1
                self.turn_pending = False
            return False

        self.position_x += self.direction * self.current_speed_px_s * delta_ms / 1000
        hit_edge = self.position_x < left or self.position_x > right
        if hit_edge:
            self.position_x = max(left, min(right, self.position_x))
            if self.behavior.state != "idle":
                pause_ms = self.rng.randint(1_200, 2_600)
                self._apply_behavior(self.behavior.force_state("idle", duration_ms=pause_ms))
                self._request_animation(self.pet.mode)
            self.turn_pending = True
            self.motion_target_px_s = 0.0
        self.move(round(self.position_x), self.y())
        return True

    def hide_household(self) -> None:
        self.household.visible = False
        self.on_change()

    def refresh(self) -> None:
        self.update()


def _approach(current: float, target: float, maximum_change: float) -> float:
    if current < target:
        return min(target, current + maximum_change)
    return max(target, current - maximum_change)
