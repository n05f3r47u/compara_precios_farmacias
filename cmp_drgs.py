# cmp_drgs.py

##
import os
import subprocess
import streamlit as st
##
# Instalar Playwright si no está listo (solo la primera vez)
#if not os.path.exists("/home/appuser/.cache/ms-playwright/chromium"):
#    with st.spinner("Instalando Playwright..."):
#        try:
#            subprocess.run(["playwright", "install", "chromium", "--with-deps"], check=True)
#            st.success("✅ Playwright instalado correctamente")
#        except Exception as e:
#            st.error(f"Error instalando Playwright: {e}")

##

import pandas as pd
from scrapers_drg import scrape_all
import time

import asyncio
import platform
if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


st.set_page_config(page_title="Comparador de precios - Droguerías (COL)", layout="wide")

st.title("🔎 Comparador de precios — Farmatodo · Pasteur · Rebaja · Cruz Verde · Exito")

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

with st.sidebar:
    st.header("Opciones")
    max_per_store = st.number_input("Máx. resultados por sitio", min_value=1, max_value=20, value=6)
    headless = st.checkbox("Ejecutar headless (sin navegador visible)", value=True)
    run_button = st.button("Buscar")

query = st.text_input("Producto a buscar (ej: dolex, trimebutina, desodorante)", value="dolex")

if run_button and query.strip():
    q = query.strip()
    st.info(f"Buscando: {q} — esto puede tardar unos segundos (cada sitio carga su página).")
    start = time.time()
    try:
        results = scrape_all(q, max_per_store=max_per_store, headless=headless)
    except Exception as e:
        st.error(f"Error en scraping: {e}")
        results = {}
    elapsed = time.time() - start
    st.success(f"Listo — tiempo: {elapsed:.1f}s")

    # Normalizar y mostrar tabla
    rows = []
    for store, items in results.items():
        for it in items:
            rows.append({
                "tienda": store,
                "titulo": it.get("title"),
                "precio_raw": it.get("price_raw"),
                "precio": it.get("price"),
                "link": it.get("link"),
                "img": it.get("img")
            })
    if not rows:
        st.warning("No se encontraron resultados. Revisa selectores o prueba otra búsqueda.")
    else:
        df = pd.DataFrame(rows)
        # Mostrar tabla interactiva
        st.subheader("Resultados")
        st.dataframe(df[['tienda','titulo','precio_raw','precio','link']].sort_values(by=['precio'], na_position='last'))

        # Resumen por tienda (mínimo)
        st.subheader("Mejor precio por tienda")
        best = df.dropna(subset=['precio']).groupby('tienda', as_index=False).apply(lambda g: g.nsmallest(1, 'precio')).reset_index(drop=True)
        st.table(best[['tienda','titulo','precio_raw','precio','link']])

        # Gráfico simple (precio por producto)
        st.subheader("Gráfico de precios (por item listado)")
        try:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(8,4))
            # ordenar y mostrar
            plot_df = df.dropna(subset=['precio']).sort_values('precio')
            ax.scatter(plot_df['precio'], plot_df['tienda'])
            ax.set_xlabel("Precio (COP)")
            ax.set_ylabel("Tienda")
            ax.set_title("Comparación de precios (items encontrados)")
            st.pyplot(fig)
        except Exception:
            st.write("Error al dibujar gráfico (falta matplotlib).")

        # Mostrar imágenes en tarjetas simples
        st.subheader("Previsualización (imágenes)")
        for idx, r in df.iterrows():
            cols = st.columns([1,4])
            with cols[0]:
                if r['img']:
                    st.image(r['img'], width=120)
                else:
                    st.write("sin imagen")
            with cols[1]:
                st.markdown(f"**{r['titulo']}**  \n**Tienda:** {r['tienda']}  \n**Precio:** {r['precio_raw']}  \n[Ver producto]({r['link']})")

        # Recomendaciones rápidas
        st.info("Consejo: si ves resultados vacíos en alguna tienda, abre el README para instrucciones sobre cómo ajustar los selectores.")
