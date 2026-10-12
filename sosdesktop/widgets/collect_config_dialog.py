"""Configuration dialog for sos collect."""

import getpass

from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)

from ..constants import ClusterTypes, SettingsKeys, TransportTypes


class CollectConfigDialog(QDialog):
    """Dialog to configure sos collect options before running."""

    def __init__(self, settings: QSettings, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("sos collect — Configuration")
        self.setMinimumWidth(480)
        self.settings = settings
        self._build_ui()

    def _build_ui(self) -> None:
        main_layout = QVBoxLayout()
        form = QFormLayout()

        self.nodes_edit = QLineEdit()
        self.nodes_edit.setPlaceholderText("host1,host2 or regex")
        self.nodes_edit.setText(
            self.settings.value(SettingsKeys.COLLECT_NODES, "")
        )
        form.addRow("Nodes:", self.nodes_edit)

        self.primary_edit = QLineEdit()
        self.primary_edit.setPlaceholderText(
            "controller/primary node (optional)"
        )
        form.addRow("Primary:", self.primary_edit)

        self.cluster_combo = QComboBox()
        self.cluster_combo.addItems(ClusterTypes.TYPES)
        saved_ct = self.settings.value(
            SettingsKeys.COLLECT_CLUSTER_TYPE, ClusterTypes.TYPES[0]
        )
        idx = self.cluster_combo.findText(saved_ct)
        if idx >= 0:
            self.cluster_combo.setCurrentIndex(idx)
        form.addRow("Cluster type:", self.cluster_combo)

        self.transport_combo = QComboBox()
        self.transport_combo.addItems(TransportTypes.TYPES)
        saved_tr = self.settings.value(
            SettingsKeys.COLLECT_TRANSPORT, TransportTypes.TYPES[0]
        )
        idx = self.transport_combo.findText(saved_tr)
        if idx >= 0:
            self.transport_combo.setCurrentIndex(idx)
        form.addRow("Transport:", self.transport_combo)

        main_layout.addLayout(form)

        # SSH group
        ssh_group = QGroupBox("SSH")
        ssh_form = QFormLayout()

        self.ssh_user_edit = QLineEdit()
        self.ssh_user_edit.setPlaceholderText(getpass.getuser())
        ssh_form.addRow("User:", self.ssh_user_edit)

        key_layout = QHBoxLayout()
        self.ssh_key_edit = QLineEdit()
        self.ssh_key_edit.setPlaceholderText("/path/to/key.pem (optional)")
        browse_key_btn = QPushButton("Browse")
        browse_key_btn.clicked.connect(self._browse_key)
        key_layout.addWidget(self.ssh_key_edit)
        key_layout.addWidget(browse_key_btn)
        ssh_form.addRow("Key:", key_layout)

        self.ssh_port_spin = QSpinBox()
        self.ssh_port_spin.setRange(1, 65535)
        self.ssh_port_spin.setValue(22)
        ssh_form.addRow("Port:", self.ssh_port_spin)

        ssh_group.setLayout(ssh_form)
        main_layout.addWidget(ssh_group)

        # Additional options
        adv_form = QFormLayout()

        self.jobs_spin = QSpinBox()
        self.jobs_spin.setRange(1, 16)
        self.jobs_spin.setValue(4)
        adv_form.addRow("Parallel jobs:", self.jobs_spin)

        self.label_edit = QLineEdit()
        self.label_edit.setPlaceholderText("Archive label (optional)")
        adv_form.addRow("Label:", self.label_edit)

        self.no_local_check = QCheckBox("Skip localhost")
        adv_form.addRow("", self.no_local_check)

        main_layout.addLayout(adv_form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)

        self.setLayout(main_layout)

    def _browse_key(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select SSH key",
            "",
            "Key files (*.pem *.key *);;All files (*)",
        )
        if path:
            self.ssh_key_edit.setText(path)

    def _on_accept(self) -> None:
        self.settings.setValue(
            SettingsKeys.COLLECT_NODES, self.nodes_edit.text()
        )
        self.settings.setValue(
            SettingsKeys.COLLECT_CLUSTER_TYPE,
            self.cluster_combo.currentText(),
        )
        self.settings.setValue(
            SettingsKeys.COLLECT_TRANSPORT,
            self.transport_combo.currentText(),
        )
        self.accept()

    def build_args(self) -> list[str]:
        """Build sos collect CLI arguments from the current dialog state."""
        args = []

        nodes = self.nodes_edit.text().strip()
        if nodes:
            args.extend(["--nodes", nodes])

        primary = self.primary_edit.text().strip()
        if primary:
            args.extend(["--primary", primary])

        cluster = self.cluster_combo.currentText()
        if cluster != ClusterTypes.TYPES[0]:
            args.extend(["--cluster-type", cluster])

        transport = self.transport_combo.currentText()
        if transport != TransportTypes.TYPES[0]:
            args.extend(["--transport", transport])

        ssh_user = self.ssh_user_edit.text().strip()
        if ssh_user:
            args.extend(["--ssh-user", ssh_user])

        ssh_key = self.ssh_key_edit.text().strip()
        if ssh_key:
            args.extend(["--ssh-key", ssh_key])

        if self.ssh_port_spin.value() != 22:
            args.extend(["--ssh-port", str(self.ssh_port_spin.value())])

        if self.jobs_spin.value() != 4:
            args.extend(["--jobs", str(self.jobs_spin.value())])

        label = self.label_edit.text().strip()
        if label:
            args.extend(["--label", label])

        if self.no_local_check.isChecked():
            args.append("--no-local")

        return args
