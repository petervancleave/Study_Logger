import sys
import sqlite3
from datetime import datetime
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, 
                           QVBoxLayout, QHBoxLayout, QWidget, QDialog,
                           QSpinBox, QDialogButtonBox, QRadioButton, QButtonGroup)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QFontDatabase

class HackingTracker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Study Logger")
        self.setMinimumSize(800, 600)
        
        # Set application-wide font
        font_id = QFontDatabase.addApplicationFont("https://github.com/JetBrains/JetBrainsMono/raw/master/fonts/ttf/JetBrainsMono-Regular.ttf")
        if font_id != -1:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        else:
            font_family = "JetBrains Mono"
        app_font = QFont(font_family, 10)
        QApplication.setFont(app_font)
        
        self.is_tracking = False
        self.current_session_time = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.setup_database()
        self.setup_ui()

    def setup_database(self):
        self.conn = sqlite3.connect('tracker.db')
        self.cursor = self.conn.cursor()
        
        # Create sessions table if it doesn't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                duration INTEGER
            )
        ''')
        self.conn.commit()

    def setup_ui(self):
        # Set dark theme
        self.setStyleSheet('''
            QMainWindow {
                background-color: #0D0D0D;
            }
            QWidget {
                background-color: #1A1A1A;
                font-family: "JetBrains Mono";
            }
            QLabel {
                color: #B3B3B3;
                font-family: "JetBrains Mono";
            }
            QPushButton {
                background-color: #E6B400 !important;
                color: #0D0D0D;
                border: none;
                padding: 10px;
                padding-left: 15px;
                padding-right: 15px;
                border-radius: 5px;
                min-width: 100px;
                font-family: "JetBrains Mono";
            }
            QPushButton:hover {
                background-color: #CCa000 !important;
            }
            QPushButton:pressed {
                background-color: #B39000 !important;
            }
            QSpinBox {
                background-color: #1A1A1A;
                color: #B3B3B3;
                border: 1px solid #E6B400;
                border-radius: 3px;
                padding: 5px;
            }
            QRadioButton {
                color: #B3B3B3;
            }
            QRadioButton::indicator {
                border: 2px solid #E6B400;
            }
            QRadioButton::indicator:checked {
                background-color: #E6B400;
            }
        ''')

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Timer display
        self.time_label = QLabel("00:00:00")
        self.time_label.setFont(QFont("JetBrains Mono", 48))
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.time_label)

        # Total time tracked
        self.total_time_label = QLabel("Total Time: 0.00 hours")
        self.total_time_label.setFont(QFont("JetBrains Mono", 14))
        self.total_time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.total_time_label)

        # Control buttons
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start Session")
        self.start_button.clicked.connect(self.toggle_tracking)
        button_layout.addWidget(self.start_button)
        
        self.adjust_time_button = QPushButton("Adjust Time")
        self.adjust_time_button.clicked.connect(self.adjust_manual_time)
        button_layout.addWidget(self.adjust_time_button)
        layout.addLayout(button_layout)
        
        self.update_total_time()

    def toggle_tracking(self):
        if not self.is_tracking:
            self.start_tracking()
        else:
            self.stop_tracking()

    def start_tracking(self):
        self.is_tracking = True
        self.start_button.setText("Stop Session")
        self.session_start_time = datetime.now()
        self.timer.start(1000)  # Update every second

    def stop_tracking(self):
        self.is_tracking = False
        self.start_button.setText("Start Session")
        self.timer.stop()
        
        # Save session to database
        end_time = datetime.now()
        duration = int((end_time - self.session_start_time).total_seconds())
        
        self.cursor.execute('''
            INSERT INTO sessions (start_time, end_time, duration)
            VALUES (?, ?, ?)
        ''', (self.session_start_time, end_time, duration))
        self.conn.commit()
        
        self.current_session_time = 0
        self.update_timer()
        self.update_total_time()

    def update_timer(self):
        if self.is_tracking:
            self.current_session_time += 1
            hours = self.current_session_time // 3600
            minutes = (self.current_session_time % 3600) // 60
            seconds = self.current_session_time % 60
            self.time_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")

    def update_total_time(self):
        self.cursor.execute('SELECT SUM(duration) FROM sessions')
        total_seconds = self.cursor.fetchone()[0] or 0
        hours = total_seconds / 3600
        self.total_time_label.setText(f"Total Time: {hours:.2f} hours")

    def adjust_manual_time(self):
        dialog = TimeEntryDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            hours = dialog.hours_spin.value()
            minutes = dialog.minutes_spin.value()
            
            # Convert to seconds, negative if removing time
            seconds = (hours * 3600) + (minutes * 60)
            if dialog.remove_radio.isChecked():
                seconds = -seconds
                
            now = datetime.now()
            self.cursor.execute('''
                INSERT INTO sessions (start_time, end_time, duration)
                VALUES (?, ?, ?)
            ''', (now, now, seconds))
            self.conn.commit()
            self.update_total_time()


class TimeEntryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Adjust Time")
        self.setFont(QFont("JetBrains Mono", 10))
        
        layout = QVBoxLayout(self)
        
        # Radio buttons for add/remove
        radio_layout = QHBoxLayout()
        self.add_radio = QRadioButton("Add Time")
        self.remove_radio = QRadioButton("Remove Time")
        self.add_radio.setChecked(True)  # Default to add
        radio_layout.addWidget(self.add_radio)
        radio_layout.addWidget(self.remove_radio)
        
        # Group radio buttons
        self.button_group = QButtonGroup()
        self.button_group.addButton(self.add_radio)
        self.button_group.addButton(self.remove_radio)
        
        layout.addLayout(radio_layout)
        
        # Hours input
        hours_layout = QHBoxLayout()
        hours_label = QLabel("Hours:")
        self.hours_spin = QSpinBox()
        self.hours_spin.setRange(0, 999)
        hours_layout.addWidget(hours_label)
        hours_layout.addWidget(self.hours_spin)
        layout.addLayout(hours_layout)
        
        # Minutes input
        minutes_layout = QHBoxLayout()
        minutes_label = QLabel("Minutes:")
        self.minutes_spin = QSpinBox()
        self.minutes_spin.setRange(0, 999)
        minutes_layout.addWidget(minutes_label)
        minutes_layout.addWidget(self.minutes_spin)
        layout.addLayout(minutes_layout)
        
        # Add OK and Cancel buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)


def main():
    app = QApplication(sys.argv)
    window = HackingTracker()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
