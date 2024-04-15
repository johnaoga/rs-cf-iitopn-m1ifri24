import streamlit as st
import numpy as np
import pandas as pd


st.sidebar.write("Ariel AHOGNISSE")
st.sidebar.write("Master 1 - GL")

if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Accueil'

def page_home():
    st.title("TP1 : Recommendation system: Collaborative Filtering (itemitem top n)")
    st.write("Cet exercice comporte les deux options d'insertion de données, la première manuelle et l'autre permet l'importation des données depuis un fichier csv.")
    st.write("Le fichier 'class_table.csv' contient les données du tableau étudié en classe pendant le cours sur des systèmes de recommandation")
    st.write("*Seuls les packages streamlit, numpy et pandas ont été utilisés")

## Insertion manuelle
def page_manual():
    st.header(':blue[Prediction de notes inserées manuellement]')

    # Création des différents containers
    dataframe_container = st.empty()

    old_dataframe = st.empty()

    dataframe_fields = st.container()

    scores_field = st.container()

    n_choice = st.container()

    user_choice = st.container()

    predicted_result = st.container()

    users_number = 4
    movies_number = 4
    N = 2

    # Définir les variables de session
    if 'dataframe' not in st.session_state:
        st.session_state['dataframe'] = pd.DataFrame()

    if 'show_dataframe_fields' not in st.session_state:
        st.session_state['show_dataframe_fields'] = True
        
    if 'show_scores_fields' not in st.session_state:
        st.session_state['show_scores_fields'] = False

    if 'choose_n' not in st.session_state:
        st.session_state['choose_n'] = False

    if 'show_user_choice' not in st.session_state:
        st.session_state['show_user_choice'] = False

    if 'show_result' not in st.session_state:
        st.session_state['show_result'] = False

    if 'n' not in st.session_state:
        st.session_state['n'] = 2

    scores_grid = st.session_state['dataframe']
    
    # Definir la taille du dataframe
    def validate_dataframe_size():
        st.session_state.users_number = users_number
        st.session_state.movies_number = movies_number

        st.session_state['show_dataframe_fields'] = not st.session_state['show_dataframe_fields']
        st.session_state['show_scores_fields'] = not st.session_state['show_scores_fields']

    # Calculer les notes maquantes
    def validate_scores_datas():

        users_labels = {scores_grid.columns[i]: f'Utilisateur {i+1}' for i in range(st.session_state['users_number'])}
        movies_labels = {scores_grid.index[i]: f'Film {i+1}' for i in range(st.session_state['movies_number'])}
        scores_grid.rename(columns=users_labels, index=movies_labels, inplace=True)

        st.session_state['n'] = N
        st.session_state['choose_n'] = not st.session_state['choose_n']
        st.session_state['show_user_choice'] = not st.session_state['show_user_choice']

        grid = st.session_state['dataframe']
        grid.replace(0.0, np.nan, inplace=True)

        for i in range(st.session_state['movies_number']):
            for j in range(st.session_state['users_number']):
                if np.isnan(grid.iloc[i,j]):
                    predicted_value = predict_user_rating(movie_index=i, user_index= j, top_n= st.session_state['n'], df= grid)
                    if np.isnan(predicted_value):
                        scores_grid.iloc[i,j] = np.nan
                    else:
                        scores_grid.iloc[i,j] = round(predicted_value)
                    st.session_state['dataframe'] = scores_grid
        dataframe_container.dataframe(scores_grid)

    # Definir la valeur de N
    def define_n():
        st.session_state['show_scores_fields'] = not st.session_state['show_scores_fields']
        st.session_state['choose_n'] = not st.session_state['choose_n']

    def predict_user_rating(df, movie_index, user_index, top_n):
        # Remplacer les valeurs NaN par des zéros pour le calcul de la similarité
        
        ratings_matrix = df.fillna(0).values
        
        # Calculer la matrice de similarité cosinus entre les films
        similarity_matrix = np.dot(ratings_matrix, ratings_matrix.T)
        norms = np.linalg.norm(ratings_matrix, axis=1)
        similarity_matrix = similarity_matrix / norms[:, None]
        similarity_matrix = similarity_matrix / norms[None, :]
        
        # Extraire les notes de l'utilisateur et vérifier si la note est manquante
        user_ratings = df.iloc[:, user_index].values
        if np.isnan(user_ratings[movie_index]):
            # Trouver les films les plus similaires qui ont été notés par l'utilisateur
            similar_films = np.argsort(-similarity_matrix[movie_index, :])
            similar_films = similar_films[~np.isnan(user_ratings[similar_films])]
            if len(similar_films) > top_n:
                similar_films = similar_films[:top_n]
            
            # Calculer la note prédite
            numerator = similarity_matrix[movie_index, similar_films].dot(user_ratings[similar_films])
            denominator = similarity_matrix[movie_index, similar_films].sum()
            predicted_rating = numerator / denominator if denominator != 0 else 0
        else:
            predicted_rating = user_ratings[movie_index]
        
        return predicted_rating

    # Rechercher le score dans le tableau
    def check_movie_score(user, movie):
        actual_dataframe = st.session_state['dataframe']
        original_dataframe = st.session_state['original_dataframe']
        st.session_state['show_result'] = True
        predicted_rating = actual_dataframe.iloc[movie, user]

        if st.session_state['show_result'] == True:
            if actual_dataframe.iloc[movie, user] != original_dataframe.iloc[movie, user]:
                predicted_result.write("Cette valeur a été calculée par le programme")
                if np.isnan(predicted_rating):
                    predicted_result.write("Cette valeur n'a pas pu être prédite")
                elif predicted_rating < 3:
                    predicted_result.write(f"L'utilisateur {user +1} n'aimerait pas le film {movie +1}, avec une note possible de {actual_dataframe.iloc[movie, user]}")
                elif predicted_rating >= 3:
                    predicted_result.write(f"L'utilisateur {user +1} pourrait apprécier le film {movie +1}, avec une note possible de {actual_dataframe.iloc[movie, user]}")
            else:
                predicted_result.write(f"Cette valeur a n'a pas été calculée, la note existante est de {actual_dataframe.iloc[movie, user]}")


    # Déroulement du programme
    if st.session_state['show_dataframe_fields']:
        column1, column2 = dataframe_fields.columns(2)
        with column1:
            movies_number = dataframe_fields.number_input('Nombre de films:', 4)
        with column2:
            users_number = dataframe_fields.number_input('Nombre d\'utilisateurs:', 4)

        dataframe_fields.button("Valider", on_click= validate_dataframe_size)

    if st.session_state['show_scores_fields'] == True:
        scores_field.write('Entrez les notes: (si aucune laisser a 0)')
        for i in range(st.session_state['movies_number']):
            for j in range(st.session_state['users_number']):
                scores_grid.loc[i,j] = scores_field.number_input(f'Note du Film {i+1} par l\'utilisateur {j+1}: ', 0, max_value=5)
                st.session_state['dataframe'] = scores_grid
                dataframe_container.dataframe(scores_grid)

        dataframe_container.dataframe(scores_grid)
        
        st.session_state['dataframe'] = scores_grid
        st.session_state['original_dataframe'] = scores_grid.copy()

        scores_field.button("Valider les notes", on_click= define_n)
            
    if st.session_state['choose_n'] == True:
        N = n_choice.number_input('Valeur du top n:', 2)
        st.session_state['n'] = N
        n_choice.button("Valider N", on_click= validate_scores_datas)

    if st.session_state['show_user_choice'] == True:
        dataframe_container.dataframe(st.session_state['dataframe'])
        grid = st.session_state['dataframe']
        user_choice.write("Choisir une donnée à predire")
        user_to_predict = user_choice.number_input('Utilisateur:', 1, max_value= len(grid.columns))
        movie_to_predict = user_choice.number_input('Films:', 1, max_value= len(grid))

        user_choice.button("Evaluer", on_click= check_movie_score(user= user_to_predict-1, movie= movie_to_predict-1))

def page_csv():
    st.header(':blue[Prediction de notes à partir d\'un csv]')

    # Création des différents containers
    dataframe_container_ = st.empty()

    csv_loader = st.container()

    scores_field_ = st.container()

    n_choice_ = st.container()

    user_choice_ = st.container()

    predicted_result_ = st.container()

    if 'dataframe_' not in st.session_state:
        st.session_state['dataframe_'] = pd.DataFrame()

    users_number_ = 0
    movies_number_ = 0

    if 'show_csv_field_' not in st.session_state:
        st.session_state['show_csv_field_'] = True

    if 'choose_n_' not in st.session_state:
        st.session_state['choose_n_'] = False

    if 'show_user_choice_' not in st.session_state:
        st.session_state['show_user_choice_'] = False

    if 'show_result_' not in st.session_state:
        st.session_state['show_result_'] = False

    if 'n_' not in st.session_state:
        st.session_state['n_'] = 2

    scores_grid_ = st.session_state['dataframe_']

    # Calculer les notes maquantes
    def validate_scores_datas():
        st.session_state['n_'] = N
        st.session_state['choose_n_'] = not st.session_state['choose_n_']
        st.session_state['show_user_choice_'] = not st.session_state['show_user_choice_']

        grid = st.session_state['dataframe_']

        for i in range(st.session_state['movies_number_']):
            for j in range(st.session_state['users_number_']):
                if np.isnan(grid.iloc[i,j]):
                    predicted_value = predict_user_rating(movie_index=i, user_index= j, top_n= st.session_state['n_'], df= grid)
                    scores_grid_.iloc[i,j] = round(predicted_value)
                    st.session_state['dataframe_'] = scores_grid_
        dataframe_container_.dataframe(scores_grid_)

    # Definir la valeur de N
    def define_n():
        st.session_state['show_csv_field_'] = not st.session_state['show_csv_field_']
        st.session_state['choose_n_'] = not st.session_state['choose_n_']
        movies_number_ = len(scores_grid_)
        users_number_ = len(scores_grid_.columns)

        st.session_state.users_number_ = users_number_
        st.session_state.movies_number_ = movies_number_

    def predict_user_rating(df, movie_index, user_index, top_n):
        # Remplacer les valeurs NaN par des zéros pour le calcul de la similarité
        
        ratings_matrix = df.fillna(0).values
        
        # Calculer la matrice de similarité cosinus entre les films
        similarity_matrix = np.dot(ratings_matrix, ratings_matrix.T)
        norms = np.linalg.norm(ratings_matrix, axis=1)
        similarity_matrix = similarity_matrix / norms[:, None]
        similarity_matrix = similarity_matrix / norms[None, :]
        
        # Extraire les notes de l'utilisateur et vérifier si la note est manquante
        user_ratings = df.iloc[:, user_index].values
        if np.isnan(user_ratings[movie_index]):
            # Trouver les films les plus similaires qui ont été notés par l'utilisateur
            similar_films = np.argsort(-similarity_matrix[movie_index, :])
            similar_films = similar_films[~np.isnan(user_ratings[similar_films])]
            if len(similar_films) > top_n:
                similar_films = similar_films[:top_n]
            
            # Calculer la note prédite
            numerator = similarity_matrix[movie_index, similar_films].dot(user_ratings[similar_films])
            denominator = similarity_matrix[movie_index, similar_films].sum()
            predicted_rating = numerator / denominator if denominator != 0 else 0
        else:
            predicted_rating = user_ratings[movie_index]
        
        return predicted_rating

    # Rechercher le score dans le tableau
    def check_movie_score(user, movie):
        actual_dataframe = st.session_state['dataframe_']
        original_dataframe = st.session_state['original_dataframe_']
        st.session_state['show_result_'] = True
        predicted_rating = actual_dataframe.iloc[movie, user]

        if st.session_state['show_result_'] == True:
            if actual_dataframe.iloc[movie, user] != original_dataframe.iloc[movie, user]:
                predicted_result_.write("Cette valeur a été calculée par le programme")
                if predicted_rating == np.nan:
                    predicted_result_.write("Cette valeur n'a pas pu être prédite")
                elif predicted_rating < 3:
                    predicted_result_.write(f"Cet utilisateur {user +1} n'aimerait pas le film {movie +1}, avec une note possible de {actual_dataframe.iloc[movie, user]}")
                elif predicted_rating >= 3:
                    predicted_result_.write(f"L'utilisateur {user +1} pourrait apprécier le film {movie +1}, avec une note possible de {actual_dataframe.iloc[movie, user]}")
            else:
                predicted_result_.write(f"Cette valeur a n'a pas été calculée, la note existante est de {actual_dataframe.iloc[movie, user]}")

    # Déroulement du programme
    if st.session_state['show_csv_field_']:
        uploaded_file = csv_loader.file_uploader("Charger un csv:", type=["csv"])
        if uploaded_file is not None:
            scores_grid_ = pd.read_csv(uploaded_file)
            st.session_state['dataframe_'] = scores_grid_
            st.session_state['original_dataframe_'] = scores_grid_.copy()
            csv_loader.button("Valider", on_click= define_n)
        

    if st.session_state['choose_n_'] == True:
        dataframe_container_.dataframe(scores_grid_)
        N = n_choice_.number_input('Valeur du top n:', 2)
        st.session_state['n_'] = N
        n_choice_.button("Valider N", on_click= validate_scores_datas)

    if st.session_state['show_user_choice_'] == True:
        dataframe_container_.dataframe(st.session_state['dataframe_'])
        grid = st.session_state['dataframe_']
        user_choice_.write("Choisir une donnée à predire")
        user_to_predict = user_choice_.number_input('Utilisateur:', 1, max_value= len(grid.columns))
        movie_to_predict = user_choice_.number_input('Films:', 1, max_value= len(grid))

        user_choice_.button("Evaluer", on_click= check_movie_score(user= user_to_predict-1, movie= movie_to_predict-1))


pages = {
    "Accueil": page_home,
    "Insertion manuelle": page_manual,
    "Insertion par csv": page_csv
}

for page_name in pages.keys():
    if st.sidebar.button(page_name):
        st.session_state.current_page = page_name

pages[st.session_state.current_page]()