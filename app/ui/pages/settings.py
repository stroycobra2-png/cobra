from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QLineEdit, QPushButton, QMessageBox

class SettingsPage(QWidget):
    def __init__(self, db, window):
        super().__init__()
        self.db = db
        self.window = window

        root = QVBoxLayout(self)
        root.setContentsMargins(38, 34, 38, 34)
        root.setSpacing(16)

        title = QLabel("Ayarlar")
        title.setObjectName("pageTitle")
        root.addWidget(title)

        card = QFrame()
        card.setObjectName("card")
        lay = QVBoxLayout(card)

        lay.addWidget(QLabel("Öğrenci adı"))
        self.name = QLineEdit()
        self.name.setPlaceholderText("Adını yaz")
        lay.addWidget(self.name)

        save = QPushButton("Kaydet")
        save.setObjectName("primaryButton")
        save.setCursor(Qt.PointingHandCursor)
        save.clicked.connect(self.save)
        lay.addWidget(save, alignment=Qt.AlignLeft)

        root.addWidget(card)

        roadmap = QFrame()
        roadmap.setObjectName("card")
        r = QVBoxLayout(roadmap)
        rt = QLabel("Yakında eklenecek ayarlar")
        rt.setObjectName("cardTitle")
        r.addWidget(rt)
        info = QLabel(
            "Günlük hedef • Ses seviyesi • İngilizce aksan seçimi • Bildirimler • "
            "Tema • Otomatik tekrar saati • Profil ve seviye testi"
        )
        info.setWordWrap(True)
        info.setObjectName("muted")
        r.addWidget(info)
        root.addWidget(roadmap)
        root.addStretch()
        self.refresh()

    def refresh(self):
        self.name.setText(self.db.get_profile()["name"])

    def save(self):
        self.db.update_profile_name(self.name.text())
        QMessageBox.information(self, "Kaydedildi", "Profil ayarların kaydedildi.")
        self.window.dashboard.refresh()
