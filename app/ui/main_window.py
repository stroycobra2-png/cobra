from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QLabel, QStackedWidget, QFrame
)
from app.ui.pages.dashboard import DashboardPage
from app.ui.pages.levels import LevelsPage
from app.ui.pages.progress import ProgressPage
from app.ui.pages.settings import SettingsPage
from app.ui.pages.lesson import LessonPage
from app.styles import APP_STYLE

class MainWindow(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setWindowTitle("FluentPath — İngilizce Öğren")
        self.resize(1180, 760)
        self.setMinimumSize(980, 650)
        self.setStyleSheet(APP_STYLE)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(235)
        side = QVBoxLayout(sidebar)
        side.setContentsMargins(22, 28, 22, 22)
        side.setSpacing(10)

        logo = QLabel("FLUENTPATH")
        logo.setObjectName("logo")
        side.addWidget(logo)

        subtitle = QLabel("Türkçeden İngilizceye")
        subtitle.setObjectName("muted")
        side.addWidget(subtitle)
        side.addSpacing(24)

        self.stack = QStackedWidget()

        self.dashboard = DashboardPage(db, self)
        self.levels = LevelsPage(db, self)
        self.progress = ProgressPage(db)
        self.settings = SettingsPage(db, self)

        self.pages = [self.dashboard, self.levels, self.progress, self.settings]
        for page in self.pages:
            self.stack.addWidget(page)

        nav_items = [
            ("⌂  Ana Sayfa", 0),
            ("▦  Seviyeler", 1),
            ("◔  İlerleme", 2),
            ("⚙  Ayarlar", 3),
        ]

        for text, index in nav_items:
            btn = QPushButton(text)
            btn.setObjectName("navButton")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked=False, i=index: self.open_page(i))
            side.addWidget(btn)

        side.addStretch()
        level_badge = QLabel("A1 → C2\nCEFR Yolculuğu")
        level_badge.setObjectName("sideBadge")
        side.addWidget(level_badge)

        layout.addWidget(sidebar)
        layout.addWidget(self.stack, 1)

    def open_page(self, index):
        if index == 0:
            self.dashboard.refresh()
        elif index == 1:
            self.levels.refresh()
        elif index == 2:
            self.progress.refresh()
        elif index == 3:
            self.settings.refresh()
        self.stack.setCurrentIndex(index)

    def open_levels(self):
        self.open_page(1)

    def open_lesson(self, lesson_id):
        lesson_page = LessonPage(self.db, lesson_id, self)
        self.stack.addWidget(lesson_page)
        self.stack.setCurrentWidget(lesson_page)

    def return_to_levels(self):
        self.open_page(1)
