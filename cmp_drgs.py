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

    # Convertir a DataFrame
    rows = []
    for store, items in data.items():
        for it in items:
            rows.append({
                "tienda": store,
                "titulo": it["title"],
                "precio_raw": it["price_raw"],
                "precio": it["price"],
                "link": it["link"],
                "img": it["img"]
            })

    if not rows:
        st.warning("No se encontraron productos.")
        st.stop()

    df = pd.DataFrame(rows)

    # Mostrar tabla
    st.subheader("Resultados")
    st.dataframe(df.sort_values("precio", na_position="last"))

    # ----------------------------------------------------
    # Mejor precio por tienda
    # ----------------------------------------------------
    st.subheader("Mejor precio por tienda")
    best = df.dropna(subset=["precio"]).groupby("tienda", as_index=False).apply(
        lambda g: g.nsmallest(1, "precio")
    ).reset_index(drop=True)
    st.table(best)

    # ----------------------------------------------------
    # Gráfico solo si hay datos
    # ----------------------------------------------------
    if df["precio"].notna().any() and st.checkbox("Mostrar gráfico de comparación"):
        plot_df = df.dropna(subset=["precio"]).sort_values("precio")
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.barh(plot_df["tienda"], plot_df["precio"])
        ax.set_xlabel("Precio (COP)")
        ax.set_title("Comparación de precios")
        st.pyplot(fig)

    # ----------------------------------------------------
    # Tarjetas visuales
    # ----------------------------------------------------
    st.subheader("Previsualización")
    for _, r in df.iterrows():
        cols = st.columns([1, 4])
        with cols[0]:
            st.image(r["img"] or "", width=120)
        with cols[1]:
            st.markdown(f"""
            **{r['titulo']}**  
            **Tienda:** {r['tienda']}  
            **Precio:** {r['precio_raw']}  
            [Ver producto]({r['link']})
            """)
