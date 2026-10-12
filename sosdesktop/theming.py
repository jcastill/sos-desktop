import os
from PyQt6.QtGui import QColor, QIcon, QPalette
from PyQt6.QtWidgets import QApplication


def apply_dark_theme(app: QApplication) -> None:
    app.setStyle("Fusion")
    palette = QPalette()
    gray = QColor(128, 128, 128)
    black = QColor(56, 56, 56)  # #383838
    accent = QColor(0xA6, 0x00, 0x00)

    # Primary surfaces to pure black
    palette.setColor(QPalette.ColorRole.Window, black)
    palette.setColor(QPalette.ColorRole.WindowText, QColor(220, 220, 220))
    palette.setColor(QPalette.ColorRole.Base, black)
    palette.setColor(QPalette.ColorRole.AlternateBase, black)
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.Text, QColor(220, 220, 220))
    palette.setColor(QPalette.ColorRole.Button, black)
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(220, 220, 220))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
    # Accents
    palette.setColor(QPalette.ColorRole.Link, accent)
    # Some platforms also respect LinkVisited
    try:
        palette.setColor(  # type: ignore[attr-defined]
            QPalette.ColorRole.LinkVisited, accent
        )
    except Exception:
        pass
    palette.setColor(QPalette.ColorRole.Highlight, accent)
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))

    # Disabled state tweaks
    palette.setColor(
        QPalette.ColorGroup.Disabled,
        QPalette.ColorRole.Text,
        gray,
    )
    palette.setColor(
        QPalette.ColorGroup.Disabled,
        QPalette.ColorRole.ButtonText,
        gray,
    )
    app.setPalette(palette)
    # Keep app icon if desired
    icon_path = os.path.join(os.path.dirname(__file__), "assets", "app.svg")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
