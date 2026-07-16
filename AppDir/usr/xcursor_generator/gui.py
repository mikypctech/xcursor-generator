# xcursor_generator/gui.py
import os
import sys
import tempfile       # <--- Add this!
import zipfile        # <--- Add this!
import shutil         # <--- Add this!
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QComboBox, QLineEdit, QLabel, QPushButton,
    QFileDialog, QGroupBox, QHeaderView, QMessageBox
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon

from xcursor_generator.converter import get_preview_pixmap
from xcursor_generator.packer import pack_theme
from xcursor_generator.autogenerator import get_best_match

# In xcursor_generator/gui.py
from xcursor_generator.cursor_database import CURSOR_TYPES

from xcursor_generator.hotspot import get_default_hotspot

class XCursorGenerator(QMainWindow):
    def __init__(self, version=""):
        super().__init__()
        self.setWindowTitle(
            f"xcursor Theme Generator {version}"
        )
        self.resize(800, 500)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        title_label = QLabel("Theme Generation")
        font = title_label.font()
        font.setPointSize(20)
        font.setBold(True)
        title_label.setFont(font)
        main_layout.addWidget(title_label)

        # Assets Table Section
        assets_group = QGroupBox("Assets")
        assets_layout = QVBoxLayout()

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(
            ["Image", "Name", "Type", "Hotspot"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.verticalHeader().setDefaultSectionSize(40)
        self.table.setIconSize(QSize(32, 32))

        assets_layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Add Files")
        self.btn_add.clicked.connect(self.add_files)
        self.btn_remove = QPushButton("Remove Selected")
        self.btn_remove.clicked.connect(self.remove_selected)
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_remove)
        assets_layout.addLayout(btn_layout)

        assets_group.setLayout(assets_layout)
        main_layout.addWidget(assets_group)

        # Metadata / Index Section
        index_group = QGroupBox("Index")
        index_layout = QHBoxLayout()

        left_meta = QVBoxLayout()

        author_layout = QHBoxLayout()
        author_layout.addWidget(QLabel("Author ="))
        self.txt_author = QLineEdit()
        self.txt_author.setPlaceholderText("e.g. YourName")
        author_layout.addWidget(self.txt_author)
        left_meta.addLayout(author_layout)

        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name   ="))
        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("e.g. MyAwesomeCursors")
        name_layout.addWidget(self.txt_name)
        left_meta.addLayout(name_layout)

        comment_layout = QHBoxLayout()
        comment_layout.addWidget(QLabel("Comment ="))
        self.txt_comment = QLineEdit()
        self.txt_comment.setPlaceholderText("e.g. A sleek cursor theme")
        comment_layout.addWidget(self.txt_comment)
        left_meta.addLayout(comment_layout)

        index_layout.addLayout(left_meta)

        right_meta = QVBoxLayout()
        fallback_layout = QHBoxLayout()
        fallback_layout.addWidget(QLabel("Fallback ="))
        self.txt_fallback = QLineEdit("Adwaita")
        fallback_layout.addWidget(self.txt_fallback)
        right_meta.addLayout(fallback_layout)
        right_meta.addStretch()
        index_layout.addLayout(right_meta)

        index_group.setLayout(index_layout)
        main_layout.addWidget(index_group)

        # Generate Button
        self.btn_generate = QPushButton("Generate Theme (.tar.gz)")
        self.btn_generate.setStyleSheet("font-weight: bold; height: 35px;")
        self.btn_generate.clicked.connect(self.handle_generation)
        main_layout.addWidget(self.btn_generate)

        # Add this to your __init__ layout
        self.btn_auto = QPushButton("Automatically add and map files")
        self.btn_auto.clicked.connect(self.prompt_auto_map)
        main_layout.addWidget(self.btn_auto)

    def prompt_auto_map(self):
        # 1. Show warning
        reply = QMessageBox.question(self, 'Warning',
            "This function relies on file names. It may not be 100% accurate. "
            "Please check the assignments after importing. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.No:
            return

        # 2. Choice: Folder or Compressed
        choice = QMessageBox(self)
        choice.setText("Select your import source:")
        btn_folder = choice.addButton("Folder", QMessageBox.ButtonRole.ActionRole)
        btn_zip = choice.addButton("Compressed (.zip/.rar/.7z)", QMessageBox.ButtonRole.ActionRole)
        choice.exec()

        if choice.clickedButton() == btn_folder:
            path = QFileDialog.getExistingDirectory(self, "Select Folder")
            if path: self.import_from_path(path, is_dir=True)
        elif choice.clickedButton() == btn_zip:
            path, _ = QFileDialog.getOpenFileName(self, "Select Archive", "", "Archives (*.zip *.rar *.7z)")
            if path: self.import_from_path(path, is_dir=False)

    def import_from_path(self, path, is_dir):
        files = []
        if is_dir:
            self.txt_name.setText(os.path.basename(path))
            files = [os.path.join(path, f) for f in os.listdir(path) if f.lower().endswith(('.cur', '.ani', '.png'))]
        else:
            self.txt_name.setText(os.path.splitext(os.path.basename(path))[0])
            # Create a secure temp directory to extract the files
            tmp_extract = tempfile.mkdtemp()
            shutil.unpack_archive(path, tmp_extract)
            for root, _, filenames in os.walk(tmp_extract):
                for f in filenames:
                    if f.lower().endswith(('.cur', '.ani', '.png')):
                        files.append(os.path.join(root, f))

        # Populate Table
        for f in files:
            self.add_single_file(f)

    def add_single_file(self, file_path):
        row = self.table.rowCount()
        self.table.insertRow(row)

        # 1. Preview
        preview_item = QTableWidgetItem()
        pixmap = get_preview_pixmap(file_path)
        if pixmap: preview_item.setIcon(QIcon(pixmap))
        self.table.setItem(row, 0, preview_item)

        # 2. Name
        file_name = os.path.basename(file_path)
        item_name = QTableWidgetItem(file_name)
        item_name.setData(Qt.ItemDataRole.UserRole, file_path)
        self.table.setItem(row, 1, item_name)

        # 3. Auto-Mapping using our new file!
        combo = QComboBox()
        combo.addItems(CURSOR_TYPES)
        # Call the function from the new file
        best_match = get_best_match(file_name)
        combo.setCurrentText(best_match)

        self.table.setCellWidget(row, 2, combo)
        if file_path.lower().endswith(".png"):
            hotspot_text = "auto"
        else:
            hotspot_text = "embedded"

        self.table.setItem(
            row,
            3,
            QTableWidgetItem(hotspot_text)
        )
    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Cursor Files", "", "Cursor Files (*.cur *.ani *.png);;All Files (*)"
        )
        for file_path in files:
            row = self.table.rowCount()
            self.table.insertRow(row)

            # 1. Generate and display preview
            preview_item = QTableWidgetItem()
            pixmap = get_preview_pixmap(file_path)
            if pixmap and not pixmap.isNull():
                preview_item.setIcon(QIcon(pixmap))
            else:
                preview_item.setText("❓")
            self.table.setItem(row, 0, preview_item)

            # 2. Add filename and store absolute path
            file_name = os.path.basename(file_path)
            item_name = QTableWidgetItem(file_name)
            item_name.setData(Qt.ItemDataRole.UserRole, file_path)
            self.table.setItem(row, 1, item_name)

            # 3. Handle Dropdown
            combo = QComboBox()
            combo.addItems(CURSOR_TYPES)

            lower_name = file_name.lower()
            if "link" in lower_name or "pointer" in lower_name:
                combo.setCurrentText("pointer")
            elif "main" in lower_name or "arrow" in lower_name or "ptr" in lower_name:
                combo.setCurrentText("left_ptr")

            self.table.setCellWidget(row, 2, combo)
            if file_path.lower().endswith(".png"):
                hotspot_text = "auto"
            else:
                hotspot_text = "embedded"

            self.table.setItem(
                row,
                3,
                QTableWidgetItem(hotspot_text)
            )

    def remove_selected(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.table.removeRow(current_row)

    def handle_generation(self):
        theme_name = self.txt_name.text().strip()
        author = self.txt_author.text().strip()
        comment = self.txt_comment.text().strip()
        fallback = self.txt_fallback.text().strip()

        if not theme_name:
            QMessageBox.warning(self, "Warning", "Theme Name is required!")
            return

        if self.table.rowCount() == 0:
            QMessageBox.warning(self, "Warning", "No cursor assets added to convert!")
            return

        save_path, _ = QFileDialog.getSaveFileName(
            self, "Save Theme Package", f"{theme_name}.tar.gz", "Tarball Archives (*.tar.gz)"
        )
        if not save_path:
            return

        # Build assets list from table data
        assets = []

        for row in range(self.table.rowCount()):

            src_path = self.table.item(
                row,
                1
            ).data(Qt.ItemDataRole.UserRole)

            target_type = self.table.cellWidget(
                row,
                2
            ).currentText()

            hotspot_item = self.table.item(
                row,
                3
            )

            hotspot = None

            if hotspot_item:
                if hotspot_item.text() == "auto":
                    hotspot = "auto"

                elif hotspot_item.text() == "embedded":
                    hotspot = "embedded"


            assets.append({
                "path": src_path,
                "type": target_type,
                "hotspot": hotspot,
            })

        # Hand off to the backend packer!
        success, error_msg = pack_theme(save_path, theme_name, author, comment, fallback, assets)

        if success:
            QMessageBox.information(self, "Success", f"Theme '{theme_name}' generated successfully!")
        else:
            QMessageBox.critical(self, "Error", f"Failed to generate theme: {error_msg}")
