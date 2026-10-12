import fcntl
import os
import shutil
import subprocess
from typing import Callable, Optional

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import (
    QLabel,
    QMessageBox,
    QProgressBar,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class SosRunner(QWidget):
    def __init__(self, on_finished_callback: Callable[[], None]):
        super().__init__()
        self.on_finished_callback = on_finished_callback
        self.process: subprocess.Popen[str] | None = None
        self._post_run_cleanup: Optional[Callable[[], None]] = None
        self.output_view = QTextEdit()
        self.output_view.setReadOnly(True)
        self.status_label = QLabel("Ready")
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setVisible(False)
        self._stdout_fd: Optional[int] = None
        self._stderr_fd: Optional[int] = None
        self._poll_timer = QTimer(self)
        self._poll_timer.setInterval(100)
        self._poll_timer.timeout.connect(self._poll_process)

        layout = QVBoxLayout()
        layout.addWidget(self.output_view)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)
        self.setLayout(layout)

    def append_output(self, text: str) -> None:
        self.output_view.append(text)
        cursor = self.output_view.textCursor()
        self.output_view.moveCursor(cursor.MoveOperation.End)

    def run_process(
        self,
        program: str,
        args: list[str],
        start_message: str,
        post_run_cleanup: Optional[Callable[[], None]] = None,
        elevate: bool = False,
        command_name: str = "sos",
    ) -> None:
        if self.process is not None:
            QMessageBox.information(
                self,
                "Already running",
                "Another task is already in progress.",
            )
            return
        self._post_run_cleanup = post_run_cleanup
        self._command_name = command_name
        self.output_view.clear()
        self.status_label.setText(start_message)
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setVisible(True)

        if elevate:
            if not shutil.which("pkexec"):
                QMessageBox.critical(
                    self, "Error",
                    "Cannot run command, no 'pkexec' tool found."
                )
                self.progress_bar.setVisible(False)
                return
            cmd: list[str] = ["pkexec", program, *args]
        else:
            cmd = [program, *args]

        try:
            # pylint: disable=consider-using-with
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                text=True,
                bufsize=1,
            )
            assert self.process.stdout is not None
            assert self.process.stderr is not None

            self._stdout_fd = self.process.stdout.fileno()
            self._stderr_fd = self.process.stderr.fileno()
            _set_nonblocking(self._stdout_fd)
            _set_nonblocking(self._stderr_fd)
            self._poll_timer.start()
        except Exception as exc:  # noqa: BLE001
            self.append_output(str(exc))
            QMessageBox.critical(self, "Failed to start", str(exc))
            self.process = None
            self.progress_bar.setVisible(False)
            return

    def _poll_process(self) -> None:
        if self.process is None:
            return
        try:
            if self._stdout_fd is not None:
                try:
                    data = os.read(self._stdout_fd, 4096).decode(
                        errors="ignore"
                    )
                except BlockingIOError:
                    data = ""
                if data:
                    self.append_output(data)
                    pct = _extract_percent_from_text(data)
                    if pct is not None:
                        if self.progress_bar.maximum() == 0:
                            self.progress_bar.setRange(0, 100)
                        self.progress_bar.setValue(pct)
            if self._stderr_fd is not None:
                try:
                    err = os.read(self._stderr_fd, 4096).decode(
                        errors="ignore"
                    )
                except BlockingIOError:
                    err = ""
                if err:
                    self.append_output(err)
        except Exception:  # noqa: BLE001
            pass

        ret = self.process.poll()
        if ret is not None:
            self._poll_timer.stop()
            self._finished(ret)

    def _finished(self, exit_code: int) -> None:
        # pkexec exit codes: 126 = user dismissed/failed the polkit prompt,
        # 127 = not authorized by policy. Everything else comes from the
        # target program (e.g. sos).
        name = getattr(self, "_command_name", "sos")
        if exit_code == 126:
            self.status_label.setText("Cancelled")
        elif exit_code == 127:
            self.status_label.setText("Not authorized")
            QMessageBox.warning(
                self,
                name,
                "Not authorized to run this command "
                "(polkit policy denied it).",
            )
        elif exit_code != 0:
            self.status_label.setText(
                f"Finished with error (code {exit_code})"
            )
            QMessageBox.warning(
                self,
                name,
                f"{name} finished with exit code {exit_code}.",
            )
        else:
            self.status_label.setText("Completed successfully.")
        self.process = None
        QTimer.singleShot(500, self.on_finished_callback)
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        if self._post_run_cleanup is not None:
            try:
                self._post_run_cleanup()
            except Exception:  # noqa: BLE001
                pass
            self._post_run_cleanup = None


def _extract_percent_from_text(text: str) -> Optional[int]:
    for token in text.split():
        if token.endswith("%"):
            num = token[:-1]
            if num.isdigit():
                val = int(num)
                if 0 <= val <= 100:
                    return val
    return None


def _set_nonblocking(fd: int) -> None:
    flags = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
