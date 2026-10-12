"""File operations utilities."""

import shutil
import subprocess

from PyQt6.QtWidgets import QMessageBox


def open_path(path: str, parent_widget=None) -> None:
    """Open a file or directory using the system default application."""
    try:
        # Prefer xdg-open, fallback to gio
        opener = shutil.which("xdg-open") or shutil.which("gio")
        if opener is None:
            raise RuntimeError("No opener found (xdg-open/gio)")

        subprocess.Popen([opener, path])  # pylint: disable=consider-using-with
    except Exception as exc:
        if parent_widget:
            QMessageBox.warning(
                parent_widget, "Open", f"Failed to open: {exc}"
            )
        else:
            raise
