import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="Annuaire sécurisé avec commentaires", layout="centered")

# Sécurité
st.title("🔐 Connexion")
code = st.text_input("Entre le mot de passe :", type="password")

if code == "invite":
    st.success("🔍 Accès invité activé")
    profil = "invite"
elif code == "admin123":
    st.success("👑 Accès admin activé")
    profil = "admin"
else:
    st.warning("🔒 Mot de passe incorrect ou vide")
    st.stop()

# Chargement des données entreprises
df = pd.read_csv("sirene_light.csv", dtype=str)

if "df_filtered" not in st.session_state:
    st.session_state.df_filtered = None

st.title("📁 Recherche d'entreprises par Code NAF et Département")

naf_input = st.text_input("Code(s) NAF (ex: 7112B)", "7112B")
dep_input = st.text_input("Département (ex: 07)", "07")
launch = st.button("Rechercher")

if launch:
    naf_list = [n.strip() for n in naf_input.upper().split(",")]
    st.session_state.df_filtered = df[
        df["activitePrincipaleEtablissement"].isin(naf_list) &
        df["codePostalEtablissement"].str.startswith(dep_input)
    ]

df_filtered = st.session_state.df_filtered

if df_filtered is not None:
    if df_filtered.empty:
        st.warning("Aucune entreprise trouvée.")
    else:
        st.success(f"{len(df_filtered)} entreprises trouvées.")
        st.dataframe(df_filtered)

        # Laisser un commentaire
        if profil == "invite":
            st.markdown("## ✍️ Laisser un commentaire")
            selected_index = st.number_input("Numéro de ligne de l'entreprise concernée", min_value=0, max_value=len(df_filtered)-1, step=1)
            nom_utilisateur = st.text_input("Ton prénom ou pseudo")
            commentaire = st.text_area("Ton commentaire")
            if st.button("Envoyer le commentaire"):
                entreprise = df_filtered.iloc[selected_index]
                new_comment = pd.DataFrame([{
                    "siren": entreprise["siren"],
                    "nic": entreprise["nic"],
                    "nom_entreprise": entreprise["denominationUniteLegale"],
                    "auteur": nom_utilisateur,
                    "commentaire": commentaire,
                    "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }])
                try:
                    comments_df = pd.read_csv("commentaires.csv")
                    comments_df = pd.concat([comments_df, new_comment], ignore_index=True)
                except FileNotFoundError:
                    comments_df = new_comment
                comments_df.to_csv("commentaires.csv", index=False)
                st.success("Commentaire enregistré ✅")

        # Affichage commentaires liés à l'entreprise sélectionnée
        try:
            comments_df = pd.read_csv("commentaires.csv")
            st.markdown("### 💬 Commentaires liés aux entreprises affichées")
            for i, row in df_filtered.iterrows():
                enterprise_comments = comments_df[comments_df["siren"] == row["siren"]]
                if not enterprise_comments.empty:
                    st.markdown(f"**🧾 {row['denominationUniteLegale']} ({row['siren']})**")
                    for _, c in enterprise_comments.iterrows():
                        st.markdown(f"- {c['auteur']} ({c['date']}): {c['commentaire']}")
        except FileNotFoundError:
            pass

        # ADMIN - Gérer les commentaires
        if profil == "admin":
            st.markdown("## 🛠️ Modération des commentaires")
            try:
                comments_df = pd.read_csv("commentaires.csv")
                comment_to_delete = st.selectbox("Choisis un commentaire à supprimer :", comments_df["commentaire"])
                if st.button("Supprimer ce commentaire"):
                    comments_df = comments_df[comments_df["commentaire"] != comment_to_delete]
                    comments_df.to_csv("commentaires.csv", index=False)
                    st.success("Commentaire supprimé ✅")
            except FileNotFoundError:
                st.info("Aucun commentaire pour le moment.")
