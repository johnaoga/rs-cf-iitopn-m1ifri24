import streamlit as st
import numpy as np

def main():
    st.title("")

    # Création d'un menu déroulant avec des options
    menu_option = st.sidebar.selectbox("Menu", ["Accueil", "Information"])

    if menu_option == "Information":
        st.write("Nom : NSELE KISAMBU")
        st.write("Prénom : Grace")
    elif menu_option == "Acceuil":  # La bonne orthographe est "Accueil"
        # Création d'un bouton pour afficher le nom et prénom
        if st.button("Lire les informations"):
            st.write("Nom : NSELE KISAMBU")
            st.write("Prénom : Grace")
    else:
        # Interface Utilisateur
        st.title("Système de Recommandation de Films")

        num_films = st.number_input("Nombre de films:", min_value=1, step=1)
        num_users = st.number_input("Nombre d'utilisateurs:", min_value=1, step=1)
        top_n = st.number_input("Top N des recommandations:", min_value=1, step=1)

        # Génération du tableau de notation
        st.subheader("Tableau de Notation")
        ratings_table = np.zeros((num_users, num_films))

        for i in range(num_users):
            for j in range(num_films):
                ratings_table[i][j] = st.slider(f"Note Utilisateur {i+1} pour Film {j+1}:", 0, 5, 2)

        st.write("Tableau de Notation:", ratings_table)

        # Calcul des similarités entre utilisateurs (exemple simple avec la similarité cosinus)
        def cosine_similarity(user1, user2):
            return np.dot(user1, user2) / (np.linalg.norm(user1) * np.linalg.norm(user2))

        st.subheader("Similarités entre Utilisateurs")

        similarity_matrix = np.zeros((num_users, num_users))
        for i in range(num_users):
            for j in range(i + 1, num_users):
                similarity = cosine_similarity(ratings_table[i], ratings_table[j])
                similarity_matrix[i][j] = similarity
                similarity_matrix[j][i] = similarity
                st.write(f"Similarité entre Utilisateur {i+1} et Utilisateur {j+1}: {similarity:.2f}")

        # Calcul des notes estimées pour chaque utilisateur et film, en incluant les notes manquantes
        estimated_ratings_table = np.copy(ratings_table)  # Copie du tableau de notation pour inclure les notes manquantes

        for i in range(num_users):
            for j in range(num_films):
                if ratings_table[i][j] == 0:  # Vérifie si la note est manquante
                    estimated_ratings_table[i][j] = estimate_ratings(i, j, ratings_table, similarity_matrix)

        # Création du tableau pour afficher les notes manquantes et les notes estimées
        table_data = [["Utilisateurs", "Film", "Note Réelle", "Note Estimée"]]
        for i in range(num_users):
            for j in range(num_films):
                if ratings_table[i][j] == 0:
                    table_data.append([f"Utilisateur {i+1}", f"Film {j+1}", "-", estimated_ratings_table[i][j]])
                else:
                    table_data.append([f"Utilisateur {i+1}", f"Film {j+1}", int(ratings_table[i][j]), int(estimated_ratings_table[i][j])])

        # Affichage du tableau
        st.subheader("Tableau des Notes Manquantes et Notes Estimées")
        st.table(table_data)

        # Recherche de la note et recommandation pour un utilisateur et un film spécifiques
        st.subheader("Recherche Utilisateur/Film")

        selected_user = st.selectbox("Sélectionner un utilisateur:", [f"Utilisateur {i+1}" for i in range(num_users)])
        selected_film = st.selectbox("Sélectionner un film:", [f"Film {j+1}" for j in range(num_films)])
        selected_user_index = int(selected_user.split()[1]) - 1
        selected_film_index = int(selected_film.split()[1]) - 1

        if ratings_table[selected_user_index][selected_film_index] != 0:
            st.write(f"Note donnée par {selected_user} pour {selected_film}: {int(ratings_table[selected_user_index][selected_film_index])}")
            st.write(f"Note estimée pour {selected_user} pour {selected_film}: {int(estimated_ratings_table[selected_user_index][selected_film_index])}")
            if estimated_ratings_table[selected_user_index][selected_film_index] >= 3:
                st.write(f"Recommander ce film à {selected_user}: Oui")
            else:
                st.write(f"Recommander ce film à {selected_user}: Non")
        else:
            st.write(f"Note pour {selected_user}/{selected_film} manquante.")

def estimate_ratings(user_id, film_id, ratings_table, similarity_matrix):
    num_users, num_films = ratings_table.shape
    total_similarities = 0
    weighted_sum = 0
    for i in range(num_users):
        if i != user_id:
            total_similarities += similarity_matrix[user_id][i]
            weighted_sum += similarity_matrix[user_id][i] * ratings_table[i][film_id]
    if total_similarities == 0:
        return 0  # Impossible de calculer une estimation
    else:
        # Arrondir la note estimée à l'entier le plus proche
        return round(weighted_sum / total_similarities)

if __name__ == "__main__":
    main()

