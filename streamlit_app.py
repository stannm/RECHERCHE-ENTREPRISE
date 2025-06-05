import streamlit as st
import pandas as pd
import datetime
import folium
from streamlit_folium import st_folium
import hashlib

st.set_page_config(page_title="Annuaire Ultra Complet", layout="wide")

# ---- CONFIG ----
PASSWORDS = {"invite": "sadelainvite2025", "admin": "admin220cv"}
EXPORT_CODE = "export2024"

# ---- AUTHENTIFICATION ----
st.sidebar.title("🔐 Connexion")
password = st.sidebar.text_input("Mot de passe", type="password")

if password in PASSWORDS.values():
    profil = [k for k, v in PASSWORDS.items() if v == password][0]
    st.sidebar.success(f"Connecté en tant que : {profil.upper()}")
else:
    st.sidebar.error("⛔ Mot de passe incorrect")
    st.stop()

# ---- DONNÉES ----
try:
    df = pd.read_csv("sirene_light.csv", dtype=str)
except:
    st.error("Fichier sirene_light.csv non trouvé.")
    st.stop()

# ---- PAGE PRINCIPALE ----
st.title("🏢 Annuaire d'entreprises complet")

# Recherche multi-critères
col1, col2, col3 = st.columns(3)
with col1:
    naf_input = st.text_input("🔍 Code(s) NAF", "7112B")
with col2:
    dep_input = st.text_input("📍 Département (ex: 07)", "07")
with col3:
    nom_input = st.text_input("🏷️ Nom d’entreprise contient", "")

if st.button("🔎 Rechercher"):
    naf_list = [n.strip() for n in naf_input.upper().split(",")]
    df_filtered = df[
        df["activitePrincipaleEtablissement"].isin(naf_list) &
        df["codePostalEtablissement"].str.startswith(dep_input)
    ]
    if nom_input:
        df_filtered = df_filtered[df_filtered["denominationUniteLegale"].str.contains(nom_input, case=False, na=False)]
    st.session_state["resultats"] = df_filtered

if "resultats" in st.session_state:
    df_filtered = st.session_state["resultats"]
    st.write(f"🎯 {len(df_filtered)} entreprise(s) trouvée(s)")
    st.dataframe(df_filtered)

    # Carte si coordonnées présentes
    if "latitude" in df_filtered.columns and "longitude" in df_filtered.columns:
        m = folium.Map(location=[45, 4.8], zoom_start=8)
        for _, row in df_filtered.iterrows():
            folium.Marker([float(row["latitude"]), float(row["longitude"])],
                          popup=row["denominationUniteLegale"]).add_to(m)
        st_folium(m, width=700)

    # ---- COMMENTAIRE UTILISATEUR ----
    if profil == "invite":
        st.markdown("## ✍️ Laisser un commentaire")
        if not df_filtered.empty:
            selected_index = st.number_input("N° ligne", min_value=0, max_value=len(df_filtered)-1)
            pseudo = st.text_input("Ton prénom ou pseudo")
            note = st.slider("Note (1 à 5 ⭐)", 1, 5, 4)
            commentaire = st.text_area("Ton commentaire")

            if st.button("Envoyer le commentaire"):
                row = df_filtered.iloc[selected_index]
                new = pd.DataFrame([{
                    "siren": row["siren"],
                    "nic": row["nic"],
                    "nom_entreprise": row["denominationUniteLegale"],
                    "auteur": pseudo,
                    "note": note,
                    "commentaire": commentaire,
                    "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }])
                try:
                    com_df = pd.read_csv("commentaires.csv")
                    com_df = pd.concat([com_df, new], ignore_index=True)
                except:
                    com_df = new
                com_df.to_csv("commentaires.csv", index=False)
                st.success("Commentaire enregistré ✅")

    # ---- COMMENTAIRES LIES AUX ENTREPRISES ----
    try:
        com_df = pd.read_csv("commentaires.csv")
        st.markdown("## 💬 Commentaires associés")
        for _, row in df_filtered.iterrows():
            sous_df = com_df[com_df["siren"] == row["siren"]]
            if not sous_df.empty:
                st.markdown(f"### 🏷️ {row['denominationUniteLegale']} ({row['siren']})")
                for _, c in sous_df.iterrows():
                    st.markdown(f"- ⭐ {c['note']} - {c['auteur']} ({c['date']}): {c['commentaire']}")
    except:
        pass

# ---- ZONE ADMIN ----
if profil == "admin":
    st.markdown("## 🛠️ Zone Admin")
    try:
        com_df = pd.read_csv("commentaires.csv")
        st.dataframe(com_df)

        com_to_delete = st.selectbox("Supprimer un commentaire :", com_df["commentaire"].unique())
        if st.button("Supprimer le commentaire"):
            com_df = com_df[com_df["commentaire"] != com_to_delete]
            com_df.to_csv("commentaires.csv", index=False)
            st.success("Commentaire supprimé")

        with st.expander("🔐 Télécharger les commentaires (protégé)"):
            export_code = st.text_input("Code d'autorisation :", type="password")
            if export_code == EXPORT_CODE:
                st.download_button("📥 Télécharger les commentaires", com_df.to_csv(index=False), "commentaires_export.csv")
            else:
                st.info("Entrez le bon code pour débloquer le téléchargement.")
    except:
        st.info("Aucun commentaire disponible.")
