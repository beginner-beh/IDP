import sys
import requests
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import (
    QApplication, QLabel, QWidget, QVBoxLayout,
    QHBoxLayout, QFrame, QMainWindow, QPushButton, QMessageBox,
    QScrollArea
)
from PyQt5.QtGui import QFont, QColor, QPalette

# Firebase Realtime Database URL
FIREBASE_URL = "https://libra-tacticl-suit-default-rtdb.asia-southeast1.firebasedatabase.app/RealtimeMonitoring.json"

def fetch_health_data():
    try:
        response = requests.get(FIREBASE_URL)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and data:
                latest_key = sorted(data.keys())[-1]
                return data[latest_key]
        return None
    except Exception as e:
        print("Error fetching health data:", e)
        return None

def fetch_historical_data():
    try:
        response = requests.get(FIREBASE_URL)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict):
                return list(data.values())
        return []
    except Exception as e:
        print("Error fetching historical data:", e)
        return []

class VitalCard(QFrame):
    def __init__(self, title, color):
        super().__init__()
        self.setFrameShape(QFrame.StyledPanel)
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)

        self.title_label = QLabel(title)
        self.title_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)

        self.value_label = QLabel("--")
        self.value_label.setFont(QFont("Arial", 32, QFont.Bold))
        self.value_label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        self.setLayout(layout)

    def update_value(self, value):
        self.value_label.setText(str(value))

class HealthMonitorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Real-Time Health Monitor")
        self.setGeometry(200, 200, 600, 300)
        self.setup_ui()
        self.setup_timer()

    def setup_ui(self):
        self.bpm_card = VitalCard("Heart Rate (BPM)", "#C8E6C9")
        self.spo2_card = VitalCard("SpO₂ (%)", "#BBDEFB")
        self.temp_card = VitalCard("Temperature (°C)", "#FFF9C4")

        self.refresh_button = QPushButton("Refresh Now")
        self.refresh_button.clicked.connect(self.manual_refresh)
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #43A047;
                color: white;
                font-weight: bold;
                border-radius: 10px;
                padding: 10px 20px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
        """)

        self.history_button = QPushButton("Show History")
        self.history_button.clicked.connect(self.show_history)
        self.history_button.setStyleSheet("""
            QPushButton {
                background-color: #1976D2;
                color: white;
                font-weight: bold;
                border-radius: 10px;
                padding: 10px 20px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #1565C0;
            }
        """)

        left_layout = QVBoxLayout()
        left_layout.addWidget(self.spo2_card, stretch=2)
        left_layout.addWidget(self.temp_card, stretch=2)
        left_layout.addWidget(self.refresh_button, alignment=Qt.AlignCenter)
        left_layout.addWidget(self.history_button, alignment=Qt.AlignCenter)
        left_layout.addStretch(1)

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.bpm_card)
        right_layout.setStretch(0, 1)

        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(right_layout, 1)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def setup_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_health_data)
        self.timer.start(2000)  # update every 2 seconds

    def update_health_data(self):
        data = fetch_health_data()
        if data:
            self.bpm_card.update_value(data.get("BPM", "--"))
            self.spo2_card.update_value(data.get("SpO2", "--"))
            self.temp_card.update_value(data.get("Temp", "--"))
        else:
            self.show_error("Failed to fetch data from Firebase.")

    def manual_refresh(self):
        self.update_health_data()

    def show_history(self):
        self.history_window = HistoryWindow(self)
        self.history_window.show()

    def show_error(self, message):
        QMessageBox.warning(self, "Error", message)

class HistoryWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Historical Health Data")
        self.setGeometry(250, 250, 400, 500)

        layout = QVBoxLayout()
        self.scroll_area = QScrollArea()
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout()
        self.scroll_widget.setLayout(self.scroll_layout)
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)
        layout.addWidget(self.scroll_area)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        self.setLayout(layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.load_history)
        self.timer.start(5000)  # refresh every 5 seconds

        self.load_history()  # initial load

    def load_history(self):
        # Clear previous entries
        while self.scroll_layout.count():
            child = self.scroll_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        history = fetch_historical_data()
        if not history:
            self.scroll_layout.addWidget(QLabel("No historical data available."))
        else:
            for record in reversed(history[-20:]):  # show the last 20 records
                bpm = record.get("BPM", "--")
                spo2 = record.get("SpO2", "--")
                temp = record.get("Temp", "--")
                label = QLabel(f"BPM: {bpm}, SpO₂: {spo2}, Temp: {temp}°C")
                self.scroll_layout.addWidget(label)

    def closeEvent(self, event):
        self.timer.stop()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = HealthMonitorApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
