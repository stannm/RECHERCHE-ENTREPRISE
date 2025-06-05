import streamlit as st
import pandas as pd
import io
import requests

st.set_page_config(page_title="Recherche d'entreprises", layout="centered")
st.title("🔎 Recherche d'entreprises par Code NAF et Département")

st.markdown("""
Entrez un **code NAF** (ex : `7112B`) et un **numéro de département** (ex : `75`) pour rechercher les entreprises correspondantes dans un fichier d'exemple.

🔽 Vous pourrez télécharger les résultats au format CSV.
""")

naf_input = st.text_input("Code(s) NAF (ex: 7112B)", "7112B")
dep_input = st.text_input("Département (ex: 75)", "75")
launch = st.button("Rechercher les entreprises")

if launch:
    with st.spinner("Chargement des données..."):
        url = "https://raw.githubusercontent.com/charlesdedampierre/datasets/main/sirene_sample.csv"
        response = requests.get(url)
        df = pd.read_csv(io.StringIO(response.content.decode('utf-8')), dtype=str)

        naf_list = [n.strip() for n in naf_input.upper().split(",")]
        df_filtered = df[
            df["activitePrincipaleEtablissement"].isin(naf_list) &
            df["codePostalEtablissement"].str.startswith(dep_input)
        ]

        if df_filtered.empty:
            st.warning("Aucune entreprise trouvée pour ces critères.")
        else:
            cols = [
                "siren", "nic", "denominationUniteLegale", "codePostalEtablissement",
                "libelleCommuneEtablissement", "adresseEtablissement", "activitePrincipaleEtablissement"
            ]
            df_result = df_filtered[cols].rename(columns={
                "denominationUniteLegale": "Entreprise",
                "codePostalEtablissement": "Code Postal",
                "libelleCommuneEtablissement": "Ville",
                "adresseEtablissement": "Adresse",
                "activitePrincipaleEtablissement": "Code NAF"
            })

            st.success(f"{len(df_result)} entreprises trouvées.")
            st.dataframe(df_result)

            csv = df_result.to_csv(index=False).encode('utf-8')
            st.download_button("📁 Télécharger les résultats CSV", csv, "entreprises_filtrees.csv", "text/csv")
