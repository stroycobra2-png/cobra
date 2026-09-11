from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QScrollArea
)

LEVEL_NOTES = {
    "A1": "Günlük hayatta en temel ifadeler",
    "A2": "Basit günlük iletişim",
    "B1": "Bağımsız İngilizce kullanımı",
    "B2": "Akıcı ve detaylı iletişim",
    "C1": "İleri akademik/profesyonel kullanım",
    "C2": "Ustalık ve doğal ifade"
}

class LevelsPage(QWidget):
    def __init__(self, db, window):
        super().__init__()
        self.db = db
        self.window = window

        outer = QVBoxLayout(self)
        outer.setContentsMargins(38, 34, 38, 34)

        title = QLabel("Seviye Haritası")
        title.setObjectName("pageTitle")
        outer.addWidget(title)

        sub = QLabel("A1'den C2'ye kadar tüm yol. Şimdilik A1 örnek dersleri aktiftir.")
        sub.setObjectName("muted")
        outer.addWidget(sub)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        self.content = QWidget()
        self.list_layout = QVBoxLayout(self.content)
        self.list_layout.setSpacing(14)
        scroll.setWidget(self.content)
        outer.addWidget(scroll)

        self.refresh()

    def clear(self):
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

    def refresh(self):
        self.clear()
        for level in self.db.get_levels():
            card = QFrame()
            card.setObjectName("levelCard")
            row = QHBoxLayout(card)
            row.setContentsMargins(22, 18, 22, 18)

            badge = QLabel(level["code"])
            badge.setObjectName("levelBadge")
            badge.setFixedWidth(72)
            row.addWidget(badge)

            text_box = QVBoxLayout()
            title = QLabel(level["title"])
            title.setObjectName("cardTitle")
            desc = QLabel(level["description"])
            desc.setObjectName("muted")
            desc.setWordWrap(True)
            note = QLabel(LEVEL_NOTES[level["code"]])
            note.setObjectName("accentText")
            text_box.addWidget(title)
            text_box.addWidget(desc)
            text_box.addWidget(note)
            row.addLayout(text_box, 1)

            lessons = self.db.get_lessons(level["code"])
            if lessons:
                btn = QPushButton(f"{len(lessons)} ders")
                btn.setObjectName("primaryButton")
                btn.setCursor(Qt.PointingHandCursor)
                btn.clicked.connect(lambda checked=False, code=level["code"]: self.show_lessons(code))
            else:
                btn = QPushButton("Yakında")
                btn.setEnabled(False)
            row.addWidget(btn)
            self.list_layout.addWidget(card)

        self.list_layout.addStretch()

    def show_lessons(self, level_code):
        self.clear()

        back = QPushButton("← Seviyelere dön")
        back.setObjectName("secondaryButton")
        back.clicked.connect(self.refresh)
        self.list_layout.addWidget(back, alignment=Qt.AlignLeft)

        heading = QLabel(f"{level_code} Dersleri")
        heading.setObjectName("pageTitle")
        self.list_layout.addWidget(heading)

        for lesson in self.db.get_lessons(level_code):
            card = QFrame()
            card.setObjectName("card")
            row = QHBoxLayout(card)

            done = "✓" if lesson["completed"] else str(lesson["position"])
            num = QLabel(done)
            num.setObjectName("lessonNumber")
            num.setFixedWidth(44)
            row.addWidget(num)

            text = QVBoxLayout()
            title = QLabel(lesson["title"])
            title.setObjectName("cardTitle")
            desc = QLabel(lesson["description"])
            desc.setObjectName("muted")
            text.addWidget(title)
            text.addWidget(desc)
            if lesson["best_score"]:
                score = QLabel(f"En iyi skor: %{lesson['best_score']}")
                score.setObjectName("accentText")
                text.addWidget(score)
            row.addLayout(text, 1)

            btn = QPushButton("Aç")
            btn.setObjectName("primaryButton")
            btn.clicked.connect(lambda checked=False, lid=lesson["id"]: self.window.open_lesson(lid))
            row.addWidget(btn)
            self.list_layout.addWidget(card)

        self.list_layout.addStretch()
