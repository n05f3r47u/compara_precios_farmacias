import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from scrapers_drg import scrape_all

st.set_page_config(layout="wide")
st.title("🔎 Comparador de Precios — Droguerías Colombia")

query = st.text_input("Producto a buscar", "dolex")
max_results = st.number_input("Máx. resultados por tienda", 1, 20, 6)

if st.button("Buscar"):
    st.info("Buscando productos...")

    data = scrape_all(query, max_results)

    rows = []
    for store, items in data.items():
        for it in items:
            rows.append({
                "seleccionar": False,
                "tienda": store,
                "titulo": it.get("title"),
                "precio_raw": it.get("price_raw"),
                "precio": it.get("price"),
                "link": it.get("link"),
                "img": it.get("img")
            })

    df = pd.DataFrame(rows)

    # Asegurar que la columna 'seleccionar' exista SIEMPRE
    if "seleccionar" not in df.columns:
        df["seleccionar"] = False

    st.subheader("Resultados (selecciona productos)")
    edited_df = st.data_editor(
        df,
        use_container_width=True,
        hide_index=True
    )

    # Filtrar seleccionados de forma segura
    selected = edited_df[edited_df.get("seleccionar", False) == True]

    if len(selected) > 0:
        st.subheader("📊 Comparación de precios — seleccionados")

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.scatter(selected["precio"], selected["tienda"])
        ax.set_xlabel("Precio (COP)")
        ax.set_ylabel("Tienda")
        ax.set_title("Comparación de precios")

        st.pyplot(fig)
    else:
        st.info("No se seleccionó ningún producto para graficar.")
