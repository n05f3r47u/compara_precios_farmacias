import streamlit as st
import pandas as pd
import nest_asyncio
import asyncio

from scrapers_drg import scrape_all

nest_asyncio.apply()

st.set_page_config(page_title="Comparador Droguerías", layout="wide")
st.title("🔎 Comparador de Precios — Droguerías en Colombia")

query = st.text_input("Producto a buscar", "dolex")
max_results = st.number_input("Máx. resultados por tienda", 1, 20, 6)

if st.button("Buscar"):
    st.info("Buscando en 5 tiendas simultáneamente...")

    loop = asyncio.get_event_loop()
    try:
        data = loop.run_until_complete(scrape_all(query, max_results))
    except Exception as e:
        st.error(f"Error: {e}")
        st.stop()

    rows = []
    for store, items in data.items():
        for it in items:
            rows.append({
                "tienda": store,
                "titulo": it.get("title"),
                "precio_raw": it.get("price_raw"),
                "precio": it.get("price"),
                "link": it.get("link"),
                "img": it.get("img")
            })

    df = pd.DataFrame(rows)

    st.subheader("Resultados")
    st.dataframe(df)

    st.subheader("Mejor precio por tienda")
    if "precio" in df.columns:
        best = (
            df.dropna(subset=["precio"])
              .groupby("tienda")
              .apply(lambda g: g.nsmallest(1, "precio"))
              .reset_index(drop=True)
        )
        st.table(best)

    st.subheader("Imágenes")
    for _, r in df.iterrows():
        cols = st.columns([1, 4])
        with cols[0]:
            if r["img"]:
                st.image(r["img"], width=120)
        with cols[1]:
            st.write(f"**{r['titulo']}** — {r['tienda']} — {r['precio_raw']}")
            if r["link"]:
                st.write(f"[Ver producto]({r['link']})")
