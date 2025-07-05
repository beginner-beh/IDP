import streamlit as st
import requests

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

def main():
    st.title("Real-Time Health Monitor")
    st.markdown("Scan the QR code below to share this dashboard!")

    # Show QR code for this page
    import qrcode
    import streamlit as st
    from io import BytesIO
    import base64

    url = st.experimental_get_query_params().get("url", [st.request.url])[0]
    qr = qrcode.make(url)
    buf = BytesIO()
    qr.save(buf)
    st.image(buf.getvalue(), caption="Scan to open this dashboard", width=200)

    # Fetch and display health data
    data = fetch_health_data()
    if data:
        st.metric("Heart Rate (BPM)", data.get("BPM", "--"))
        st.metric("SpO₂ (%)", data.get("SpO2", "--"))
        st.metric("Temperature (°C)", data.get("Temp", "--"))
    else:
        st.error("Failed to fetch data from Firebase.")

    if st.button("Refresh Now"):
        st.experimental_rerun()

if __name__ == "__main__":
    main()