import streamlit as st

# AUTHENTIFICATION SIMPLE
st.title("🔐 Connexion")

code = st.text_input("Entre le mot de passe :", type="password")

if code == "invite":
    st.success("🔍 Accès invité : recherche activée")
    profil = "invite"

elif code == "admin123":
    st.success("👑 Accès admin activé")
    profil = "admin"

else:
    st.warning("🔒 Code incorrect ou vide")
    st.stop()

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
        df = pd.read_csv("sirene_light.csv", dtype=str)


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
