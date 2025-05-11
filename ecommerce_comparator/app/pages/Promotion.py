import streamlit as st
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from app.utils import scrape_site
import pandas as pd

st.set_page_config(layout="wide")
st.header("🔥 Bons Plans & Réductions")

query = st.text_input("Filtrer par mot-clé", "")
discount_min = st.slider("Réduction minimale (%)", 0, 90, 30)
sites = st.multiselect("Sites à inclure", ["intersport", "decathlon"], default=["intersport", "decathlon"])

if st.button("Trouver les promos"):
    all_data = []
    for site in sites:
        with st.spinner(f"Scraping {site}..."):
            data = scrape_site(site, query)
            for item in data:
                item["source"] = site
            all_data.extend(data)

    # Conversion et filtrage
    df = pd.DataFrame(all_data)
    df["current_price"] = pd.to_numeric(df.get("current_price", pd.Series()), errors="coerce")
    df["original_price"] = pd.to_numeric(df.get("original_price", pd.Series()), errors="coerce")
    df["discount"] = pd.to_numeric(df.get("discount", pd.Series()), errors="coerce")
    df = df[df["discount"] >= discount_min]

    # Filtrage par mot-clé sur le nom du produit
    if query:
        df = df[df["name"].str.lower().str.contains(query.lower())]

    df = df.sort_values("discount", ascending=False)

    if not df.empty:
        st.success(f"{len(df)} bons plans trouvés !")
        for i, row in df.iterrows():
            with st.container():
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.image(row["image_url"], width=120)
                with col2:
                    st.markdown(f"### {row['name']}")
                    if pd.notnull(row["original_price"]) and row["original_price"] > row["current_price"]:
                        st.markdown(f"💰 **{row['current_price']} €**  ~~{row['original_price']} €~~")
                        st.markdown(f"🔥 **-{row['discount']}%**")
                    else:
                        st.markdown(f"💰 **{row['current_price']} €**")
                    st.markdown(f"🏬 *{row['source'].capitalize()}*")
                    with st.expander("🔍 Plus de détails"):
                        st.markdown("**Description :**")
                        st.markdown(row.get("description", "_Pas de description disponible._"))
                        st.markdown(f"[🔗 Voir le produit]({row['link']})")
    else:
        st.warning("Aucune promotion trouvée avec ces critères.")