import sys

from PySide6.QtCore import Qt, QTimer, QElapsedTimer, QRectF, QEasingCurve, QPropertyAnimation
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QLinearGradient
from PySide6.QtWidgets import QApplication

from app.database import Database
from app.main_window import MainWindow, ProfileCreateDialog
from app.styles import apply_theme
from app.starfield import StarfieldWidget


APP_NAME = "12/D Dil Programı"
UI_FONT = "Noto Sans" if sys.platform.startswith("linux") else "Segoe UI"
CREDIT_TEXT = "Made By Hacı Bozkurt / The Teacher Pelin Doğan Ortaç"
SPLASH_MS = 5000


def _clamp(value, low=0.0, high=1.0):
    return max(low, min(high, value))


def _smoothstep(value):
    value = _clamp(value)
    return value * value * (3.0 - 2.0 * value)


class SplashScreen(StarfieldWidget):
    """Safe 5-second animated splash without child graphics effects."""

    def __init__(self):
        super().__init__(theme="dark", particle_count=150, splash_mode=True)
        self.setWindowTitle(APP_NAME)
        self.setFixedSize(980, 560)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )

        self._clock = QElapsedTimer()
        self._animation_timer = QTimer(self)
        self._animation_timer.setInterval(16)
        self._animation_timer.timeout.connect(self._frame)
        self._center()

    def _center(self):
        screen = QApplication.primaryScreen()
        if screen:
            rect = screen.availableGeometry()
            frame = self.frameGeometry()
            frame.moveCenter(rect.center())
            self.move(frame.topLeft())

    def start_animations(self):
        self.setWindowOpacity(1.0)
        self._clock.start()
        self._animation_timer.start()
        self.update()

    def stop_animations(self):
        self._animation_timer.stop()
        self.timer.stop()

    def closeEvent(self, event):
        self.stop_animations()
        super().closeEvent(event)

    def _frame(self):
        elapsed = self._clock.elapsed()
        if elapsed >= 4400:
            fade = _clamp((elapsed - 4400) / 600.0)
            self.setWindowOpacity(1.0 - _smoothstep(fade))
        else:
            self.setWindowOpacity(1.0)
        self.update()
        if elapsed >= SPLASH_MS:
            self._animation_timer.stop()

    def paintEvent(self, event):
        super().paintEvent(event)
        elapsed = self._clock.elapsed() if self._clock.isValid() else 0

        panel_p = _smoothstep((elapsed - 100) / 700.0)
        title_p = _smoothstep((elapsed - 450) / 750.0)
        subtitle_p = _smoothstep((elapsed - 850) / 700.0)
        credit_p = _smoothstep((elapsed - 1350) / 850.0)
        loading_p = _smoothstep((elapsed - 1850) / 650.0)

        painter = QPainter()
        if not painter.begin(self):
            return

        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)

            painter.setBrush(QColor(4, 8, 18, int(150 * panel_p)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(QRectF(32, 30, 916, 500), 32, 32)

            scale = 0.965 + (0.035 * panel_p)
            base_w, base_h = 870.0, 455.0
            w, h = base_w * scale, base_h * scale
            panel = QRectF(
                (self.width() - w) / 2.0,
                (self.height() - h) / 2.0,
                w,
                h,
            )

            panel_grad = QLinearGradient(panel.topLeft(), panel.bottomRight())
            panel_grad.setColorAt(0.0, QColor(27, 21, 55, int(246 * panel_p)))
            panel_grad.setColorAt(0.52, QColor(15, 24, 48, int(244 * panel_p)))
            panel_grad.setColorAt(1.0, QColor(8, 35, 50, int(242 * panel_p)))
            painter.setBrush(panel_grad)
            painter.setPen(QPen(QColor(139, 124, 255, int(135 * panel_p)), 1.2))
            painter.drawRoundedRect(panel, 30, 30)

            painter.setPen(QPen(QColor(120, 149, 255, int(210 * title_p)), 3))
            painter.drawLine(
                int(panel.center().x() - 66),
                int(panel.top() + 78),
                int(panel.center().x() + 66),
                int(panel.top() + 78),
            )

            title_rect = QRectF(panel.left() + 45, panel.top() + 104, panel.width() - 90, 72)
            painter.setPen(QColor(255, 255, 255, int(255 * title_p)))
            font = QFont(UI_FONT, 33)
            font.setBold(True)
            font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 2.1)
            painter.setFont(font)
            painter.drawText(
                title_rect,
                Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextSingleLine,
                "12/D DİL PROGRAMI",
            )

            sub_rect = QRectF(panel.left() + 45, panel.top() + 178, panel.width() - 90, 38)
            painter.setPen(QColor(190, 201, 221, int(255 * subtitle_p)))
            painter.setFont(QFont(UI_FONT, 14))
            painter.drawText(
                sub_rect,
                Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextSingleLine,
                "A1 → C2  •  PREMIUM ENGLISH LEARNING",
            )

            credit_rect = QRectF(panel.left() + 38, panel.top() + 244, panel.width() - 76, 60)
            painter.setPen(QColor(158, 178, 255, int(255 * credit_p)))
            credit_font = QFont(UI_FONT, 15)
            credit_font.setBold(True)
            painter.setFont(credit_font)
            painter.drawText(
                credit_rect,
                Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap,
                CREDIT_TEXT,
            )

            load_rect = QRectF(panel.left() + 48, panel.bottom() - 92, panel.width() - 96, 28)
            painter.setPen(QColor(137, 151, 177, int(255 * loading_p)))
            painter.setFont(QFont(UI_FONT, 10))
            dots = "." * ((elapsed // 450) % 4)
            painter.drawText(
                load_rect,
                Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextSingleLine,
                f"Premium öğrenme deneyimi hazırlanıyor{dots}",
            )

            progress = _clamp(elapsed / SPLASH_MS)
            bar_rect = QRectF(panel.left() + 76, panel.bottom() - 49, panel.width() - 152, 8)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(255, 255, 255, int(28 * loading_p)))
            painter.drawRoundedRect(bar_rect, 4, 4)

            fill_width = max(0.0, bar_rect.width() * progress)
            if fill_width > 0:
                fill_rect = QRectF(bar_rect.left(), bar_rect.top(), fill_width, bar_rect.height())
                painter.setBrush(QColor(120, 149, 255, int(255 * loading_p)))
                painter.drawRoundedRect(fill_rect, 4, 4)

            pct_rect = QRectF(panel.left() + 76, panel.bottom() - 36, panel.width() - 152, 24)
            painter.setPen(QColor(113, 127, 153, int(230 * loading_p)))
            painter.setFont(QFont(UI_FONT, 9))
            painter.drawText(
                pct_rect,
                Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextSingleLine,
                f"%{int(progress * 100)}",
            )
        finally:
            painter.end()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName("12D")

    splash = SplashScreen()
    splash.show()
    splash.start_animations()
    app.processEvents()

    db = Database()
    db.initialize()

    # QApplication üzerinde referans tut; pencereler GC tarafından kapanmasın.
    app._main_window = None
    app._first_profile_dialog = None

    def show_main_window():
        profile = db.get_profile()
        if profile is None:
            app.quit()
            return

        apply_theme(app, profile["theme"])

        window = MainWindow(db, app)
        app._main_window = window
        window.setWindowOpacity(0.0)
        window.show()
        window.raise_()
        window.activateWindow()

        window._open_animation = QPropertyAnimation(window, b"windowOpacity", window)
        window._open_animation.setDuration(550)
        window._open_animation.setStartValue(0.0)
        window._open_animation.setEndValue(1.0)
        window._open_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        window._open_animation.start()

    def finish_splash():
        splash.stop_animations()
        splash.close()

        # İLK AÇILIŞ KİLİDİ:
        # Profil yoksa MainWindow hiç oluşturulmaz.
        if not db.has_profiles():
            apply_theme(app, "dark")
            dialog = ProfileCreateDialog(db, mandatory=True)
            app._first_profile_dialog = dialog

            result = dialog.exec()
            app._first_profile_dialog = None

            if result != dialog.DialogCode.Accepted or not db.has_profiles():
                # Profil oluşturmadan pencere kapatılırsa uygulama kapanır.
                app.quit()
                return

        show_main_window()

    QTimer.singleShot(SPLASH_MS, finish_splash)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
