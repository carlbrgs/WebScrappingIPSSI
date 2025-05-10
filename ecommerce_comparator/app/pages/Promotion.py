import streamlit as st
from app.utils import scrape_site
import pandas as pd

st.header("🔥 Bons Plans & Réductions")

query = st.text_input("Filtrer par mot-clé", "")
discount_min = st.slider("Réduction minimale (%)", 0, 90, 30)

if st.button("Trouver les promos"):
    all_data = []
    for source in ["intersport", "decathlon"]:
        with st.spinner(f"Scraping {source}..."):
            data = scrape_site(source, query)
            all_data.extend(data)

    df = pd.DataFrame(all_data)
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["discount"] = pd.to_numeric(df["discount"], errors="coerce")

    df = df[df["discount"] >= discount_min]
    df = df.sort_values("discount", ascending=False)

    st.success(f"{len(df)} bons plans trouvés !")

    for _, row in df.iterrows():
        st.markdown(f"### {row['name']}")
        st.image(row["image_url"], width=150)
        st.markdown(f"💸 {row['price']} € | 🔥 -{row['discount']}% | 🏪 {row['source']}")
        st.markdown(f"[Voir sur le site]({row['link']})")
        st.markdown("---")
