from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QTextEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QRadioButton, QButtonGroup, QTabWidget,
    QToolTip, QListWidget, QMessageBox
)
from PySide6.QtGui import QIcon, QFont, QPalette, QColor
from PySide6.QtCore import Qt
import sys, datetime, os, json
from lang import encrypt, decrypt


class CipherNotes(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cipher Notes")
        self.setFixedSize(700, 600)
        self.setWindowIcon(QIcon("logo_32.png"))

        self.result = ""
        self.dark_mode = True
        self.default_font = QFont("Consolas", 11)

        self.load_theme_preference()

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.main_tab = QWidget()
        self.notes_tab = QWidget()

        self.tabs.addTab(self.main_tab, "Main")
        self.tabs.addTab(self.notes_tab, "Notes Viewer")

        self.init_main_tab()
        self.init_notes_tab()
        self.apply_theme()

    def init_main_tab(self):
        layout = QVBoxLayout(self.main_tab)

        tools_layout = QHBoxLayout()
        self.theme_btn = QPushButton("🌓")
        self.theme_btn.setCursor(Qt.PointingHandCursor)
        self.theme_btn.setFixedSize(30, 30)
        tools_layout.addWidget(self.theme_btn)
        tools_layout.addStretch()
        layout.addLayout(tools_layout)

        self.status_display = QLabel("")
        self.status_display.setFont(QFont("Segoe UI", 9))
        self.status_display.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_display)

        self.title = QLabel("Cipher Notes")
        self.title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        self.title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title)

        radio_layout = QHBoxLayout()
        self.encrypt_radio = QRadioButton("Encrypt")
        self.decrypt_radio = QRadioButton("Decrypt")
        self.encrypt_radio.setChecked(True)
        for btn in (self.encrypt_radio, self.decrypt_radio):
            btn.setFont(QFont("Segoe UI", 10))
            btn.toggled.connect(self.clear_input_on_toggle)
            radio_layout.addWidget(btn)
        layout.addLayout(radio_layout)

        self.input_text = QTextEdit()
        self.input_text.setFont(self.default_font)
        self.input_text.setPlaceholderText("Type your message here...")
        self.input_text.textChanged.connect(self.process_live)
        layout.addWidget(self.input_text)

        self.result_display = QTextEdit()
        self.result_display.setFont(self.default_font)
        self.result_display.setReadOnly(True)
        self.result_display.setPlaceholderText("Encrypted/Decrypted result here...")
        self.result_display.setFixedHeight(130)
        layout.addWidget(self.result_display)

        buttons = QHBoxLayout()
        self.copy_btn = QPushButton("Copy")
        self.clear_btn = QPushButton("Clear")
        self.save_btn = QPushButton("Save")
        for btn in (self.copy_btn, self.clear_btn, self.save_btn):
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(40)
            buttons.addWidget(btn)
        layout.addLayout(buttons)

        self.copy_btn.clicked.connect(self.copy_result)
        self.clear_btn.clicked.connect(self.clear_all)
        self.save_btn.clicked.connect(self.save_to_notes)
        self.theme_btn.clicked.connect(self.toggle_theme)

    def init_notes_tab(self):
        layout = QVBoxLayout()
        self.notes_list = QListWidget()
        self.notes_list.setFont(self.default_font)
        layout.addWidget(self.notes_list)

        delete_btn = QPushButton("🗑️ Delete Selected Line")
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.clicked.connect(self.delete_selected_note)
        layout.addWidget(delete_btn)

        self.notes_tab.setLayout(layout)
        self.load_notes()

    def load_notes(self):
        self.notes_list.clear()
        if os.path.exists("ciphernotes.txt"):
            with open("ciphernotes.txt", "r", encoding="utf-8") as f:
                for line in f.readlines():
                    if line.strip():
                        self.notes_list.addItem(line.strip())

    def delete_selected_note(self):
        item = self.notes_list.currentItem()
        if item is None:
            self.update_status("⚠️ No line selected to delete", success=False)
            return

        row = self.notes_list.currentRow()
        item_text = item.text()
        confirm = QMessageBox.question(self, "Confirm Delete", f"Delete this line?\n\n{item_text}")
        if confirm == QMessageBox.Yes:
            self.notes_list.takeItem(row)
            with open("ciphernotes.txt", "w", encoding="utf-8") as f:
                for i in range(self.notes_list.count()):
                    f.write(self.notes_list.item(i).text() + "\n")
            self.update_status("🗑️ Deleted line", success=True)

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.save_theme_preference()
        self.apply_theme()

    def apply_theme(self):
        if self.dark_mode:
            self.setStyleSheet("background-color: #1e1e2e;")
            self.result_display.setStyleSheet("background:#313244; color:#a6e3a1; padding:10px;")
            self.input_text.setStyleSheet("background:#313244; color:#f2f2f2; padding:10px;")
            self.status_display.setStyleSheet("color:#a6e3a1;")
            self.notes_list.setStyleSheet("background:#2a2a3a; color:#eeeeee;")
        else:
            self.setStyleSheet("")
            self.result_display.setStyleSheet("background:#ffffff; color:#000; padding:10px;")
            self.input_text.setStyleSheet("background:#ffffff; color:#000; padding:10px;")
            self.status_display.setStyleSheet("color:#000000;")
            self.notes_list.setStyleSheet("background:#ffffff; color:#000000;")

    def save_theme_preference(self):
        with open("theme.json", "w") as f:
            json.dump({"dark_mode": self.dark_mode}, f)

    def load_theme_preference(self):
        if os.path.exists("theme.json"):
            with open("theme.json", "r") as f:
                try:
                    data = json.load(f)
                    self.dark_mode = data.get("dark_mode", True)
                except:
                    self.dark_mode = True

    def update_status(self, message, success=True):
        color = "#a6e3a1" if success else "#f38ba8"
        self.status_display.setStyleSheet(f"color: {color};")
        self.status_display.setText(message)

    def clear_input_on_toggle(self):
        self.input_text.clear()
        self.result_display.setText("")
        self.status_display.clear()

    def clear_all(self):
        self.input_text.clear()
        self.result_display.setText("")
        self.status_display.clear()
        self.result = ""

    def process_live(self):
        text = self.input_text.toPlainText().strip()
        if not text:
            self.result_display.setText("")
            return
        try:
            new_result = encrypt(text) if self.encrypt_radio.isChecked() else decrypt(text)
            if new_result != self.result:
                self.result = new_result
                self.result_display.setText(self.result)
        except:
            self.result_display.setText("❌ Invalid input")

    def copy_result(self):
        if not self.result:
            self.update_status("⚠️ Nothing to copy", success=False)
            return
        QApplication.clipboard().setText(self.result)
        self.update_status("✅ Copied to clipboard", success=True)

    def save_to_notes(self):
        if not self.result:
            self.update_status("⚠️ Nothing to save", success=False)
            return
        mode = "ENCRYPTED" if self.encrypt_radio.isChecked() else "DECRYPTED"
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"{mode} [{timestamp}]: {self.result}"
        with open("ciphernotes.txt", "a", encoding="utf-8") as f:
            f.write(entry + "\n")
        self.load_notes()
        self.update_status("✅ Saved to notes", success=True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("logo_256.ico"))  # Taskbar icon
    window = CipherNotes()
    window.show()
    sys.exit(app.exec())
