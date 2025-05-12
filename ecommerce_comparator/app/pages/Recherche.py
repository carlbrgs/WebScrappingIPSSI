import streamlit as st
import pandas as pd
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from app.utils import scrape_site

st.set_page_config(layout="wide")
st.header("🔍 Recherche de produits")

query = st.text_input("Produit à rechercher", "")
sites = st.multiselect("Sites à inclure", ["intersport", "decathlon"], default=["intersport", "decathlon"])

if st.button("Rechercher"):
    all_data = []
    for site in sites:
        with st.spinner(f"Scraping {site}..."):
            data = scrape_site(site, query)
            for item in data:
                item["source"] = site
            all_data.extend(data)

    # 🔍 Filtrage local par mot-clé (au moins un mot doit apparaître dans le nom du produit)
    keywords = query.lower().split()
    filtered_data = [
        item for item in all_data
        if any(word in item["name"].lower() for word in keywords)
    ]

    if filtered_data:
        df = pd.DataFrame(filtered_data)
        df["current_price"] = pd.to_numeric(df["current_price"], errors="coerce")
        df = df.sort_values("current_price")

        st.success(f"{len(df)} produit(s) trouvés pour « {query} ».")

        for i, row in df.iterrows():
            with st.container():
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.image(row["image_url"], width=120)
                with col2:
                    st.markdown(f"### {row['name']}")

                    if row["original_price"] and float(row["original_price"]) > float(row["current_price"]):
                        st.markdown(f"💰 **{row['current_price']} €**  ~~{row['original_price']} €~~")
                        st.markdown(f"🎯 **-{row['discount']}%**")
                    else:
                        st.markdown(f"💰 **{row['current_price']} €**")

                    st.markdown(f"🏬 *{row['source'].capitalize()}*")

                    with st.expander("🔍 Plus de détails"):
                        st.markdown("**Description :**")
                        st.markdown(row.get("description", "_Pas de description disponible._"))
                        st.markdown(f"[🔗 Voir le produit]({row['link']})")
    else:
        st.warning(f"Aucun produit trouvé contenant « {query} ».")
