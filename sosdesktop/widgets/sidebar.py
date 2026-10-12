"""Left sidebar with action buttons."""

from PyQt6.QtWidgets import QVBoxLayout, QPushButton, QWidget

from ..constants import Styles


class Sidebar(QWidget):
    """Left sidebar containing action buttons."""

    def __init__(self, actions, parent=None) -> None:
        super().__init__(parent)
        self.actions = actions
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout()

        # Create action buttons
        self.generate_button = QPushButton("Generate Report")
        self.generate_button.clicked.connect(self.actions.generate_report)

        self.upload_button = QPushButton("Upload Selected")
        self.upload_button.clicked.connect(self._handle_upload)

        self.remote_button = QPushButton("Generate Remote Report")
        self.remote_button.clicked.connect(
            self.actions.generate_remote_report
        )

        self.collect_button = QPushButton("Multi-node Collect")
        self.collect_button.clicked.connect(self.actions.collect_reports)

        self.clean_button = QPushButton("Obfuscate Report")
        self.clean_button.clicked.connect(self._handle_clean)

        self.authorize_button = QPushButton("Authorize System")
        self.authorize_button.clicked.connect(self.actions.authorize_system)

        # Add buttons to layout
        layout.addWidget(self.generate_button)
        layout.addWidget(self.upload_button)
        layout.addWidget(self.remote_button)
        layout.addWidget(self.collect_button)
        layout.addWidget(self.clean_button)
        layout.addWidget(self.authorize_button)
        layout.addStretch(1)

        # Apply styling
        small_btn_css = (
            f"QPushButton {{ font-size: {Styles.SMALL_BUTTON_SIZE}; }}"
        )
        for btn in [
            self.generate_button,
            self.upload_button,
            self.remote_button,
            self.collect_button,
            self.clean_button,
            self.authorize_button,
        ]:
            btn.setStyleSheet(small_btn_css)

        self.setLayout(layout)

    def _handle_upload(self) -> None:
        if hasattr(self, "get_selected_report"):
            path = self.get_selected_report()
            self.actions.upload_report(path)
        else:
            self.actions.upload_report(None)

    def _handle_clean(self) -> None:
        if hasattr(self, "get_selected_report"):
            path = self.get_selected_report()
            self.actions.clean_reports(path)
        else:
            self.actions.clean_reports(None)

    def set_get_selected_report_callback(self, callback) -> None:
        """Set callback to get the currently selected report path."""
        self.get_selected_report = callback
