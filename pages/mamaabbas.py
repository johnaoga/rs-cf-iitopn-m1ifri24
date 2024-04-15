import streamlit as st
import numpy as np


st.title("Système de recommandation de films")

# Saisie du nombre de films, d'utilisateurs et du top N des recommandations
num_movies = st.number_input("Nombre de films :", min_value=1, step=1)
num_users = st.number_input("Nombre d'utilisateurs :", min_value=1, step=1)
top_n = st.number_input("Top N recommandations :", min_value=1, step=1)


rating_table = np.zeros((num_users, num_movies))

# Saisie des notes pour chaque utilisateur et film
for i in range(num_users):
    for j in range(num_movies):
        rating = st.text_input(
            f"Note de l'utilisateur {i+1} pour le film {j+1} :", value="2"
        )
        if rating:
            rating_table[i][j] = int(rating)


st.write("Table de notation :")
st.write(rating_table)


# Fonction pour calculer la similarité entre utilisateurs
def user_similarity(user1, user2):
    dot_product = np.dot(user1, user2)
    norm_user1 = np.linalg.norm(user1)
    norm_user2 = np.linalg.norm(user2)
    return dot_product / (norm_user1 * norm_user2)



st.subheader("Similarités entre utilisateurs")
similarity_matrix = np.zeros((num_users, num_users))

# Calcul de la similarité entre chaque paire d'utilisateurs
for i in range(num_users):
    for j in range(i + 1, num_users):
        similarity = user_similarity(rating_table[i], rating_table[j])
        similarity_matrix[i][j] = similarity
        similarity_matrix[j][i] = similarity
        st.write(
            f"Similarité entre l'utilisateur {i+1} et l'utilisateur {j+1} : {similarity:.2f}"
        )


# Fonction pour estimer les notes manquantes
def estimate_ratings(user_id, movie_id, rating_table, similarity_matrix):
    total_similarities = 0
    weighted_sum = 0

    # Calcul de la note estimée en utilisant la moyenne pondérée des notes des utilisateurs similaires
    for other_user_id in range(num_users):
        if other_user_id != user_id:
            similarity = similarity_matrix[user_id][other_user_id]
            total_similarities += similarity
            weighted_sum += similarity * rating_table[other_user_id][movie_id]


    if total_similarities == 0:
        return 0
    else:
        return round(weighted_sum / total_similarities)



estimated_rating_table = np.copy(rating_table)

# Estimation des notes manquantes dans la table de notation
for i in range(num_users):
    for j in range(num_movies):
        if rating_table[i][j] == 0:
            estimated_rating_table[i][j] = estimate_ratings(
                i, j, rating_table, similarity_matrix
            )


table_data = [["Utilisateur", "Film", "Note réelle", "Note estimée"]]

for i in range(num_users):
    for j in range(num_movies):
        if rating_table[i][j] == 0:
            table_data.append(
                [
                    f"Utilisateur {i+1}",
                    f"Film {j+1}",
                    "-",
                    estimated_rating_table[i][j],
                ]
            )
        else:
            table_data.append(
                [
                    f"Utilisateur {i+1}",
                    f"Film {j+1}",
                    rating_table[i][j],
                    estimated_rating_table[i][j],
                ]
            )

# Affichage des notes manquantes et des notes estimées dans un tableau
st.subheader("Notes manquantes et notes estimées")
st.table(table_data)
