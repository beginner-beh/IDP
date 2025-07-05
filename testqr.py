# streamlit_app.py
import requests
import streamlit as st
import qrcode
from io import BytesIO
import socket
import time

FIREBASE_URL = "https://libra-tacticl-suit-default-rtdb.asia-southeast1.firebasedatabase.app/RealtimeMonitoring.json"

def fetch_latest_health_data():
    try:
        response = requests.get(FIREBASE_URL)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and data:
                latest_key = sorted(data.keys())[-1]
                return data[latest_key]
    except Exception as e:
        print("Fetch error:", e)
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
        share_url = f"https://z8vjom2c2uvgdul7bbbebz.streamlit.app/"
    except:
        share_url = "https://z8vjom2c2uvgdul7bbbebz.streamlit.app/"

    st.image(generate_qr_code(share_url), width=200, caption=share_url)

    st.markdown("---")
    st.subheader("Live Vital Signs (Auto-refresh every 2s)")

    placeholder = st.empty()  # placeholder for live metrics

    while True:
        with placeholder.container():
            data = fetch_latest_health_data()
            if data:
                col1, col2, col3 = st.columns(3)
                col1.metric("❤️ Heart Rate (BPM)", data.get("BPM", "--"))
                col2.metric("🩸 SpO₂ (%)", data.get("SpO2", "--"))
                col3.metric("🌡️ Temperature (°C)", data.get("Temp", "--"))
            else:
                st.error("Failed to fetch data from Firebase.")

            st.markdown("---")
            st.info("This dashboard updates automatically every 2 seconds. Run it on your local server and share over LAN.")

        time.sleep(2)
        st.experimental_rerun()

if __name__ == "__main__":
    main()
