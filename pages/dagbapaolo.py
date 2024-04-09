import pandas as pd
import streamlit as st
from sklearn.metrics.pairwise import cosine_similarity

# Fonction pour charger les données des utilisateurs et des films à partir du fichier CSV
def load_data():
    return pd.read_csv('notes.csv', index_col=0)

# Fonction pour enregistrer les notes dans un fichier CSV
def save_notes_to_csv(notes_df):
    try:
        notes_df.to_csv('notes.csv')
        return True
    except Exception as e:
        st.error(f"Erreur lors de l'enregistrement des notes : {str(e)}")
        return False

# Page "Enregistrement des données"
def enregistrement_des_donnees():
    st.title("Enregistrement des données")
    st.write("Saisissez le nom de chaque utilisateur :")
    utilisateurs = [st.text_input(f"Utilisateur {i+1}") for i in range(5)]
    utilisateurs = [user for user in utilisateurs if user]  # Supprimer les valeurs vides
    st.write("Saisissez le nom de chaque film :")
    films = [st.text_input(f"Film {i+1}") for i in range(5)]
    if st.button("Enregistrer les noms"):
        if save_notes_to_csv(pd.DataFrame(columns=utilisateurs, index=films)):
            st.success("Les noms ont été enregistrés avec succès dans le fichier notes.csv.")
            st.write("")
            if st.button("Passer à la page suivante"):
                st.experimental_set_query_params(page="Attribution des notes")

# Page "Attribution des notes"
def attribution_des_notes():
    st.title("Attribution des notes")

    # Charger les données depuis notes.csv
    df_notes = load_data()

    if df_notes.empty:
        st.error("Les données doivent d'abord être enregistrées avec succès avant d'accéder à cette page.")
        return

    utilisateurs = df_notes.columns
    films = df_notes.index

    st.header("Attribution des notes")

    for utilisateur in utilisateurs:
        st.subheader(f"Notes pour \"{utilisateur}\":")
        for film in films:
            st.subheader(f"Note pour \"{film}\":")
            key = f"{utilisateur}-{film}"
            note = st.number_input("Note", min_value=-1.0, max_value=5.0, step=0.5, key=key, value=df_notes.loc[film, utilisateur] if (film, utilisateur) in df_notes.index else None)
            if pd.notnull(note):
                df_notes.loc[film, utilisateur] = note
        st.write("")

    # Enregistrer les modifications
    if st.button("Enregistrer les notes"):
        if save_notes_to_csv(df_notes):
            st.success("Les notes ont été enregistrées avec succès.")
        else:
            st.error("Une erreur s'est produite lors de l'enregistrement des notes.")

# Page "Nouvelles fonctionnalités"
def nouvelles_fonctionnalites():
    st.title("Nouvelles fonctionnalités")

    # Charger les données
    df_notes = load_data()

    # Obtenir la liste des utilisateurs et des films
    utilisateurs = df_notes.columns
    films = df_notes.index

    st.header("Spécifier le top 'n' des recommandations")
    n_top = st.number_input("Nombre de recommandations à afficher :", min_value=1, max_value=len(films), value=5)

    st.header("Afficher la matrice avec les notes manquantes et satisfaites")
    st.write(df_notes)

    st.header("Rechercher une note spécifique")
    utilisateur = st.selectbox("Sélectionner un utilisateur :", utilisateurs)
    film = st.selectbox("Sélectionner un film :", films)
    note_utilisateur = df_notes.loc[film, utilisateur]
    note_utilisateur = note_utilisateur if not pd.isna(note_utilisateur) else "Non noté"
    st.write(f"Note attribuée par {utilisateur} au film {film} : {note_utilisateur}")
    recommander = st.radio("Recommander ce film à cet utilisateur ?", ("Oui", "Non"))
    if recommander == "Oui":
        st.write("Vous avez choisi de recommander ce film à cet utilisateur.")
    else:
        st.write("Vous avez choisi de ne pas recommander ce film à cet utilisateur.")

# Page "Recommandation de films"
def recommandation_de_films():
    st.title("Recommandation de films")

    # Charger les données depuis notes.csv
    df_notes = load_data()

    # Calculer la similarité entre les utilisateurs
    similarity_matrix = cosine_similarity(df_notes.fillna(0))

    # Sélectionner l'utilisateur actuel
    user = st.selectbox("Sélectionner un utilisateur :", df_notes.columns)

    # Identifier les films non notés par l'utilisateur actuel
    films_non_notes = df_notes.index[df_notes.loc[:, user].isna()]

    # Filtrer la matrice de similarité pour ne considérer que les utilisateurs similaires
    similar_users = similarity_matrix[df_notes.columns.get_loc(user)].argsort()[::-1][1:]

    # Dictionnaire pour stocker les notes prédites des films non notés
    predicted_ratings = {}

    # Calculer les notes prédites pour chaque film non noté
    for film in films_non_notes:
        sum_ratings = 0
        sum_similarity = 0
        for sim_user in similar_users:
            rating = df_notes.loc[film, df_notes.columns[sim_user]]
            if pd.notnull(rating):
                sum_ratings += similarity_matrix[df_notes.columns.get_loc(user), sim_user] * rating
                sum_similarity += similarity_matrix[df_notes.columns.get_loc(user), sim_user]
        if sum_similarity != 0:
            predicted_ratings[film] = sum_ratings / sum_similarity

    # Afficher les films recommandés avec les notes prédites
    if predicted_ratings:
        st.write("Films recommandés :")
        for film, rating in sorted(predicted_ratings.items(), key=lambda x: x[1], reverse=True):
            st.write(f"{film}: Note prédite - {rating:.2f}")
    else:
        st.write("Aucune recommandation disponible pour le moment.")

# Fonction principale
def main():
    st.title("Système de Recommandation de Films")

    # Barre de navigation horizontale
    page = st.radio("Navigation", ["Enregistrement des données", "Attribution des notes", "Nouvelles fonctionnalités", "Recommandation de films"])

    if page == "Enregistrement des données":
        enregistrement_des_donnees()
    elif page == "Attribution des notes":
        attribution_des_notes()
    elif page == "Nouvelles fonctionnalités":
        nouvelles_fonctionnalites()
    elif page == "Recommandation de films":
        recommandation_de_films()

if __name__ == "__main__":
    main()
