import streamlit as st

import pandas as pd
import numpy as np

# Fonction pour calculer la similarité entre deux films
def calculate_similarity(ratings, movie1, movie2):
    
    # Trouver les utilisateurs qui ont noté les deux films
    common_users = ratings[movie1].dropna().index.intersection(ratings[movie2].dropna().index)
    
    # Utiliser la moyenne des notes de tous les utilisateurs pour chaque film
    mean_movie1 = ratings[movie1].mean()
    mean_movie2 = ratings[movie2].mean()

    #Calculer les écarts pour chaque film
    ratings_movie1 = ratings.loc[common_users, movie1]
    ratings_movie2 = ratings.loc[common_users, movie2]
    
    ratings_movie1_array = ratings_movie1.to_numpy()
    ratings_movie2_array = ratings_movie2.to_numpy()

    ecarts_movie1 = []
    for i in range(len(ratings_movie1_array)) :
        ecarts_movie1.append(ratings_movie1_array[i] - mean_movie1)

    ecarts_movie2 = []
    for i in range(len(ratings_movie2_array)) :
        ecarts_movie2.append(ratings_movie2_array[i] - mean_movie2)

    #calculer la somme des produits des écarts
    produits_ecart= []
    for i in range(len(ecarts_movie1)) :
        produits_ecart.append(ecarts_movie1[i]*ecarts_movie2[i])

    somme_produits_ecarts=0
    for i in range(len(produits_ecart)) :
        somme_produits_ecarts = somme_produits_ecarts + produits_ecart[i]

    numerator = somme_produits_ecarts

    #calculer somme des écarts type
    somme_ecart_type_movie1 = 0
    for i in range (len(ecarts_movie1)):
        somme_ecart_type_movie1 = somme_ecart_type_movie1 + (ecarts_movie1[i])**2

    somme_ecart_type_movie2 = 0
    for i in range (len(ecarts_movie2)):
        somme_ecart_type_movie2 = somme_ecart_type_movie2 + (ecarts_movie2[i])**2
    
    denominator = np.sqrt(somme_ecart_type_movie1) * np.sqrt(somme_ecart_type_movie2)
    
    return numerator/denominator if denominator != 0 else 0


def predict_missing_rating(ratings, user, movie, n = 2):
    similarities = []
    
    # Calculer la similarité du film movie avec tous les autres films
    for other_movie in ratings.columns:
        if other_movie != movie:
            similarity = calculate_similarity(ratings, movie, other_movie)
            similarities.append((other_movie, similarity))
    
    # Trier par similarité et prendre les top n films
    top_similar_movies = sorted(similarities, key=lambda x: x[1], reverse=True)[:n]
    
    # Calculer la note prédite en utilisant la somme pondérée des similarités
    ratings_filled = ratings.fillna(0)
    numerator = sum(ratings_filled.loc[user, m] * sim for m, sim in top_similar_movies)
    denominator = sum(sim for _, sim in top_similar_movies)
       
    predicted_rating = numerator / denominator if denominator != 0 else 0

    return predicted_rating
    
# Interface Streamlit pour entrer les notes et prédire les notes manquantes
st.title('Système de recommandation de films')

# Entrée du nombre de films et d'utilisateurs
num_users = st.number_input('Nombre d\'utilisateurs', min_value=1, value=3)
num_movies = st.number_input('Nombre de films', min_value=1, value=3)

# Création d'un DataFrame vide pour les notes
ratings = pd.DataFrame(
    index=[f'User{i+1}' for i in range(num_users)],
    columns=[f'Movie{i+1}' for i in range(num_movies)]
)

# Entrée des notes des utilisateurs
for user in ratings.index:
    for movie in ratings.columns:
        rating = st.number_input(f'Note de {user} pour {movie} (laissez vide si inconnu):',
                                 key=f'{user}_{movie}', min_value=0.0, max_value=5.0, value=np.nan, step=0.5)
        ratings.at[user, movie] = rating

nb = st.number_input('Entrez le n du top n', step=1, format='%d')

if st.button('Afficher le dataframe') :
    st.write(ratings)   

original_ratings = ratings.copy()

if st.button('Afficher le dataframe avec les notes manquantes'):
    for user in ratings.index:
        for movie in ratings.columns:
            if pd.isna(ratings.at[user, movie]):
              #st.write(calculSimil(ratings, movie))
                predicted_rating = predict_missing_rating(ratings, user, movie, nb)
                ratings.at[user, movie] = predicted_rating
    
    st.write(ratings)

text_style = """
<style>
.big-font {
    font-weight : bold;
    font-size:20px !important;
    color: #4E9AF1;
}
</style>
"""

# Injecter le CSS avec st.markdown
st.markdown(text_style, unsafe_allow_html=True)

# Utiliser la classe CSS pour styliser le texte
st.markdown('<p class="big-font">Rechercher la note d\'un utilisateur pour un film spécifique</p>', unsafe_allow_html=True)
    
#st.markdown("**Rechercher la note d'un utilisateur pour un film spécifique**")
col3, col4 = st.columns(2)
with col3:
    selected_user = st.selectbox('Choisir un utilisateur', ratings.index)
with col4:
    selected_movie = st.selectbox('Choisir un film', ratings.columns)
if st.button('Afficher la note'):
    rating = ratings.at[selected_user, selected_movie]
    original_rating = original_ratings.at[selected_user, selected_movie]
    if pd.isna(original_rating):
        rating_type = "calculée"
    else:
        rating_type = "originale"
        st.write(f"La note de {selected_user} pour {selected_movie} est {rating_type} et vaut {rating:.1f}.")
    if rating >= 3:
        st.success(f"Nous recommandons donc le film {selected_movie} à {selected_user}!")
    elif rating < 3 :
        st.error(f"Nous ne recommandons donc pas le film {selected_movie} à {selected_user}!")