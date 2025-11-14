import os
import tarfile
import urllib.request
import streamlit as st

CHROMIUM_URL = "https://github.com/macchrome/linchrome/releases/download/v142.7444.166-M142.0.7444.166-r1522585-portable-ungoogled-Lin64/ungoogled-chromium_142.0.7444.166_1.vaapi_linux.tar.xz"

CHROMIUM_DIR = "/tmp/chromium"
CHROMIUM_BIN = os.path.join(CHROMIUM_DIR, "chrome")

@st.cache_resource
def get_chromium():
    if os.path.exists(CHROMIUM_BIN):
        return CHROMIUM_BIN

    os.makedirs(CHROMIUM_DIR, exist_ok=True)
    archive_path = "/tmp/chromium.tar.xz"

    st.write("Descargando Chromium…")
    urllib.request.urlretrieve(CHROMIUM_URL, archive_path)

    st.write("Descomprimiendo…")
    with tarfile.open(archive_path) as tar:
        tar.extractall(path=CHROMIUM_DIR)

    # Asegurar permisos de ejecución
    os.chmod(CHROMIUM_BIN, 0o755)

    return CHROMIUM_BIN
