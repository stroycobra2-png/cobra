from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton,
    QRadioButton, QButtonGroup, QMessageBox
)

class LessonPage(QWidget):
    def __init__(self, db, lesson_id, window):
        super().__init__()
        self.db = db
        self.lesson_id = lesson_id
        self.window = window
        self.lesson = db.get_lesson(lesson_id)

        root = QVBoxLayout(self)
        root.setContentsMargins(38, 30, 38, 30)
        root.setSpacing(16)

        back = QPushButton("← Derslere dön")
        back.setObjectName("secondaryButton")
        back.clicked.connect(self.window.return_to_levels)
        root.addWidget(back, alignment=Qt.AlignLeft)

        title = QLabel(f"{self.lesson['level_code']} • {self.lesson['title']}")
        title.setObjectName("pageTitle")
        root.addWidget(title)

        desc = QLabel(self.lesson["description"])
        desc.setObjectName("muted")
        root.addWidget(desc)

        vocab_card = QFrame()
        vocab_card.setObjectName("card")
        vlay = QVBoxLayout(vocab_card)
        vtitle = QLabel("Kelime Kartları")
        vtitle.setObjectName("cardTitle")
        vlay.addWidget(vtitle)
        for pair in self.lesson["vocabulary"].split(";"):
            en, tr = pair.split("|", 1)
            line = QLabel(f"<b>{en}</b>  —  {tr}")
            vlay.addWidget(line)
        root.addWidget(vocab_card)

        example_card = QFrame()
        example_card.setObjectName("card")
        elay = QVBoxLayout(example_card)
        et = QLabel("Örnek")
        et.setObjectName("cardTitle")
        elay.addWidget(et)
        en, tr = self.lesson["example"].split("|", 1)
        e1 = QLabel(en)
        e1.setObjectName("exampleEnglish")
        e2 = QLabel(tr)
        e2.setObjectName("muted")
        elay.addWidget(e1)
        elay.addWidget(e2)
        root.addWidget(example_card)

        quiz_card = QFrame()
        quiz_card.setObjectName("heroCard")
        qlay = QVBoxLayout(quiz_card)

        parts = self.lesson["quiz"].split("|")
        self.question = parts[0]
        self.answers = parts[1:5]
        self.correct_index = int(parts[5])

        qtitle = QLabel("Mini Quiz")
        qtitle.setObjectName("accentText")
        qlay.addWidget(qtitle)
        question = QLabel(self.question)
        question.setObjectName("cardTitle")
        question.setWordWrap(True)
        qlay.addWidget(question)

        self.group = QButtonGroup(self)
        for i, ans in enumerate(self.answers):
            radio = QRadioButton(ans)
            self.group.addButton(radio, i)
            qlay.addWidget(radio)

        check = QPushButton("Cevabı kontrol et")
        check.setObjectName("primaryButton")
        check.clicked.connect(self.check_answer)
        qlay.addWidget(check, alignment=Qt.AlignLeft)
        root.addWidget(quiz_card)

        root.addStretch()

    def check_answer(self):
        selected = self.group.checkedId()
        if selected == -1:
            QMessageBox.information(self, "Cevap seç", "Önce bir cevap seçmelisin.")
            return

        score = 100 if selected == self.correct_index else 0
        if score == 100:
            earned = self.db.complete_lesson(self.lesson_id, score)
            QMessageBox.information(
                self,
                "Harika!",
                f"Doğru cevap! Ders tamamlandı.\n+{earned} XP kazandın."
            )
            self.window.return_to_levels()
        else:
            QMessageBox.warning(
                self,
                "Tekrar dene",
                "Bu cevap doğru değil. Kelime ve örneği tekrar inceleyip yeniden dene."
            )
