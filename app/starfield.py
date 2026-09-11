import math
import random

from PySide6.QtCore import QTimer, QPointF
from PySide6.QtGui import QColor, QPainter, QPen, QLinearGradient, QRadialGradient
from PySide6.QtWidgets import QWidget


class StarfieldWidget(QWidget):
    """Premium animated background: gradient sky + nebula + star particles."""

    def __init__(self, parent=None, theme="dark", particle_count=115, splash_mode=False):
        super().__init__(parent)
        self.theme = theme if theme in ("dark", "light") else "dark"
        self.particle_count = max(20, int(particle_count))
        self.splash_mode = splash_mode
        self._tick = 0.0
        self._stars = []
        self._orbs = [
            {"x": .18, "y": .22, "r": .34, "phase": 0.2, "tone": "violet"},
            {"x": .80, "y": .30, "r": .30, "phase": 2.4, "tone": "blue"},
            {"x": .56, "y": .82, "r": .38, "phase": 4.1, "tone": "cyan"},
        ]
        self.setAutoFillBackground(False)
        self._seed_stars()

        self.timer = QTimer(self)
        self.timer.setInterval(33)
        self.timer.timeout.connect(self._advance)
        self.timer.start()

    def set_theme(self, theme):
        self.theme = "light" if theme == "light" else "dark"
        self.update()

    def _seed_stars(self):
        self._stars = [self._make_star(random.random()) for _ in range(self.particle_count)]

    def _make_star(self, y=None):
        depth = random.uniform(.22, 1.0)
        return {
            "x": random.random(),
            "y": random.random() if y is None else y,
            "depth": depth,
            "size": random.uniform(.55, 1.9) * depth,
            "speed": random.uniform(.00055, .0019) * (.55 + depth),
            "phase": random.uniform(0.0, math.tau),
        }

    def _advance(self):
        if not self.isVisible():
            return
        self._tick += .07
        mult = 1.8 if self.splash_mode else 1.0
        for star in self._stars:
            star["y"] += star["speed"] * mult
            star["x"] += math.sin(self._tick * .18 + star["phase"]) * .000035 * star["depth"]
            if star["y"] > 1.02:
                star.update(self._make_star(-.02))
            if star["x"] < -.02:
                star["x"] = 1.01
            elif star["x"] > 1.02:
                star["x"] = -.01
        self.update()

    def _paint_nebula(self, painter, w, h):
        dark_tones = {
            "violet": (112, 72, 255),
            "blue": (47, 102, 255),
            "cyan": (35, 198, 255),
        }
        light_tones = {
            "violet": (126, 98, 255),
            "blue": (81, 124, 255),
            "cyan": (73, 188, 232),
        }
        tones = light_tones if self.theme == "light" else dark_tones
        for orb in self._orbs:
            drift_x = math.sin(self._tick * .10 + orb["phase"]) * .035
            drift_y = math.cos(self._tick * .08 + orb["phase"]) * .026
            cx = (orb["x"] + drift_x) * w
            cy = (orb["y"] + drift_y) * h
            radius = orb["r"] * max(w, h)
            grad = QRadialGradient(QPointF(cx, cy), radius)
            r, g, b = tones[orb["tone"]]
            if self.theme == "light":
                grad.setColorAt(0.0, QColor(r, g, b, 26))
                grad.setColorAt(.42, QColor(r, g, b, 10))
            else:
                grad.setColorAt(0.0, QColor(r, g, b, 40))
                grad.setColorAt(.42, QColor(r, g, b, 14))
            grad.setColorAt(1.0, QColor(r, g, b, 0))
            painter.setPen(QPen(QColor(0, 0, 0, 0), 0))
            painter.setBrush(grad)
            painter.drawEllipse(QPointF(cx, cy), radius, radius)

    def paintEvent(self, event):
        painter = QPainter()
        if not painter.begin(self):
            return
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            w, h = max(1, self.width()), max(1, self.height())

            bg = QLinearGradient(0, 0, w, h)
            if self.theme == "light":
                bg.setColorAt(0.0, QColor("#F7F8FD"))
                bg.setColorAt(.50, QColor("#F1F4FB"))
                bg.setColorAt(1.0, QColor("#EEF2FA"))
                star_base = QColor(65, 88, 138)
            else:
                bg.setColorAt(0.0, QColor("#050711"))
                bg.setColorAt(.48, QColor("#080C19"))
                bg.setColorAt(1.0, QColor("#050914"))
                star_base = QColor(211, 222, 255)
            painter.fillRect(self.rect(), bg)
            self._paint_nebula(painter, w, h)

            for star in self._stars:
                twinkle = .58 + .42 * math.sin(self._tick + star["phase"])
                if self.theme == "light":
                    alpha = int(12 + 33 * star["depth"] * twinkle)
                else:
                    alpha = int(42 + 150 * star["depth"] * twinkle)
                color = QColor(star_base)
                color.setAlpha(max(10, min(220, alpha)))
                painter.setPen(QPen(color, 0))
                painter.setBrush(color)
                radius = max(.5, star["size"])
                x, y = star["x"] * w, star["y"] * h
                painter.drawEllipse(QPointF(x, y), radius, radius)

            cycle = self._tick % 16.0
            if 3.0 < cycle < 4.35 and self.theme == "dark":
                t = (cycle - 3.0) / 1.35
                x = w * (.18 + .60 * t)
                y = h * (.12 + .24 * t)
                streak = QColor(150, 175, 255, int(80 * (1.0 - abs(t - .5) * 1.7)))
                painter.setPen(QPen(streak, 1.2))
                painter.drawLine(QPointF(x - 44, y - 18), QPointF(x, y))
        finally:
            painter.end()
