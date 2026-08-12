"""Household, adoption, inventory, and shop window."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import Qt, QThread, QUrl, Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QFormLayout,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .auth import (
    AuthenticationError,
    DeviceAuthorization,
    begin_device_flow,
    complete_device_flow,
)
from .catalog import FOODS
from .domain import BREEDS, MAX_LIFESPAN_DAYS, MAX_PETS, MIN_LIFESPAN_DAYS, Household


class DeviceFlowWorker(QThread):
    connected = Signal()
    failed = Signal(str)

    def __init__(self, authorization: DeviceAuthorization) -> None:
        super().__init__()
        self.authorization = authorization

    def run(self) -> None:
        try:
            complete_device_flow(self.authorization)
            self.connected.emit()
        except AuthenticationError as exc:
            self.failed.emit(str(exc))


class AdoptionDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Adopt a CodePet")
        self.name = QLineEdit("Byte")
        self.species = QComboBox()
        self.species.addItems(BREEDS)
        self.breed = QComboBox()
        self.lifespan = QSpinBox()
        self.lifespan.setRange(MIN_LIFESPAN_DAYS, MAX_LIFESPAN_DAYS)
        self.lifespan.setValue(365)
        self.species.currentTextChanged.connect(self._update_breeds)
        self._update_breeds(self.species.currentText())
        form = QFormLayout()
        form.addRow("Name", self.name)
        form.addRow("Species", self.species)
        form.addRow("Breed", self.breed)
        form.addRow("Lifespan in days", self.lifespan)
        adopt = QPushButton("Adopt")
        adopt.clicked.connect(self.accept)
        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(adopt)

    def _update_breeds(self, species: str) -> None:
        self.breed.clear()
        self.breed.addItems(BREEDS[species])

    def values(self) -> tuple[str, str, str, int]:
        return (
            self.name.text(),
            self.species.currentText(),
            self.breed.currentText(),
            self.lifespan.value(),
        )


class DashboardWindow(QMainWindow):
    def __init__(
        self,
        household: Household,
        on_change: Callable[[], None],
        on_adopt: Callable[[], None],
        on_sync: Callable[[], None],
        on_visibility: Callable[[], None],
    ) -> None:
        super().__init__()
        self.household = household
        self.on_change = on_change
        self.on_adopt = on_adopt
        self.on_sync = on_sync
        self.on_visibility = on_visibility
        self.auth_worker: DeviceFlowWorker | None = None
        self.setWindowTitle("CodePet Home")
        self.setMinimumSize(720, 560)
        self.setStyleSheet("""
            QMainWindow, QWidget { background: #f6f0e6; color: #302923; }
            QGroupBox { border: 1px solid #d5c8b8; border-radius: 9px; margin-top: 12px; padding: 12px; font-weight: 700; }
            QPushButton { background: #a84c2f; color: white; border: 0; border-radius: 7px; padding: 8px 12px; font-weight: 650; }
            QPushButton:disabled { background: #b9ada1; }
            QComboBox, QSpinBox, QLineEdit { background: white; border: 1px solid #cfc2b3; border-radius: 6px; padding: 6px; }
            QTabWidget::pane { border: 1px solid #d5c8b8; border-radius: 8px; }
            QTabBar::tab { padding: 9px 18px; }
        """)

        root = QWidget()
        root_layout = QVBoxLayout(root)
        header = QHBoxLayout()
        self.pet_selector = QComboBox()
        self.pet_selector.currentIndexChanged.connect(self._select_pet)
        self.coins_label = QLabel()
        sync = QPushButton("Sync GitHub")
        sync.clicked.connect(self.on_sync)
        connect = QPushButton("Connect GitHub")
        connect.clicked.connect(self._connect_github)
        toggle = QPushButton("Show / Hide Pets")
        toggle.clicked.connect(self.on_visibility)
        header.addWidget(QLabel("Active pet"))
        header.addWidget(self.pet_selector)
        header.addStretch()
        header.addWidget(self.coins_label)
        header.addWidget(connect)
        header.addWidget(sync)
        header.addWidget(toggle)
        root_layout.addLayout(header)

        tabs = QTabWidget()
        tabs.addTab(self._create_home_tab(), "Home")
        tabs.addTab(self._create_shop_tab(), "Shop")
        tabs.addTab(self._create_inventory_tab(), "Inventory")
        root_layout.addWidget(tabs)
        self.setCentralWidget(root)
        self.refresh()

    def _create_home_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.pet_summary = QLabel()
        self.pet_summary.setTextFormat(Qt.TextFormat.RichText)
        self.pet_summary.setWordWrap(True)
        layout.addWidget(self.pet_summary)
        actions = QHBoxLayout()
        play = QPushButton("Play (+2 to +4 bond)")
        play.clicked.connect(self._play)
        self.adopt_button = QPushButton("Adopt a second pet")
        self.adopt_button.clicked.connect(self.on_adopt)
        actions.addWidget(play)
        actions.addWidget(self.adopt_button)
        actions.addStretch()
        layout.addLayout(actions)
        layout.addStretch()
        return tab

    def _create_shop_tab(self) -> QWidget:
        content = QWidget()
        grid = QGridLayout(content)
        for row, food in enumerate(FOODS.values()):
            grid.addWidget(QLabel(f"<b>{food.name}</b><br>{food.hunger_restore} hunger restored"), row, 0)
            grid.addWidget(QLabel(f"{food.price} coins"), row, 1)
            buy = QPushButton("Buy")
            buy.clicked.connect(lambda checked=False, food_id=food.id: self._buy(food_id))
            grid.addWidget(buy, row, 2)
        grid.setRowStretch(len(FOODS), 1)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(content)
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addWidget(scroll)
        return tab

    def _create_inventory_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.inventory_summary = QLabel()
        self.inventory_summary.setWordWrap(True)
        self.food_selector = QComboBox()
        feed = QPushButton("Feed active pet")
        feed.clicked.connect(self._feed)
        layout.addWidget(self.inventory_summary)
        layout.addWidget(self.food_selector)
        layout.addWidget(feed)
        layout.addStretch()
        return tab

    def _select_pet(self, index: int) -> None:
        pet_id = self.pet_selector.itemData(index)
        if pet_id:
            self.household.select_pet(pet_id)
            self.on_change()

    def _connect_github(self) -> None:
        try:
            authorization = begin_device_flow()
        except AuthenticationError as exc:
            QMessageBox.warning(self, "Unable to connect GitHub", str(exc))
            return
        QApplication.clipboard().setText(authorization.user_code)
        QDesktopServices.openUrl(QUrl(authorization.verification_uri))
        QMessageBox.information(
            self,
            "Authorize CodePet on GitHub",
            f"The code has been copied to your clipboard.\n\n"
            f"Code: {authorization.user_code}\n\n"
            f"Enter it in the GitHub page that just opened, then return to CodePet.",
        )
        self.auth_worker = DeviceFlowWorker(authorization)
        self.auth_worker.connected.connect(self._github_connected)
        self.auth_worker.failed.connect(self._github_connection_failed)
        self.auth_worker.finished.connect(self._auth_finished)
        self.auth_worker.start()

    def _github_connected(self) -> None:
        QMessageBox.information(self, "GitHub connected", "CodePet can now sync your activity.")

    def _github_connection_failed(self, message: str) -> None:
        QMessageBox.warning(self, "GitHub connection failed", message)

    def _auth_finished(self) -> None:
        self.auth_worker = None

    def _play(self) -> None:
        try:
            gained = self.household.active_pet.play()
            QMessageBox.information(self, "Play time", f"Bond increased by {gained}.")
            self.on_change()
        except ValueError as exc:
            QMessageBox.information(self, "Play time", str(exc))

    def _buy(self, food_id: str) -> None:
        try:
            self.household.buy(food_id)
            self.on_change()
        except ValueError as exc:
            QMessageBox.information(self, "Shop", str(exc))

    def _feed(self) -> None:
        food_id = self.food_selector.currentData()
        if not food_id:
            QMessageBox.information(self, "Inventory", "Buy food from the shop first.")
            return
        change = self.household.feed_active_pet(food_id)
        result = f"Bond changed by {change:+d}."
        QMessageBox.information(self, "Meal served", result)
        self.on_change()

    def refresh(self) -> None:
        selected_id = self.household.active_pet_id
        self.pet_selector.blockSignals(True)
        self.pet_selector.clear()
        for pet in self.household.pets:
            self.pet_selector.addItem(f"{pet.name} · {pet.breed}", pet.id)
        selected_index = self.pet_selector.findData(selected_id)
        self.pet_selector.setCurrentIndex(max(0, selected_index))
        self.pet_selector.blockSignals(False)

        pet = self.household.active_pet
        self.coins_label.setText(f"<b>{self.household.coins} coins</b>")
        self.pet_summary.setText(
            f"<h2>{pet.mood_emoji} {pet.name}</h2>"
            f"<p>{pet.breed} · Level {pet.level} {pet.stage}</p>"
            f"<p><b>XP</b> {pet.xp}/{pet.next_level_xp} &nbsp; "
            f"<b>Bond</b> {pet.bond} ({pet.bond_rank}) &nbsp; "
            f"<b>Streak</b> {self.household.streak} day(s)</p>"
            f"<p><b>Hunger</b> {pet.hunger}/100 &nbsp; "
            f"<b>Happiness</b> {pet.happiness}/100 &nbsp; "
            f"<b>Energy</b> {pet.energy}/100</p>"
            f"<p><b>Life remaining</b> {pet.days_remaining()} day(s)</p>"
        )
        self.adopt_button.setEnabled(len(self.household.pets) < MAX_PETS)

        items = [(food_id, count) for food_id, count in self.household.inventory.items() if count > 0]
        self.food_selector.clear()
        for food_id, count in items:
            self.food_selector.addItem(f"{FOODS[food_id].name} × {count}", food_id)
        self.inventory_summary.setText(
            "<h3>Pantry</h3>" + (
                "<br>".join(f"{FOODS[food_id].name}: {count}" for food_id, count in items)
                if items else "Your pantry is empty."
            )
        )
