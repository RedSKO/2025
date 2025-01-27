# Importation des bibliothèques nécessaires pour Streamlit
import streamlit as st
import pandas as pd

# --- Étape 1 : Titre et introduction de la démo --- #
st.title("Démo : Assistant Financier Intelligent (AFI)")
st.write("""
Cette démo illustre comment un agent AI peut analyser les données extraites par ABBYY Vantage pour 
identifier des anomalies et proposer des recommandations.
""")

# --- Étape 2 : Chargement des données extraites --- #
st.header("1. Importer une facture (données extraites)")
uploaded_file = st.file_uploader("Importer un fichier JSON ou CSV contenant les données extraites par ABBYY", type=["json", "csv"])

if uploaded_file:
    # Lecture des données
    if uploaded_file.name.endswith('.csv'):
        data = pd.read_csv(uploaded_file)
    else:
        data = pd.read_json(uploaded_file)
    
    st.write("### Données extraites :")
    st.dataframe(data)

    # --- Étape 3 : Simuler l'analyse AI --- #
    st.header("2. Analyse par l'agent AI")
    anomalies = []

    # Détection d'anomalies fictives
    for index, row in data.iterrows():
        if "TVA" in data.columns and row["TVA"] != 20.0:
            anomalies.append(f"Ligne {index + 1}: Taux de TVA incorrect ({row['TVA']}% au lieu de 20%).")
        if "Montant" in data.columns and row["Montant"] > 5000:
            anomalies.append(f"Ligne {index + 1}: Dépassement budgétaire détecté (montant de {row['Montant']} €).")

    # Afficher les anomalies détectées
    if anomalies:
        st.error("Anomalies détectées :")
        for anomaly in anomalies:
            st.write(f"- {anomaly}")
    else:
        st.success("Aucune anomalie détectée.")

    # --- Étape 4 : Recommandations --- #
    st.header("3. Recommandations")
    st.write("""
    En fonction des anomalies détectées, l'agent propose les actions suivantes :
    """)

    # Exemples d'actions proposées
    actions = ["Valider la facture malgré l'anomalie", 
               "Renvoyer au fournisseur pour correction", 
               "Escalader au manager pour décision"]

    for action in actions:
        st.button(action)

else:
    st.info("Veuillez importer un fichier pour continuer.")
