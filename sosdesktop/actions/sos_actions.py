"""SOS command action handlers."""

import os
import shutil
import subprocess

from PyQt6.QtWidgets import QMessageBox, QInputDialog

from ..sos_runner import SosRunner


class SosActions:
    """Handles execution of all SOS-related commands."""

    def __init__(
        self,
        parent_widget,
        runner: SosRunner,
        get_case_id_callback,
        get_upload_target_callback,
        get_verbosity_callback,
        settings=None,
    ) -> None:
        self.parent = parent_widget
        self.runner = runner
        self.get_case_id = get_case_id_callback
        self.get_upload_target = get_upload_target_callback
        self.get_verbosity = get_verbosity_callback
        self.settings = settings

    def _get_verbosity_flags(self) -> list[str]:
        """Build verbosity flags based on current verbosity level."""
        verbosity = self.get_verbosity()
        if verbosity <= 0:
            return []
        # Build -v, -vv, -vvv, or -vvvv based on level
        return ["-" + "v" * min(verbosity, 4)]

    def generate_report(self) -> None:
        """Generate a new SOS report."""
        sos_path = shutil.which("sos")
        if not sos_path:
            QMessageBox.critical(
                self.parent,
                "sos not found",
                (
                    "The 'sos' utility is not installed. Install the 'sos' "
                    "package and try again."
                ),
            )
            return

        args = ["report", "--batch"]
        case_id = self.get_case_id()
        if case_id:
            args.extend(["--case-id", case_id])
        args.extend(self._get_verbosity_flags())

        self.runner.run_process(
            program=sos_path,
            args=args,
            start_message=(
                "Starting sos report... "
                "Authenticate in the polkit prompt if asked."
            ),
            elevate=True,
            command_name="sos report",
        )

    def upload_report(self, report_path: str | None) -> None:
        """Upload the selected SOS report."""
        if not report_path:
            QMessageBox.information(
                self.parent,
                "Upload",
                "Select a report to upload.",
            )
            return
        sos_path = shutil.which("sos")
        if not sos_path:
            QMessageBox.critical(
                self.parent, "Upload", "'sos' not found on system"
            )
            return

        case_id = self.get_case_id()
        upload_target = self.get_upload_target()

        args = ["upload"]
        if case_id:
            args.extend(["--case-id", case_id])
        if upload_target:
            args.extend(["--upload-target", upload_target])
        args.extend(self._get_verbosity_flags())
        args.append(report_path)

        self.runner.run_process(
            program=sos_path,
            args=args,
            start_message=(
                f"Uploading {os.path.basename(report_path)} via sos upload…"
            ),
            elevate=True,
            command_name="sos upload",
        )

    def generate_remote_report(self) -> None:
        """Generate SOS report on a remote host via SSH."""
        if not shutil.which("ssh"):
            QMessageBox.critical(
                self.parent, "Remote Report", "'ssh' not found in PATH"
            )
            return

        target, ok = QInputDialog.getText(
            self.parent,
            "Remote Host",
            "Enter SSH target (e.g., user@host):",
        )
        if not ok or not target.strip():
            return

        case_id = self.get_case_id()
        remote_cmd = ["sudo", "sos", "report", "--batch"]
        if case_id:
            remote_cmd.extend(["--case-id", case_id])

        ssh_args = ["ssh", target.strip(), " ".join(remote_cmd)]

        self.runner.run_process(
            program="ssh",
            args=ssh_args[1:],
            start_message=f"Generating sos report on {target.strip()}…",
            command_name="sos report (remote)",
        )

    def collect_reports(self) -> None:
        """Open collect configuration dialog then run sos collect."""
        from ..widgets.collect_config_dialog import CollectConfigDialog

        sos_path = shutil.which("sos")
        if not sos_path:
            QMessageBox.critical(
                self.parent, "Collect", "'sos' not found on system"
            )
            return

        dialog = CollectConfigDialog(self.settings, self.parent)
        if not dialog.exec():
            return

        args = ["collect", "--batch"] + dialog.build_args()
        case_id = self.get_case_id()
        if case_id:
            args.extend(["--case-id", case_id])
        args.extend(self._get_verbosity_flags())

        self.runner.run_process(
            program=sos_path,
            args=args,
            start_message="Running 'sos collect'…",
            elevate=True,
            command_name="sos collect",
        )

    def clean_reports(self, report_path: str | None) -> None:
        """Obfuscate sensitive data in the selected sos report archive."""
        if not report_path:
            QMessageBox.information(
                self.parent,
                "Clean / Mask",
                "Select a report to obfuscate.",
            )
            return

        sos_path = shutil.which("sos")
        if not sos_path:
            QMessageBox.critical(
                self.parent, "Clean / Mask", "'sos' not found on system"
            )
            return

        keywords, ok = QInputDialog.getText(
            self.parent,
            "Additional keywords (optional)",
            "Comma-separated words to obfuscate (e.g. myhost,10.0.0.0/8):",
        )
        if not ok:
            return

        confirm = QMessageBox.question(
            self.parent,
            "Confirm obfuscation",
            (
                "Create an obfuscated copy of:\n"
                f"{os.path.basename(report_path)}\n\n"
                "IPs, MACs, hostnames, and any supplied keywords will be "
                "replaced with consistent fake values.\n\n"
                "The original archive is not modified. Continue?"
            ),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        args = ["clean", "--batch", report_path]
        for kw in [k.strip() for k in keywords.split(",") if k.strip()]:
            args.extend(["--keywords", kw])
        args.extend(self._get_verbosity_flags())

        self.runner.run_process(
            program=sos_path,
            args=args,
            start_message=(
                f"Obfuscating {os.path.basename(report_path)}… "
                "This may take a few minutes."
            ),
            elevate=True,
            command_name="sos clean",
        )

    def authorize_system(self) -> None:
        """Pre-authorize this system for sos uploads (stores auth token)."""
        sos_path = shutil.which("sos")
        if not sos_path:
            QMessageBox.critical(
                self.parent,
                "Authorize System",
                "'sos' not found on system.",
            )
            return

        try:
            help_out = subprocess.run(
                [sos_path, "upload", "--help"],
                capture_output=True, text=True, timeout=10,
                check=False,
            ).stdout
        except Exception:
            help_out = ""

        if "--preauth" not in help_out:
            QMessageBox.warning(
                self.parent,
                "Authorize System",
                "The installed version of sos does not support --preauth.\n"
                "Upgrade sos to use this feature.",
            )
            return

        upload_target = self.get_upload_target()
        args = ["upload", "--preauth", "--batch"]
        if upload_target:
            args.extend(["--upload-target", upload_target])

        self.runner.run_process(
            program=sos_path,
            args=args,
            start_message=(
                "Pre-authorizing system for sos uploads… "
                "Authenticate in the polkit prompt if asked."
            ),
            elevate=True,
            command_name="sos upload --preauth",
        )
