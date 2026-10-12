"""Minimal PyQt6 app to generate and view sos reports."""

import getpass
import sys

from PyQt6.QtCore import Qt, QSettings, QTimer
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QMessageBox,
    QSplitter,
    QLabel,
    QTabWidget,
    QApplication,
)

from .theming import apply_dark_theme
from .widgets.top_bar import TopBar
from .widgets.sidebar import Sidebar
from .widgets.sos_reports_tab import SosReportsTab
from .actions.sos_actions import SosActions
from .sos_runner import SosRunner
from .file_operations import open_path
from .constants import APP_NAME, APP_VERSION, APP_ORG, Styles


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(900, 560)

        # Settings for persistence
        self.settings = QSettings(APP_ORG, APP_ORG)

        # Create components
        self._create_widgets()
        self._create_layout()
        self._create_menu()
        self._setup_status_bar()

        QTimer.singleShot(0, self._refresh_all)

    def _create_widgets(self) -> None:
        """Create all UI widgets."""
        self.top_bar = TopBar(self.settings, self._refresh_all)

        self.sos_runner = SosRunner(on_finished_callback=self._refresh_reports)

        self.sos_reports_tab = SosReportsTab(
            on_open_callback=lambda path: open_path(path, self)
        )

        self.actions = SosActions(
            parent_widget=self,
            runner=self.sos_runner,
            get_case_id_callback=self.top_bar.get_case_id,
            get_upload_target_callback=self.top_bar.get_upload_target,
            get_verbosity_callback=self.top_bar.get_verbosity,
            settings=self.settings,
        )

        self.sidebar = Sidebar(self.actions)
        self.sidebar.set_get_selected_report_callback(
            self.sos_reports_tab.get_selected_path
        )

    def _create_layout(self) -> None:
        """Create and arrange the main layout."""
        tabs = QTabWidget()
        tabs.addTab(self.sos_reports_tab, "SOS Reports")

        # Top right area: top bar + tabs
        right_top = QWidget()
        right_top_layout = QVBoxLayout()
        right_top_layout.addWidget(self.top_bar)
        right_top_layout.addWidget(tabs, 1)
        right_top.setLayout(right_top_layout)

        # Right vertical splitter: content above, runner below
        right_splitter = QSplitter()
        right_splitter.setOrientation(Qt.Orientation.Vertical)
        right_splitter.addWidget(right_top)
        right_splitter.addWidget(self.sos_runner)
        right_splitter.setSizes([360, 200])

        # Main horizontal splitter: sidebar | right content
        main_splitter = QSplitter()
        main_splitter.setOrientation(Qt.Orientation.Horizontal)
        main_splitter.addWidget(self.sidebar)
        main_splitter.addWidget(right_splitter)
        main_splitter.setSizes([180, 720])

        # Set as central widget
        container = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(main_splitter)
        container.setLayout(layout)
        self.setCentralWidget(container)

    def _create_menu(self) -> None:
        """Create the menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")
        refresh_action = QAction("Refresh", self)
        refresh_action.triggered.connect(self._refresh_all)
        file_menu.addAction(refresh_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Help menu
        help_menu = menubar.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _setup_status_bar(self) -> None:
        """Setup the status bar with user info and version."""
        status = self.statusBar()
        status.setStyleSheet(
            f"QStatusBar {{ background-color: {Styles.STATUS_BAR_BG};"
            f" color: {Styles.STATUS_BAR_TEXT}; }}"
        )

        user_label = QLabel(f"User: {getpass.getuser()}")
        version_label = QLabel(f"Version: {APP_VERSION}")

        user_label.setStyleSheet("QLabel { color: white; }")
        version_label.setStyleSheet("QLabel { color: white; }")

        status.addWidget(user_label)
        status.addPermanentWidget(version_label)

    def _refresh_all(self) -> None:
        """Refresh all tables."""
        self._refresh_reports()

    def _refresh_reports(self) -> None:
        """Refresh the SOS reports table."""
        self.sos_reports_tab.refresh()

    def _show_about(self) -> None:
        """Show about dialog."""
        QMessageBox.information(
            self,
            f"About {APP_NAME}",
            (
                f"{APP_NAME} v{APP_VERSION}\n\n"
                "A desktop front-end for the sos suite of tools.\n"
                "Generate, view, obfuscate, and upload sos reports\n"
                "without leaving the GUI.\n\n"
                "License: GPL-2.0-or-later"
            ),
        )


def main() -> None:
    """Console entry point: create the app, apply theme, show the window."""
    app = QApplication(sys.argv)
    apply_dark_theme(app)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
