from PySide6.QtGui import QColor, QPalette

ACCENT = "#7C6CFF"
ACCENT_2 = "#4FA8FF"


def _dark_palette():
    p = QPalette()
    values = {
        QPalette.ColorRole.Window: "#060914",
        QPalette.ColorRole.WindowText: "#F2F4FA",
        QPalette.ColorRole.Base: "#0D1322",
        QPalette.ColorRole.AlternateBase: "#111A2D",
        QPalette.ColorRole.ToolTipBase: "#11192A",
        QPalette.ColorRole.ToolTipText: "#F2F4FA",
        QPalette.ColorRole.Text: "#EEF1F8",
        QPalette.ColorRole.Button: "#131C2F",
        QPalette.ColorRole.ButtonText: "#EEF1F8",
        QPalette.ColorRole.BrightText: "#FFFFFF",
        QPalette.ColorRole.Link: ACCENT_2,
        QPalette.ColorRole.Highlight: ACCENT,
        QPalette.ColorRole.HighlightedText: "#FFFFFF",
        QPalette.ColorRole.PlaceholderText: "#667085",
    }
    for role, color in values.items():
        p.setColor(role, QColor(color))
    return p


def _light_palette():
    p = QPalette()
    values = {
        QPalette.ColorRole.Window: "#F4F6FC",
        QPalette.ColorRole.WindowText: "#182033",
        QPalette.ColorRole.Base: "#FFFFFF",
        QPalette.ColorRole.AlternateBase: "#F6F7FC",
        QPalette.ColorRole.ToolTipBase: "#FFFFFF",
        QPalette.ColorRole.ToolTipText: "#182033",
        QPalette.ColorRole.Text: "#182033",
        QPalette.ColorRole.Button: "#FFFFFF",
        QPalette.ColorRole.ButtonText: "#27304A",
        QPalette.ColorRole.BrightText: "#101729",
        QPalette.ColorRole.Link: "#5369E9",
        QPalette.ColorRole.Highlight: "#6E64F5",
        QPalette.ColorRole.HighlightedText: "#FFFFFF",
        QPalette.ColorRole.PlaceholderText: "#8992A5",
    }
    for role, color in values.items():
        p.setColor(role, QColor(color))
    return p


def apply_theme(app, theme="dark"):
    theme = "light" if theme == "light" else "dark"
    app.setPalette(_light_palette() if theme == "light" else _dark_palette())
    app.setStyleSheet("")
    app.setStyleSheet(get_stylesheet(theme))
    for widget in app.allWidgets():
        try:
            style = widget.style()
            style.unpolish(widget)
            style.polish(widget)
            widget.update()
        except Exception:
            pass


def get_stylesheet(theme="dark"):
    if theme == "light":
        return r"""
        * { outline:none; }
        QMainWindow { background:#F4F6FC; }
        QWidget { color:#182033;font-family:"Noto Sans","Segoe UI",sans-serif;font-size:14px;background:transparent; }
        QDialog,QMessageBox { background:#F6F7FC;color:#182033; }
        QMessageBox QLabel { color:#182033;background:transparent; }
        QStackedWidget,QScrollArea,QAbstractScrollArea::viewport { background:transparent; }

        QFrame#sidebar { background:rgba(255,255,255,250);border-right:1px solid #E0E5F0; }
        QFrame#brandCard { background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #F0EEFF,stop:1 #EAF5FF);border:1px solid #D7D8F7;border-radius:18px; }
        QLabel#logoMark { background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #7567F4,stop:1 #4EA9F7);color:white;border-radius:12px;font-size:17px;font-weight:900;min-width:48px;min-height:48px;max-width:48px;max-height:48px;qproperty-alignment:AlignCenter; }
        QLabel#brandTitle { color:#171E31;font-size:15px;font-weight:900;letter-spacing:0.8px;padding:0px; }
        QLabel#brandSub { color:#737D92;font-size:10px;font-weight:650;padding:0px; }
        QLabel#brandCredit { color:#626D84;font-size:9px;font-weight:650;line-height:1.15;padding:0px 2px; }
        QLabel#premiumTag { color:#5F55D9;background:#ECEAFF;border:1px solid #D7D2FF;border-radius:8px;padding:2px 8px;font-size:9px;font-weight:850; }
        QLabel#navSection { color:#9BA4B6;font-size:10px;font-weight:800;letter-spacing:1.6px;padding:9px 9px 3px 9px; }

        QFrame#topbar { background:rgba(255,255,255,238);border-bottom:1px solid #E0E5F0; }
        QLabel#topbarTitle { color:#151C2E;font-size:20px;font-weight:850; }
        QLabel#topbarSub { color:#8A93A5;font-size:11px;font-weight:600; }
        QLabel#levelPill,QLabel#metricPill { background:#F4F5FA;color:#404A60;border:1px solid #DFE4EE;border-radius:12px;padding:7px 12px;font-weight:700; }
        QLabel#levelPill { background:#EFEDFF;color:#5A4FD1;border-color:#DCD7FF; }
        QLabel#avatar { background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #7768F5,stop:1 #4EA8FA);color:#FFFFFF;border-radius:18px;min-width:36px;max-width:36px;min-height:36px;max-height:36px;font-weight:900;font-size:15px;qproperty-alignment:AlignCenter; }

        QLabel#pageEyebrow { color:#6C62E9;font-size:10px;font-weight:900;letter-spacing:1.8px; }
        QLabel#pageTitle { font-size:31px;font-weight:900;color:#12192A; }
        QLabel#heroTitle { font-size:25px;font-weight:900;color:#171E31; }
        QLabel#cardTitle { font-size:16px;font-weight:800;color:#20283A; }
        QLabel#muted { color:#737D91; }
        QLabel#accentText { color:#6258E6;font-weight:800; }
        QLabel#statValue { font-size:29px;font-weight:900;color:#12192A; }
        QLabel#sideCaption { color:#858EA2;font-size:9px;font-weight:900;letter-spacing:1.5px;padding:0; }
        QLabel#sideLevel { color:#151C2E;font-size:24px;font-weight:900; }
        QLabel#sideProgressText { color:#667085;font-size:11px;font-weight:750; }
        QLabel#sideSmall { color:#7C869A;font-size:10px;font-weight:650; }
        QLabel#sideFooter { color:#9AA3B4;font-size:9px;padding-top:2px; }

        QFrame#card,QFrame#levelCard { background:rgba(255,255,255,244);border:1px solid #E0E5EF;border-radius:18px; }
        QFrame#statCard { background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 rgba(255,255,255,250),stop:1 rgba(247,249,255,248));border:1px solid #E0E5EF;border-radius:18px; }
        QFrame#heroCard { background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #F1EFFF,stop:.55 #EEF4FF,stop:1 #EAF9FF);border:1px solid #D6D8F8;border-radius:22px; }
        QFrame#sideStatusCard { background:#F7F8FC;border:1px solid #E1E5EF;border-radius:16px; }

        QPushButton { min-height:39px;border-radius:11px;padding:0 15px;background:#FFFFFF;color:#2A3349;border:1px solid #DCE2ED;font-weight:650; }
        QPushButton:hover { background:#F8F9FD;border-color:#B9C2D5; }
        QPushButton:pressed { background:#F0F2F8; }
        QPushButton:disabled { background:#EEF0F5;color:#A1A8B6;border-color:#E5E8EF; }
        QPushButton#navButton { background:transparent;text-align:left;border:none;color:#5B657A;padding:0 13px;min-height:38px;border-radius:11px;font-weight:650; }
        QPushButton#navButton:hover { background:#F3F5FA;color:#1B2335; }
        QPushButton#navButton[active="true"] { background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #EEEAFE,stop:1 #EEF5FF);color:#5145C8;font-weight:800;border-left:3px solid #7165EF; }
        QPushButton#primaryButton { background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #7366F2,stop:1 #4C9FF4);color:white;border:none;font-weight:800;min-height:42px; }
        QPushButton#primaryButton:hover { background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #8074FA,stop:1 #5AAAFB); }
        QPushButton#secondaryButton { background:#FFFFFF;border:1px solid #DCE2ED;color:#313B52;font-weight:700; }
        QPushButton#quickButton { background:rgba(255,255,255,245);border:1px solid #DDE3EF;color:#273149;text-align:left;padding:12px 15px;min-height:62px;font-weight:750;border-radius:14px; }
        QPushButton#quickButton:hover { border:1px solid #8278F5;background:#F8F7FF;color:#4D44C2; }

        QLineEdit,QTextEdit,QPlainTextEdit,QComboBox,QSpinBox { background:#FFFFFF;color:#1C2437;border:1px solid #DDE3EE;border-radius:11px;padding:9px;selection-background-color:#7064EE;selection-color:white; }
        QLineEdit:focus,QTextEdit:focus,QPlainTextEdit:focus,QComboBox:focus,QSpinBox:focus { border:1px solid #756AF0; }
        QComboBox QAbstractItemView { background:#FFFFFF;color:#1C2437;border:1px solid #DDE3EE;selection-background-color:#EFEDFF;selection-color:#4B42BE;outline:none; }
        QCheckBox,QRadioButton { color:#253047;spacing:7px; }
        QProgressBar { background:#E9EDF5;border:none;border-radius:7px;min-height:14px;text-align:center;color:#586177;font-size:10px;font-weight:700; }
        QProgressBar::chunk { background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #7769F3,stop:1 #4EB6F7);border-radius:7px; }
        QTableWidget,QListView,QTreeView { background:#FFFFFF;color:#1C2437;alternate-background-color:#F8F9FC;border:1px solid #E0E5EF;border-radius:12px;gridline-color:#EDF0F5;selection-background-color:#EFEFFF;selection-color:#4037B4; }
        QHeaderView::section { background:#F4F6FA;color:#485267;padding:8px;border:none;border-right:1px solid #E2E6EE;border-bottom:1px solid #E2E6EE;font-weight:750; }
        QScrollArea { border:none; }
        QScrollBar:vertical { background:transparent;width:10px;margin:3px; }
        QScrollBar::handle:vertical { background:#C8CFDC;min-height:30px;border-radius:5px; }
        QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical { height:0px; }
        QStatusBar { background:rgba(255,255,255,240);color:#80899B;border-top:1px solid #E0E5EF;font-size:11px; }
        QToolTip { background:#FFFFFF;color:#1C2437;border:1px solid #D5DBE8;padding:6px;border-radius:6px; }
        QPushButton#menuButton { background:#F1F4FB;color:#25314A;border:1px solid #D9E0EF;border-radius:18px;min-width:38px;max-width:38px;min-height:38px;max-height:38px;font-size:20px;font-weight:900;padding:0; }
        QPushButton#menuButton:hover { background:#E7ECF8;border-color:#AFC0E8;color:#4D60C7; }
        QMenu { background:#FFFFFF;color:#1C2333;border:1px solid #DCE3F0;border-radius:12px;padding:7px; }
        QMenu::item { padding:9px 26px 9px 12px;border-radius:7px; }
        QMenu::item:selected { background:#EEF1FF;color:#3F52BE; }
        QMenu::item:disabled { color:#7C879A;font-weight:700; }
        QMenu::separator { height:1px;background:#E8ECF4;margin:6px 8px; }

        """

    return r"""
    * { outline:none; }
    QMainWindow { background:#050711; }
    QWidget { color:#EDF1FA;font-family:"Noto Sans","Segoe UI",sans-serif;font-size:14px;background:transparent; }
    QDialog,QMessageBox { background:#0A0F1D;color:#EDF1FA; }
    QMessageBox QLabel { color:#EDF1FA;background:transparent; }
    QStackedWidget,QScrollArea,QAbstractScrollArea::viewport { background:transparent; }

    QFrame#sidebar { background:rgba(7,11,22,248);border-right:1px solid rgba(111,128,168,42); }
    QFrame#brandCard { background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 rgba(123,103,255,38),stop:.52 rgba(55,104,255,24),stop:1 rgba(48,207,255,18));border:1px solid rgba(134,128,255,62);border-radius:18px; }
    QLabel#logoMark { background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #7E6BFF,stop:1 #47B5FF);color:#FFFFFF;border-radius:12px;font-size:17px;font-weight:900;min-width:48px;min-height:48px;max-width:48px;max-height:48px;qproperty-alignment:AlignCenter; }
    QLabel#brandTitle { color:#FFFFFF;font-size:15px;font-weight:900;letter-spacing:0.8px;padding:0px; }
    QLabel#brandSub { color:#8D9AB5;font-size:10px;font-weight:650;padding:0px; }
    QLabel#brandCredit { color:#8290AC;font-size:9px;font-weight:650;line-height:1.15;padding:0px 2px; }
    QLabel#premiumTag { color:#B8B1FF;background:rgba(120,102,255,20);border:1px solid rgba(130,115,255,50);border-radius:8px;padding:2px 8px;font-size:9px;font-weight:850; }
    QLabel#navSection { color:#56627A;font-size:10px;font-weight:850;letter-spacing:1.6px;padding:9px 9px 3px 9px; }

    QFrame#topbar { background:rgba(7,11,22,235);border-bottom:1px solid rgba(111,128,168,38); }
    QLabel#topbarTitle { color:#F8FAFF;font-size:20px;font-weight:900; }
    QLabel#topbarSub { color:#66738E;font-size:11px;font-weight:650; }
    QLabel#levelPill,QLabel#metricPill { background:rgba(19,28,48,220);color:#CBD3E5;border:1px solid rgba(94,111,149,65);border-radius:12px;padding:7px 12px;font-weight:750; }
    QLabel#levelPill { background:rgba(115,93,255,24);color:#BCB4FF;border-color:rgba(132,114,255,60); }
    QLabel#avatar { background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #7C69FF,stop:1 #49B8FF);color:#FFFFFF;border-radius:18px;min-width:36px;max-width:36px;min-height:36px;max-height:36px;font-weight:900;font-size:15px;qproperty-alignment:AlignCenter; }

    QLabel#pageEyebrow { color:#8D83FF;font-size:10px;font-weight:900;letter-spacing:1.9px; }
    QLabel#pageTitle { font-size:31px;font-weight:900;color:#FFFFFF; }
    QLabel#heroTitle { font-size:25px;font-weight:900;color:#FFFFFF; }
    QLabel#cardTitle { font-size:16px;font-weight:800;color:#F4F6FC; }
    QLabel#muted { color:#8591A9; }
    QLabel#accentText { color:#A69EFF;font-weight:800; }
    QLabel#statValue { font-size:29px;font-weight:900;color:#FFFFFF; }
    QLabel#sideCaption { color:#56627A;font-size:9px;font-weight:900;letter-spacing:1.5px;padding:0; }
    QLabel#sideLevel { color:#FFFFFF;font-size:24px;font-weight:900; }
    QLabel#sideProgressText { color:#8995AE;font-size:11px;font-weight:750; }
    QLabel#sideSmall { color:#66738D;font-size:10px;font-weight:650; }
    QLabel#sideFooter { color:#46536C;font-size:9px;padding-top:2px; }

    QFrame#card,QFrame#levelCard { background:rgba(13,19,34,236);border:1px solid rgba(101,116,151,48);border-radius:18px; }
    QFrame#statCard { background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 rgba(19,27,47,246),stop:1 rgba(12,18,33,244));border:1px solid rgba(101,116,151,48);border-radius:18px; }
    QFrame#heroCard { background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 rgba(52,40,107,242),stop:.44 rgba(29,39,83,242),stop:1 rgba(13,44,70,240));border:1px solid rgba(134,118,255,78);border-radius:22px; }
    QFrame#sideStatusCard { background:rgba(13,20,35,220);border:1px solid rgba(99,115,151,45);border-radius:16px; }

    QPushButton { min-height:39px;border-radius:11px;padding:0 15px;background:#121B2D;color:#E9EDF7;border:1px solid rgba(90,108,145,75);font-weight:650; }
    QPushButton:hover { background:#18243A;border-color:rgba(125,139,175,110);color:#FFFFFF; }
    QPushButton:pressed { background:#0E1626; }
    QPushButton:disabled { background:#0D1320;color:#505C70;border-color:#1A2435; }
    QPushButton#navButton { background:transparent;text-align:left;color:#8F9BB1;border:none;padding:0 13px;min-height:38px;border-radius:11px;font-weight:650; }
    QPushButton#navButton:hover { background:rgba(89,102,142,18);color:#E9EDF7; }
    QPushButton#navButton[active="true"] { background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 rgba(117,91,255,32),stop:1 rgba(63,153,255,13));color:#D5D0FF;font-weight:800;border-left:3px solid #8274FF; }
    QPushButton#primaryButton { background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #7A68FF,stop:.52 #676EF8,stop:1 #48A8FF);color:#FFFFFF;border:none;font-weight:850;min-height:42px; }
    QPushButton#primaryButton:hover { background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #8979FF,stop:.52 #7480FF,stop:1 #57B6FF); }
    QPushButton#primaryButton:pressed { background:#6257D8; }
    QPushButton#secondaryButton { background:rgba(18,27,45,225);border:1px solid rgba(91,108,144,78);color:#DDE3F0;font-weight:700; }
    QPushButton#quickButton { background:rgba(14,21,37,235);border:1px solid rgba(96,111,148,55);color:#E8EDF7;text-align:left;padding:12px 15px;min-height:62px;font-weight:750;border-radius:14px; }
    QPushButton#quickButton:hover { border:1px solid rgba(135,119,255,145);background:rgba(36,31,68,225);color:#FFFFFF; }

    QLineEdit,QTextEdit,QPlainTextEdit,QComboBox,QSpinBox { background:#0B1220;color:#EDF1F9;border:1px solid rgba(92,108,143,76);border-radius:11px;padding:9px;selection-background-color:#7667F1;selection-color:#FFFFFF; }
    QLineEdit:focus,QTextEdit:focus,QPlainTextEdit:focus,QComboBox:focus,QSpinBox:focus { border:1px solid #8175FA;background:#0D1525; }
    QComboBox::drop-down { border:none;width:28px; }
    QComboBox QAbstractItemView { background:#0D1525;color:#EDF1F9;border:1px solid #2D3951;selection-background-color:#292557;selection-color:#FFFFFF;outline:none; }
    QCheckBox,QRadioButton { color:#DCE2EE;spacing:7px; }
    QProgressBar { background:#0A1120;border:1px solid rgba(76,91,124,52);border-radius:7px;min-height:14px;text-align:center;color:#8E99AE;font-size:10px;font-weight:700; }
    QProgressBar::chunk { background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #7C69FF,stop:1 #4AB9FF);border-radius:7px; }
    QTableWidget,QListView,QTreeView { background:#0B1220;color:#EAF0F9;alternate-background-color:#0E1728;border:1px solid rgba(90,106,140,55);border-radius:12px;gridline-color:#192337;selection-background-color:#282456;selection-color:#FFFFFF; }
    QHeaderView::section { background:#111A2B;color:#B8C2D4;padding:8px;border:none;border-right:1px solid #253049;border-bottom:1px solid #253049;font-weight:750; }
    QTableCornerButton::section { background:#111A2B;border:1px solid #253049; }
    QScrollArea { border:none; }
    QScrollBar:vertical { background:transparent;width:10px;margin:3px; }
    QScrollBar::handle:vertical { background:#29364E;min-height:30px;border-radius:5px; }
    QScrollBar::handle:vertical:hover { background:#3B4B68; }
    QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical { height:0px; }
    QScrollBar:horizontal { background:transparent;height:10px;margin:3px; }
    QScrollBar::handle:horizontal { background:#29364E;min-width:30px;border-radius:5px; }
    QScrollBar::add-line:horizontal,QScrollBar::sub-line:horizontal { width:0px; }
    QStatusBar { background:rgba(6,10,19,238);color:#59657B;border-top:1px solid rgba(91,107,142,34);font-size:11px; }
    QStatusBar::item { border:none; }
    QToolTip { background:#111A2B;color:#EAF0F8;border:1px solid #33415C;padding:6px;border-radius:6px; }
    QPushButton#menuButton { background:rgba(22,30,48,230);color:#EAF0FF;border:1px solid rgba(120,139,198,70);border-radius:18px;min-width:38px;max-width:38px;min-height:38px;max-height:38px;font-size:20px;font-weight:900;padding:0; }
    QPushButton#menuButton:hover { background:rgba(45,55,91,240);border-color:#788CFF;color:#FFFFFF; }
    QMenu { background:#101725;color:#EEF3FF;border:1px solid #2E3A54;border-radius:12px;padding:7px; }
    QMenu::item { padding:9px 26px 9px 12px;border-radius:7px; }
    QMenu::item:selected { background:#263557;color:#FFFFFF; }
    QMenu::item:disabled { color:#7E8AA3;font-weight:700; }
    QMenu::separator { height:1px;background:#273249;margin:6px 8px; }

    """
