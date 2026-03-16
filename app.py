import streamlit as st
from datetime import datetime
from generator import generer_visuel_commune, charger_donnees

# Configuration de la page
st.set_page_config(page_title="Togo Atlas Pro", layout="wide")

# Sécurité : Clé du jour (Ex: JCDC + Jour)
cle_du_jour = f"JCDC{datetime.now().day}"

st.title("🇹🇬 Atlas des cartes du Togo Pro")
st.write("Plateforme Officielle - Direction Sylvestre BOCCO")

# Barre latérale de sécurité
st.sidebar.header("🔐 Sécurité")
access_key = st.sidebar.text_input("Clé d'accès quotidienne", type="password")

if access_key != cle_du_jour:
    st.sidebar.warning("Veuillez entrer la clé valide pour débloquer l'accès.")
else:
    st.sidebar.success("✅ Accès autorisé")
    
    # Chargement des données Shapefile
    gdf_comm, _, _, _, _ = charger_donnees()

    # Détection des noms de colonnes
    c_reg = 'ADM1_FR' if 'ADM1_FR' in gdf_comm.columns else 'Adm1_fr'
    c_pref = 'ADM2_FR' if 'ADM2_FR' in gdf_comm.columns else 'Adm2_fr'
    c_com = 'Communes' if 'Communes' in gdf_comm.columns else 'Commune'

    st.sidebar.header("📍 Localisation")
    reg = st.sidebar.selectbox("Choisir la Région", sorted(gdf_comm[c_reg].unique()))
    pref = st.sidebar.selectbox("Choisir la Préfecture", sorted(gdf_comm[gdf_comm[c_reg] == reg][c_pref].unique()))
    com = st.sidebar.selectbox("Choisir la Commune", sorted(gdf_comm[gdf_comm[c_pref] == pref][c_com].unique()))

    st.sidebar.header("🎨 Personnalisation")
    titre_p = st.sidebar.text_input("Titre personnalisé (Optionnel)")
    couleur = st.sidebar.color_picker("Couleur thématique", "#2E86C1")
    nom_auteur = st.sidebar.text_input("Nom de l'auteur *")

    # BOUTON DE GÉNÉRATION
    if st.sidebar.button("GÉNÉRER L'ATLAS HD", key="btn_generer_atlas"):
        if not nom_auteur:
            st.error("⚠️ Le nom de l'auteur est obligatoire pour signer la carte.")
        else:
            with st.spinner('Rendu cartographique en cours...'):
                chemin = generer_visuel_commune(com, couleur, nom_auteur, titre_p)
                
                if chemin:
                    st.image(chemin, use_container_width=True)
                    
                    # Bouton de téléchargement
                    with open(chemin, "rb") as f:
                        st.download_button(
                            label="📥 Télécharger l'Atlas HD (PNG)",
                            data=f,
                            file_name=f"Atlas_JCDC_{com}.png",
                            mime="image/png",
                            key="btn_telecharger"
                        )
                else:
                    st.error("Désolé, une erreur technique est survenue lors de la génération.")