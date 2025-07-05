# streamlit_app.py
import requests
import streamlit as st
import qrcode
from io import BytesIO
import socket

FIREBASE_URL = "https://libra-tacticl-suit-default-rtdb.asia-southeast1.firebasedatabase.app/RealtimeMonitoring.json"

def fetch_latest_health_data():
    try:
        response = requests.get(FIREBASE_URL)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and data:
                latest_key = sorted(data.keys())[-1]
                return data[latest_key]
    except:
        pass
    return None

def generate_qr_code(url):
    qr = qrcode.make(url)
    buf = BytesIO()
    qr.save(buf)
    return buf.getvalue()

def main():
    st.set_page_config(page_title="Real-Time Health Monitor", layout="wide")
    st.title("🌐 Real-Time Health Monitor")
    st.markdown("Scan the QR code to share this page on another device:")

    # Generate Local IP URL
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        share_url = f"http://{local_ip}:8501"
    except:
        share_url = "http://localhost:8501"

    st.image(generate_qr_code(share_url), width=200, caption=share_url)

    st.markdown("---")
    st.subheader("Live Vital Signs")
    data = fetch_latest_health_data()

    if data:
        col1, col2, col3 = st.columns(3)
        col1.metric("❤️ Heart Rate (BPM)", data.get("BPM", "--"))
        col2.metric("🩸 SpO₂ (%)", data.get("SpO2", "--"))
        col3.metric("🌡️ Temperature (°C)", data.get("Temp", "--"))
    else:
        st.error("Failed to fetch data from Firebase.")

    if st.button("⟳ Refresh"):
        st.experimental_rerun()

    st.markdown("---")
    st.info("This dashboard updates manually via refresh. Run it on your local server and share over LAN.")

if __name__ == "__main__":
    main()
