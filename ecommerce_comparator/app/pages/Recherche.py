import streamlit as st
import pandas as pd
from app.utils import scrape_site

st.set_page_config(layout="wide")
st.header("🔍 Recherche de produits")

query = st.text_input("Produit à rechercher", "chaussures running")
sites = st.multiselect("Sites à inclure", ["intersport", "decathlon"], default=["intersport", "decathlon"])

if st.button("Rechercher"):
    all_data = []
    for site in sites:
        with st.spinner(f"Scraping {site}..."):
            data = scrape_site(site, query)
            for item in data:
                item["source"] = site
            all_data.extend(data)

    if all_data:
        df = pd.DataFrame(all_data)
        df["price"] = pd.to_numeric(df["price"], errors="coerce")
        df = df.sort_values("price")

        st.success(f"{len(df)} produit(s) trouvés.")

        for i, row in df.iterrows():
            with st.container():
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.image(row["image_url"], width=120)
                with col2:
                    st.markdown(f"### {row['name']}")
                    st.markdown(f"💰 **{row['price']} €**")
                    st.markdown(f"🏬 *{row['source'].capitalize()}*")

                    with st.expander("🔍 Plus de détails"):
                        st.markdown("**Description :**")
                        st.markdown(row.get("description", "_Pas de description disponible._"))
                        st.markdown(f"[🔗 Voir le produit]({row['link']})")
    else:
        st.warning("Aucun produit trouvé.")
