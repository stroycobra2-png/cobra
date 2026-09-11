from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QProgressBar
)

def stat_card(title, value, note):
    frame = QFrame()
    frame.setObjectName("card")
    lay = QVBoxLayout(frame)
    t = QLabel(title)
    t.setObjectName("muted")
    v = QLabel(value)
    v.setObjectName("statValue")
    n = QLabel(note)
    n.setObjectName("muted")
    lay.addWidget(t)
    lay.addWidget(v)
    lay.addWidget(n)
    return frame

class DashboardPage(QWidget):
    def __init__(self, db, window):
        super().__init__()
        self.db = db
        self.window = window

        root = QVBoxLayout(self)
        root.setContentsMargins(38, 34, 38, 34)
        root.setSpacing(20)

        self.greeting = QLabel()
        self.greeting.setObjectName("pageTitle")
        root.addWidget(self.greeting)

        intro = QLabel("Bugünkü hedefin: kısa ama düzenli çalış. Her tamamlanan ders ilerlemene eklenir.")
        intro.setObjectName("muted")
        intro.setWordWrap(True)
        root.addWidget(intro)

        stats = QHBoxLayout()
        self.xp_card_holder = QHBoxLayout()
        root.addLayout(stats)

        self.level_card = stat_card("Mevcut seviye", "A1", "Başlangıç")
        self.xp_card = stat_card("Toplam XP", "0", "Derslerle artar")
        self.lesson_card = stat_card("Tamamlanan", "0", "ders")
        stats.addWidget(self.level_card)
        stats.addWidget(self.xp_card)
        stats.addWidget(self.lesson_card)

        continue_card = QFrame()
        continue_card.setObjectName("heroCard")
        hero = QVBoxLayout(continue_card)
        hero.setContentsMargins(26, 24, 26, 24)

        small = QLabel("BUGÜNÜN ROTASI")
        small.setObjectName("accentText")
        hero.addWidget(small)

        title = QLabel("A1 • Temelleri kur")
        title.setObjectName("heroTitle")
        hero.addWidget(title)

        desc = QLabel("Selamlaşma → Kendini tanıtma → Sayılar ve yaş")
        desc.setObjectName("heroDescription")
        hero.addWidget(desc)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(True)
        hero.addWidget(self.progress_bar)

        btn = QPushButton("Derslere devam et  →")
        btn.setObjectName("primaryButton")
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(self.window.open_levels)
        hero.addWidget(btn, alignment=Qt.AlignLeft)
        root.addWidget(continue_card)

        focus = QFrame()
        focus.setObjectName("card")
        f = QVBoxLayout(focus)
        f.addWidget(QLabel("Nasıl ilerleyeceksin?"))
        txt = QLabel(
            "Kelime + Dilbilgisi + Okuma + Dinleme + Konuşma + Yazma becerileri "
            "ayrı ayrı takip edilecek. Bir seviyeyi sadece soru çözerek değil, tüm becerilerde "
            "yeterli başarı göstererek tamamlayacaksın."
        )
        txt.setWordWrap(True)
        txt.setObjectName("muted")
        f.addWidget(txt)
        root.addWidget(focus)
        root.addStretch()
        self.refresh()

    def refresh(self):
        profile = self.db.get_profile()
        stats = self.db.progress_stats()
        self.greeting.setText(f"Merhaba, {profile['name']} 👋")

        # kartlardaki ikinci label değerlerini güncelle
        self.level_card.layout().itemAt(1).widget().setText(profile["current_level"])
        self.xp_card.layout().itemAt(1).widget().setText(str(profile["xp"]))
        self.lesson_card.layout().itemAt(1).widget().setText(str(stats["completed"]))

        percent = int((stats["completed"] / stats["total"]) * 100) if stats["total"] else 0
        self.progress_bar.setValue(percent)
