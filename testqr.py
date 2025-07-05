import sys
import os
import socket
import requests
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import (
    QApplication, QLabel, QWidget, QVBoxLayout,
    QHBoxLayout, QFrame, QMainWindow, QPushButton, QMessageBox,
    QScrollArea
)
from PyQt5.QtGui import QFont, QColor, QPalette
# Streamlit and QR Code
import streamlit as st
import qrcode
from io import BytesIO

FIREBASE_URL = "https://libra-tacticl-suit-default-rtdb.asia-southeast1.firebasedatabase.app/RealtimeMonitoring.json"

# === Firebase Fetch Functions ===
def fetch_health_data():
    try:
        response = requests.get(FIREBASE_URL)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and data:
                latest_key = sorted(data.keys())[-1]
                return data[latest_key]
        return None
    except:
        return None

def fetch_historical_data():
    try:
        response = requests.get(FIREBASE_URL)
        if response.status_code == 200:
            data = response.json()
            return list(data.values()) if isinstance(data, dict) else []
    except:
        pass
    return []

# === PyQt5 Components ===
class VitalCard(QFrame):
    def __init__(self, title, color):
        super().__init__()
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
        self.setGeometry(100, 100, 600, 300)
        self.setup_ui()
        self.setup_timer()

    def setup_ui(self):
        self.bpm_card = VitalCard("Heart Rate (BPM)", "#C8E6C9")
        self.spo2_card = VitalCard("SpO₂ (%)", "#BBDEFB")
        self.temp_card = VitalCard("Temperature (°C)", "#FFF9C4")

        self.refresh_button = QPushButton("Refresh Now")
        self.refresh_button.clicked.connect(self.manual_refresh)

        self.history_button = QPushButton("Show History")
        self.history_button.clicked.connect(self.show_history)

        left_layout = QVBoxLayout()
        left_layout.addWidget(self.spo2_card)
        left_layout.addWidget(self.temp_card)
        left_layout.addWidget(self.refresh_button)
        left_layout.addWidget(self.history_button)
        left_layout.addStretch()

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
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_health_data)
        self.timer.start(3000)

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
        self.setGeometry(150, 150, 500, 400)

        self.scroll_area = QScrollArea()
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout()
        self.scroll_widget.setLayout(self.scroll_layout)
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)

        layout = QVBoxLayout()
        layout.addWidget(self.scroll_area)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.close)
        layout.addWidget(cancel_btn, alignment=Qt.AlignRight)
        self.setLayout(layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_history)
        self.timer.start(3000)

        self.refresh_history()

    def refresh_history(self):
        while self.scroll_layout.count():
            child = self.scroll_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        history = fetch_historical_data()
        for record in history:
            label = QLabel(f"BPM: {record.get('BPM', '--')}, SpO₂: {record.get('SpO2', '--')}, Temp: {record.get('Temp', '--')} °C")
            self.scroll_layout.addWidget(label)

    def closeEvent(self, event):
        self.timer.stop()
        event.accept()

# === Streamlit Dashboard ===
def streamlit_main():
    st.set_page_config(page_title="Health Monitor", layout="wide")
    st.title("Real-Time Health Monitor")
    st.markdown("Scan to view this page on mobile:")

    local_ip = socket.gethostbyname(socket.gethostname())
    url = f"http://{local_ip}:8501"
    qr = qrcode.make(url)
    buf = BytesIO()
    qr.save(buf)
    st.image(buf.getvalue(), width=200)

    data = fetch_health_data()
    if data:
        col1, col2, col3 = st.columns(3)
        col1.metric("💍 BPM", data.get("BPM", "--"))
        col2.metric("🩸 SpO₂", data.get("SpO2", "--"))
        col3.metric("🌡️ Temp", data.get("Temp", "--"))
    else:
        st.error("Failed to fetch data from Firebase.")

    if st.button("Refresh"):
        st.experimental_rerun()

# === Main Entry Point ===
if os.getenv("STREAMLIT_RUN") == "1" or "streamlit" in sys.modules:
    streamlit_main()
else:
    if __name__ == '__main__':
        app = QApplication(sys.argv)
        window = HealthMonitorApp()
        window.show()
        sys.exit(app.exec_())
