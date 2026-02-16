# app_streamlit.py
import os
import socket
import subprocess
import sys
import time
import contextlib

import streamlit as st
import streamlit.components.v1 as components

APP_PORT = int(os.getenv("GRADIO_PORT", "7860"))
APP_HOST = os.getenv("GRADIO_HOST", "127.0.0.1")
GRADIO_ENTRY = os.getenv("GRADIO_ENTRY", "app_gradio.py")

st.set_page_config(page_title="Gradio-in-Streamlit Demo", page_icon="🎛️", layout="centered")

def is_port_open(host: str, port: int, timeout: float = 0.25) -> bool:
    with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.settimeout(timeout)
        return sock.connect_ex((host, port)) == 0

@st.cache_resource(show_spinner=False)
def launch_gradio_server() -> dict:
    """
    Startet den Gradio-Server als Subprozess, falls der Port nicht belegt ist.
    Rückgabe enthält Prozess-Handle und URL.
    """
    url = f"http://{APP_HOST}:{APP_PORT}"
    if is_port_open(APP_HOST, APP_PORT):
        return {"proc": None, "url": url, "fresh": False}

    # Starte Gradio im Hintergrund
    cmd = [sys.executable, GRADIO_ENTRY]
    env = os.environ.copy()
    # Wir setzen Host/Port via ENV (wird in app_gradio.py genutzt, falls du es so implementieren willst)
    env["GRADIO_SERVER_PORT"] = str(APP_PORT)
    # Hinweis: unser Beispiel liest Port/Host direkt in app_gradio.py; alternativ könntest du hier Argumente übergeben.
    proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    # Warten, bis Port offen ist (max ~10s)
    for _ in range(100):
        if is_port_open(APP_HOST, APP_PORT):
            break
        time.sleep(0.1)

    return {"proc": proc, "url": url, "fresh": True}

def main():
    st.title("🎛️ Gradio in Streamlit – Stimmungs-Demo")
    st.caption("Variante A: Streamlit hostet einen lokalen Gradio-Server und bettet ihn per iframe ein.")

    server = launch_gradio_server()
    url = server["url"]

    # Health-Hinweis
    if not is_port_open(APP_HOST, APP_PORT):
        st.error("Gradio-Server konnte nicht gestartet/erreicht werden.")
        st.stop()

    st.success(f"Gradio läuft unter {url}")

    # Iframe einbetten
    iframe_html = f"""
        <div style="border:1px solid #ddd;border-radius:8px;overflow:hidden">
          <iframe src="{url}" width="100%" height="720" frameborder="0"></iframe>
        </div>
    """
    components.html(iframe_html, height=740, scrolling=True)

    with st.expander("⚙️ Debug/Log"):
        st.write("Port:", APP_PORT)
        st.write("Host:", APP_HOST)
        st.write("Neu gestartet:", server["fresh"])
        st.info("Falls nichts lädt: Port-Konflikt prüfen oder lokale Netz-/Iframe-Policies beachten.")

if __name__ == "__main__":
    main()
