import streamlit as st
import requests
import qrcode
from io import BytesIO

FIREBASE_URL = "https://libra-tacticl-suit-default-rtdb.asia-southeast1.firebasedatabase.app/RealtimeMonitoring.json"

def fetch_health_data():
    try:
        response = requests.get(FIREBASE_URL)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception:
        return None

def show_qr_code(url):
    qr = qrcode.make(url)
    buf = BytesIO()
    qr.save(buf)
    st.image(buf.getvalue(), caption="Scan to open this dashboard", width=200)

def show_metrics(data):
    col1, col2, col3 = st.columns(3)
    col1.metric("❤️ Heart Rate (BPM)", data.get("BPM", "--"))
    col2.metric("🩸 SpO₂ (%)", data.get("SpO2", "--"))
    col3.metric("🌡️ Temperature (°C)", data.get("Temp", "--"))

def main():
    st.set_page_config(page_title="Real-Time Health Monitor", layout="wide")
    st.title("Real-Time Health Monitor")
    st.markdown("Share this dashboard by scanning the QR code below!")

    # Use your local URL for testing, update to your public URL after deployment
    url = "http://10.12.134.233:8501"
    show_qr_code(url)

    data = fetch_health_data()
    if data:
        show_metrics(data)
    else:
        st.error("Failed to fetch data from Firebase.")

    if st.button("🔄 Refresh Now"):
        st.experimental_rerun()

if __name__ == "__main__":
    main()