import streamlit as st
import pandas as pd
import os

if 'num_films' not in st.session_state:
    st.session_state.num_films = 0

st.title('Partagez votre avis sur nos films avec nous')

# Liste pour stocker les données des films
films_data = []

# Vérifier si le fichier CSV existe
if 'films_notes.csv' in os.listdir():
    existing_df = pd.read_csv('films_notes.csv')
    films_data.extend(existing_df.to_dict(orient='records'))
    
while True:
    # Générer une clé unique pour chaque itération de la boucle
    widget_key = f"film_input_{st.session_state.num_films}"
    
    # Champ pour le nom de l'utilisateur
    user_name = st.text_input('Nom de l\'utilsateur')

    # Champ pour le nom du film
    film_name = st.text_input(f'Nom du film ', key=widget_key)

    # Champ pour la note du film
    film_rating = st.number_input(f'Votre note concernant le film {st.session_state.num_films}', min_value=0, max_value=10, value=0, step=1, key=widget_key + "_rating")

    # Ajouter les données du film à la liste si le nom du film n'est pas vide
    if film_name.strip():
        films_data.append({'User_Name': user_name, 'Movie_Name': film_name, 'Rating': film_rating})

    # Bouton pour ajouter un autre film ou terminer avec une clé unique
    add_another = 0
    if not add_another:
        break

    # Incrémenter le nombre de films
    st.session_state.num_films += 1
    
films_df = pd.DataFrame(films_data)


if not films_df.empty:
    if st.button('Terminer'):
        films_df.to_csv('notes.csv', index=False)
        st.success('Les données des films ont été enregistrées dans le fichier films_notes.csv avec succès!')
        
else:
    st.warning('Aucune donnée de film saisie!')    

def charger_donnees(filename):
    data = pd.read_csv(filename)
    return data

data = charger_donnees('notes.csv')

st.dataframe(data) 

# Convertissement des données en une matrice utilisateur-film pour le calcul de similarité
user_movie_matrix = data.pivot(index='User_Name', columns='Movie_Name', values='Rating').fillna(0)


# Sélection de l'utilisateur et du film
selected_user = st.selectbox('Choisissez un utilisateur :', user_movie_matrix.index)
unrated_movies = user_movie_matrix.columns[user_movie_matrix.loc[selected_user] == 0]
selected_movie = st.selectbox('Choisissez un film non noté :', unrated_movies)


# Définir une fonction pour calculer la similarité de Jaccard entre deux ensembles
def jaccard_similarity(set1, set2):
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union != 0 else 0

# Calculer la similarité de Jaccard
similarities = {}
movies_user = set(user_movie_matrix.loc[selected_user][user_movie_matrix.loc[selected_user] > 0].index)
for movie in movies_user:
    if movie != selected_movie:
        movies_pair = (selected_movie, movie) if selected_movie < movie else (movie, selected_movie)
        similarity = jaccard_similarity(set(user_movie_matrix[selected_movie][user_movie_matrix[selected_movie] > 0].index),
                                         set(user_movie_matrix[movie][user_movie_matrix[movie] > 0].index))
        similarities[movies_pair] = similarity
        
top_n = st.number_input("Nombre du top n", min_value=1, max_value=5, value=3, step=1)

# Trier les films similaires par ordre décroissant de similarité
similar_movies = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
top_n_similar_movies = [movie[0] for movie in similar_movies[:top_n]]


# Calculer la note prédite pour le film choisi en utilisant la somme pondérée des notes des films similaires
weighted_sum = 0
total_similarity = 0
for similar_movie, similarity in similar_movies[:top_n]:
    weighted_sum += similarity * user_movie_matrix.loc[selected_user][similar_movie[1]]
    total_similarity += similarity

predicted_rating = weighted_sum / total_similarity if total_similarity != 0 else 0


# Note de comparaison
comparison_rating = 4


# Comparer la note prédite avec la note de comparaison pour recommander le film à l'utilisateur
if predicted_rating >= comparison_rating:
    st.success(f"Vous pourriez aimer le film {selected_movie} avec une note prédite de {predicted_rating:.2f}.")
else:
    st.warning(f"La note prédite pour le film {selected_movie} est de {predicted_rating:.2f}, ce qui est inférieur à la note de comparaison.")

