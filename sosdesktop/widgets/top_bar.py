"""Top bar widget with case ID configuration."""

from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QWidget,
    QComboBox,
    QCheckBox,
)

from ..constants import SettingsKeys, Styles, UploadTargets


class TopBar(QWidget):
    """Top bar containing case ID, upload target, verbosity, and refresh."""

    def __init__(
        self, settings: QSettings, on_refresh_callback, parent=None
    ) -> None:
        super().__init__(parent)
        self.settings = settings
        self._setup_ui(on_refresh_callback)

    def _setup_ui(self, on_refresh_callback) -> None:
        layout = QHBoxLayout()

        # Case ID input
        layout.addWidget(QLabel("Case:"))
        self.case_id_edit = QLineEdit()
        self.case_id_edit.setPlaceholderText("Case ID (optional)")
        self.case_id_edit.setText(
            self.settings.value(SettingsKeys.CASE_ID, "")
        )
        self.case_id_edit.textChanged.connect(
            lambda text: self.settings.setValue(SettingsKeys.CASE_ID, text)
        )
        self.case_id_edit.setStyleSheet(
            (
                "QLineEdit { color: rgb(240,240,240); }\n"
                "QLineEdit::placeholder { color: rgb(180,180,180); }"
            )
        )
        layout.addWidget(self.case_id_edit)

        # Upload target selector
        layout.addWidget(QLabel("Upload Target:"))
        self.upload_target_combo = QComboBox()
        # Available upload targets from sos source code
        # See: sos upload --help | grep upload-target
        self.upload_target_combo.addItems(UploadTargets.all())
        # Load saved target or default to UploadTargets.AUTO
        saved_target = self.settings.value(
            SettingsKeys.UPLOAD_TARGET, UploadTargets.AUTO
        )
        index = self.upload_target_combo.findText(saved_target)
        if index >= 0:
            self.upload_target_combo.setCurrentIndex(index)
        self.upload_target_combo.currentTextChanged.connect(
            lambda text: self.settings.setValue(
                SettingsKeys.UPLOAD_TARGET, text
            )
        )
        layout.addWidget(self.upload_target_combo)

        # Verbosity checkbox
        self.verbosity_checkbox = QCheckBox("Verbose")
        self.verbosity_checkbox.setChecked(
            self.settings.value(
                SettingsKeys.VERBOSE_ENABLED, False, type=bool
            )
        )
        self.verbosity_checkbox.setToolTip(
            "Enable verbose output: adds -vvvv to sos commands"
        )
        self.verbosity_checkbox.stateChanged.connect(
            lambda state: self.settings.setValue(
                SettingsKeys.VERBOSE_ENABLED, bool(state)
            )
        )
        layout.addWidget(self.verbosity_checkbox)

        layout.addStretch(1)

        # Refresh button
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(on_refresh_callback)
        layout.addWidget(self.refresh_button)

        self.refresh_button.setStyleSheet(
            f"QPushButton {{ font-size: {Styles.SMALL_BUTTON_SIZE}; }}"
        )

        self.setLayout(layout)

    def get_case_id(self) -> str:
        """Return the current case ID."""
        return self.case_id_edit.text().strip()

    def get_upload_target(self) -> str:
        """Return the current upload target."""
        target = self.upload_target_combo.currentText()
        return target if target != UploadTargets.AUTO else ""

    def get_verbosity(self) -> int:
        """Return the current verbosity level (0 or 4)."""
        return 4 if self.verbosity_checkbox.isChecked() else 0
