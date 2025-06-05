import streamlit as st
import pandas as pd

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

# SI ACCÈS INVITE OU ADMIN, AFFICHAGE PRINCIPAL
if profil == "invite" or profil == "admin":
    st.set_page_config(page_title="Annuaire d'entreprises - Filtrage NAF", layout="centered")
    st.title("📆 Annuaire d'entreprises par Code NAF et Département")

    st.markdown("""
    Entrez un **code NAF** (ex: `7112B`) et un **département** (ex: `07`) pour extraire un tableau d'entreprises.

    Les données proviennent d’un fichier CSV de test (sirene_light.csv). 🔽
    """)

    naf_input = st.text_input("Code(s) NAF (séparés par une virgule s'il y en a plusieurs)", "7112B")
    dep_input = st.text_input("Numéro de département (ex: 07)", "07")
    launch = st.button("Rechercher les entreprises")

    if launch:
        with st.spinner("🔄 Chargement des données..."):
            df = pd.read_csv("sirene_light.csv", dtype=str)

            naf_list = [n.strip() for n in naf_input.upper().split(",")]
            df_filtered = df[
                df["activitePrincipaleEtablissement"].isin(naf_list) &
                df["codePostalEtablissement"].str.startswith(dep_input)
            ]

            cols_to_keep = [
                "siren", "nic", "denominationUniteLegale", "codePostalEtablissement",
                "libelleCommuneEtablissement", "adresseEtablissement", "activitePrincipaleEtablissement"
            ]
            df_result = df_filtered[cols_to_keep].rename(columns={
                "denominationUniteLegale": "Entreprise",
                "codePostalEtablissement": "Code Postal",
                "libelleCommuneEtablissement": "Ville",
                "adresseEtablissement": "Adresse",
                "activitePrincipaleEtablissement": "Code NAF"
            })

            st.success(f"{len(df_result)} entreprises trouvées.")
            st.dataframe(df_result)

            csv = df_result.to_csv(index=False).encode('utf-8')
            st.download_button("📁 Télécharger le fichier CSV", csv, "entreprises_filtrees.csv", "text/csv")

    if profil == "admin":
        st.markdown("🔧 Espace Admin : à venir (ajout d’entreprises, gestion, etc.)")