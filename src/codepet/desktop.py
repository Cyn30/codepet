"""Application controller and desktop entry point."""

from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone

try:
    from PySide6.QtCore import Qt, QTimer
    from PySide6.QtGui import QAction, QCursor
    from PySide6.QtWidgets import QApplication, QDialog, QMenu, QMessageBox, QSystemTrayIcon
except ImportError as exc:  # pragma: no cover - optional desktop dependency
    raise SystemExit("Install desktop support with: pip install -e '.[desktop]'") from exc

from .dashboard import AdoptionDialog, DashboardWindow
from .domain import Household
from .github import GitHubError, fetch_recent_activity
from .overlay import PetOverlay
from .rewards import apply_activity
from .sprites import SpriteSheet
from .storage import load, write


class CodePetApplication:
    def __init__(self, app: QApplication, household: Household) -> None:
        self.app = app
        self.household = household
        self.sprites = SpriteSheet()
        self.overlays: list[PetOverlay] = []
        self.tray = QSystemTrayIcon(app)
        self.dashboard = DashboardWindow(
            household,
            self.persist_and_refresh,
            self.adopt_pet,
            self.sync_github,
            self.toggle_visibility,
        )
        self.rebuild_overlays()
        self._configure_tray()
        self.decay_timer = QTimer(app)
        self.decay_timer.timeout.connect(self.apply_time_decay)
        self.decay_timer.start(60_000)

    def _configure_tray(self) -> None:
        self.tray.setToolTip("CodePet")
        menu = QMenu()
        home = QAction("Open CodePet Home", menu)
        home.triggered.connect(self.show_dashboard)
        menu.addAction(home)
        menu.addAction("Show or hide pets", self.toggle_visibility)
        menu.addAction("Sync GitHub", self.sync_github)
        menu.addSeparator()
        menu.addAction("Quit CodePet", self.app.quit)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._tray_activated)
        self.tray.show()

    def _tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show_dashboard()

    def rebuild_overlays(self) -> None:
        for overlay in self.overlays:
            overlay.close()
        self.overlays = [
            PetOverlay(
                self.household,
                pet,
                self.sprites,
                self.persist_and_refresh,
                self.show_dashboard,
                self.sync_github,
                index,
            )
            for index, pet in enumerate(self.household.pets)
        ]
        if self.overlays:
            self.tray.setIcon(self.sprites.frame(self.household.active_pet).scaled(32, 32))
        self._apply_visibility()

    def adopt_pet(self) -> None:
        dialog = AdoptionDialog(self.dashboard)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            self.household.adopt(*dialog.values())
            self.rebuild_overlays()
            self.persist_and_refresh()
        except ValueError as exc:
            QMessageBox.warning(self.dashboard, "Unable to adopt", str(exc))

    def show_dashboard(self) -> None:
        self.dashboard.refresh()
        self.dashboard.show()
        self.dashboard.raise_()
        self.dashboard.activateWindow()

    def toggle_visibility(self) -> None:
        self.household.visible = not self.household.visible
        self.persist_and_refresh()

    def _apply_visibility(self) -> None:
        for overlay in self.overlays:
            overlay.setVisible(self.household.visible)

    def persist_and_refresh(self) -> None:
        write(self.household)
        self.dashboard.refresh()
        self._apply_visibility()
        for overlay in self.overlays:
            overlay.refresh()

    def apply_time_decay(self) -> None:
        self.household.apply_time_decay()
        self.persist_and_refresh()
        for overlay in self.overlays:
            if overlay.pet.needs_attention:
                overlay.show_bubble(overlay.pet.mood_emoji, 5000)

    def sync_github(self) -> None:
        QApplication.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))
        since = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
        try:
            username, events = fetch_recent_activity(since)
            rewards = apply_activity(self.household, events)
            self.persist_and_refresh()
            food_count = sum(1 for reward in rewards if reward.food_id)
            summary = (
                f"Synced @{username}.\n\n"
                f"New activity: {len(rewards)}\n"
                f"XP: +{sum(reward.xp for reward in rewards)}\n"
                f"Coins: +{sum(reward.coins for reward in rewards)}\n"
                f"Food drops: {food_count}"
            )
            QMessageBox.information(self.dashboard, "GitHub sync complete", summary)
            for overlay in self.overlays:
                overlay.show_bubble("🎉" if rewards else "✅")
        except GitHubError as exc:
            QMessageBox.warning(self.dashboard, "GitHub sync failed", str(exc))
        finally:
            QApplication.restoreOverrideCursor()


def _initial_household() -> Household | None:
    household = load()
    if household is not None:
        return household
    dialog = AdoptionDialog()
    if dialog.exec() != QDialog.DialogCode.Accepted:
        return None
    household = Household()
    household.adopt(*dialog.values())
    write(household)
    return household


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("CodePet")
    app.setOrganizationName("CodePet Contributors")
    app.setQuitOnLastWindowClosed(False)
    household = _initial_household()
    if household is None:
        return
    controller = CodePetApplication(app, household)
    controller.show_dashboard()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
