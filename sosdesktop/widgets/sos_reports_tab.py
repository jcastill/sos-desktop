"""SOS Reports table widget."""

import os
from datetime import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QAbstractItemView,
    QFileIconProvider,
    QHeaderView,
    QLabel,
    QMenu,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..constants import Paths
from ..utils import find_sos_reports, human_readable_size


class SosReportsTab(QWidget):
    """Tab widget displaying SOS reports table."""

    def __init__(self, on_open_callback, parent=None) -> None:
        super().__init__(parent)
        self.on_open_callback = on_open_callback
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout()

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(
            ["Name", "Modified", "Size", "Path"]
        )
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeMode.Stretch
        )
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.table.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.table.customContextMenuRequested.connect(
            self._open_context_menu
        )
        self.table.doubleClicked.connect(self._open_selected_file)

        self._empty_label = QLabel(
            f"No sos reports found in {Paths.VAR_TMP}.\n"
            'Click "Generate Report" to create one.'
        )
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.setStyleSheet(
            "QLabel { color: rgb(160,160,160); font-size: 13px; }"
        )

        self._stack = QStackedWidget()
        self._stack.addWidget(self.table)         # index 0
        self._stack.addWidget(self._empty_label)  # index 1

        layout.addWidget(self._stack)
        self.setLayout(layout)

    def refresh(self) -> None:
        """Refresh the table with current SOS reports."""
        reports = find_sos_reports()
        self.table.setRowCount(0)

        if not reports:
            self._stack.setCurrentIndex(1)
            return

        self._stack.setCurrentIndex(0)
        icon_provider = QFileIconProvider()

        for path, size in reports:
            row = self.table.rowCount()
            self.table.insertRow(row)

            name_item = QTableWidgetItem(os.path.basename(path))
            name_item.setIcon(
                icon_provider.icon(QFileIconProvider.IconType.File)
            )
            name_item.setData(Qt.ItemDataRole.UserRole, path)

            try:
                mtime = os.path.getmtime(path)
                modified_text = datetime.fromtimestamp(mtime).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            except OSError:
                modified_text = "-"

            modified_item = QTableWidgetItem(modified_text)
            size_item = QTableWidgetItem(human_readable_size(size))
            path_item = QTableWidgetItem(path)

            for item in [name_item, modified_item, size_item, path_item]:
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

            self.table.setItem(row, 0, name_item)
            self.table.setItem(row, 1, modified_item)
            self.table.setItem(row, 2, size_item)
            self.table.setItem(row, 3, path_item)

        self.table.resizeRowsToContents()

    def get_selected_path(self) -> str | None:
        """Return the path of the currently selected report."""
        selected = self.table.selectedItems()
        if not selected:
            return None
        row = selected[0].row()
        item = self.table.item(row, 0)
        return item.data(Qt.ItemDataRole.UserRole)

    def _open_context_menu(self, pos) -> None:
        path = self.get_selected_path()
        if not path:
            return

        menu = QMenu(self)
        open_file = menu.addAction("Open file")
        open_folder = menu.addAction("Open containing folder")
        copy_path = menu.addAction("Copy path")

        action = menu.exec(self.table.viewport().mapToGlobal(pos))

        if action == open_file:
            self.on_open_callback(path)
        elif action == open_folder:
            self.on_open_callback(os.path.dirname(path))
        elif action == copy_path:
            QApplication.clipboard().setText(path)

    def _open_selected_file(self) -> None:
        path = self.get_selected_path()
        if path:
            self.on_open_callback(path)
