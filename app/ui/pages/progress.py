from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QProgressBar

class ProgressPage(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(38, 34, 38, 34)
        self.title = QLabel("İlerleme")
        self.title.setObjectName("pageTitle")
        self.root.addWidget(self.title)

        self.card = QFrame()
        self.card.setObjectName("card")
        self.lay = QVBoxLayout(self.card)
        self.summary = QLabel()
        self.summary.setObjectName("cardTitle")
        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        self.xp = QLabel()
        self.xp.setObjectName("accentText")
        self.lay.addWidget(self.summary)
        self.lay.addWidget(self.bar)
        self.lay.addWidget(self.xp)
        self.root.addWidget(self.card)

        note = QLabel(
            "Tam sürümde burada kelime, dilbilgisi, okuma, dinleme, konuşma ve yazma "
            "becerilerinin her biri ayrı grafiklerle gösterilecek."
        )
        note.setWordWrap(True)
        note.setObjectName("muted")
        self.root.addWidget(note)
        self.root.addStretch()
        self.refresh()

    def refresh(self):
        stats = self.db.progress_stats()
        percent = int((stats["completed"] / stats["total"]) * 100) if stats["total"] else 0
        self.summary.setText(f"{stats['completed']} / {stats['total']} örnek ders tamamlandı")
        self.bar.setValue(percent)
        self.xp.setText(f"Toplam XP: {stats['xp']}")
