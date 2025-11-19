import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from scrapers_drg import scrape_all
import time

st.set_page_config(page_title="Comparador Droguerías", layout="wide")

st.title("🔎 Comparador de precios — Farmatodo · Pasteur · Rebaja · Cruz Verde · Éxito")

# ----------------------------------------------------
# Opciones
# ----------------------------------------------------
with st.sidebar:
    st.header("Opciones")
    max_per_store = st.number_input("Máx. productos por tienda", 1, 20, 6)

    store_list = ["Farmatodo", "Pasteur", "Cruz Verde", "Rebaja", "Éxito"]
    selected_stores = st.multiselect("Tiendas a consultar", store_list, default=store_list)

    run_button = st.button("Buscar")

query = st.text_input("Producto a buscar", "dolex")

# ----------------------------------------------------
# Ejecutar scraping
# ----------------------------------------------------
if run_button and query.strip():
    st.info("Buscando productos…")
    start = time.time()

    data = scrape_all(query.strip(), max_per_store=max_per_store, selected_stores=selected_stores)

    elapsed = time.time() - start
    st.success(f"Búsqueda completada en {elapsed:.1f} s")

    # Convertir resultados a DataFrame
    rows
