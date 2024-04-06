import streamlit as st
import pandas as pd
from math import isnan
import numpy as np
from math import isnan
import uuid

def similarity(x, y):
    x = x.astype(float)
    y = y.astype(float)
    
    moy_x = np.nanmean(x)
    moy_y = np.nanmean(y)
   
    x_w_nan = np.isnan(x)
    y_w_nan = np.isnan(y)

    x_f = x[~x_w_nan & ~y_w_nan]
    y_f = y[~x_w_nan & ~y_w_nan]

    diff_x = x_f - moy_x
    diff_y = y_f - moy_y
    
    sum_product = np.sum(diff_x * diff_y)
    
    sum_carre_x = np.sum(diff_x ** 2)
    sum_carre_y = np.sum(diff_y ** 2)
    
    denom = np.sqrt(sum_carre_x) * np.sqrt(sum_carre_y)
    
    if denom == 0:
        return 0
    
    corr_pear = sum_product / denom
    
    return corr_pear

def predict_rating(user, movie, data, n=3):
    
    if isnan(float(data.loc[movie, user])):
        x = np.array(data.loc[movie])
        

        # problematic_index = np.where(np.char.isdigit(x.astype(str)) == False)[0][0]
        # problematic_value = x[problematic_index]

        # print("Problematic value:", problematic_value)

        # # Handle the problematic value by removing the entire row
        # x = np.delete(x, problematic_index)

        # print("Array after removing problematic value:", x)
                
        similarities = {}
        for key, value in data.iterrows():
            if key != movie:
                sim = similarity(x, value.values)
                similarities[key] = round(sim, 2)
    
        top_n_similarities = {}
        i = 0
        for key, value in sorted(similarities.items(), key=lambda x:x[1], reverse=True):
            if value > 0:
                if i < n:
                    top_n_similarities[key] = value
                    i += 1
                else:
                    break 

        sum_product = 0
        sum_sim_top_n = 0
        
        for key, value in top_n_similarities.items():
            if isnan(float(data.loc[key,user])):
                not_ = 0
            else:
                not_ = data.loc[key,user]
            product = not_ * value
            sum_product += product
            sum_sim_top_n += value

        if sum_sim_top_n == 0:
            return 0
        else:
            note = round(sum_product / sum_sim_top_n, 2)
            return note

def convert_to_numeric(value):
    try:
        return float(value)
    except ValueError:
        return np.nan
    
def main():
    
    st.title("Système de recommandation : Filtrage collaborative")

    st.subheader(":blue[Choisir la manière dont les données seront initialisées.]")
        
    selected_option = st.selectbox("Sélectionnez l'option pour initialiser", ["Mettre mes données manuellement","Télécharger un fichier CSV", ])
    
    users = [] 
    movies = [] 
    total_movies = 3
    total_users = 3
    data_frames = None
    file = None
    
    if selected_option == "Mettre mes données manuellement":
            
        st.subheader(":blue[Initialiser le nombre total de film et d'utilisateur dans notre data set.]")
        
        column1, column2 = st.columns(2)
        
        with column1:
            
            total_movies = st.number_input(
                'Combien de film aviez vous sur votre système?' ,
                step=1, 
                format="%d", 
                min_value=3
            )
            
            st.subheader(":blue[Réccupérer les films.]")

            if len(movies) != total_movies or len(movies) == 0:
                st.warning(f"Svp renseignez les films.")
                
            for i in range(int(total_movies)):
                    
                movie = st.text_input(f"Entrez le nom  du film n°{i+1}: ", key="movie_"+str(i))
                if movie.strip() != "":
                    if movie not in movies:
                        movies.append(movie)
                    else:
                        st.warning(f"Le film '{movie}' a déjà été saisi. Veuillez saisir un autre film.")

        with column2:
            
            total_users = st.number_input(
                'Combien d\'utilisateurs aviez vous? ' ,
                step=1, 
                format="%d",
                min_value=3
            )
        
            st.subheader(":blue[Réccupérer les utilisateurs]")

            if len(users) == 0 or len(users) != total_users:
                st.warning(f"Svp renseignez les utilisateurs.")
                    
            for i in range(int(total_users)):
                    
                user = st.text_input(f"Entrez l'utilisateur n°{i+1}: ", key="user_"+str(i))
                if user.strip() != "":
                    if user not in users:
                        users.append(user)
                    else:
                        st.warning(f"L'utilisateur '{user}' a déjà été saisi. Veuillez saisir un autre film.")
               
                        
        if  len(users) == total_users and len(movies) == total_movies:
        
            data_frames = pd.DataFrame(columns = users, index=movies)
            
            st.subheader(":blue[Editer le tableau ci-dessous pour mettre les notes des utilisateurs pour les films.]")
            
            data_frames = st.data_editor(data_frames)
        
    elif selected_option == "Télécharger un fichier CSV":
        
        st.subheader(":blue[Importation de fichier csv.]")
        file = st.file_uploader("Importer le fichier CSV", type="csv")
        
        if file is not None:
        
            data_frames = pd.read_csv(file, index_col=0)
            
            st.subheader(":blue[Afficher le data frame crée.]")

            st.dataframe(data_frames)
        
    
    if (len(users) == total_users and len(movies) == total_movies) or file is not None:
        
        top_n = st.number_input(
            'Quel est le top n que l\'on doit on prendre en compte? ' ,
            step=1, 
            format="%d",
            min_value=1,
            max_value=total_movies,
            value=3
        )
        
        button_data_filled = st.button("Recharger le dataframe avec les nouvelles valeur")

        if button_data_filled:
            
            data_frames = data_frames.applymap(convert_to_numeric)

            st.subheader(":blue[Affichage du tableau complété]")
            
            for index, row in data_frames.iterrows():
                for user in data_frames.columns:
                    value = row[user]
                    if isnan(value):
                        movie = index
                        note_u_f = predict_rating(user, movie, data_frames, top_n)
                        data_frames.at[movie, user] = note_u_f
            
            st.session_state.data_frames = data_frames
        
        if 'data_frames' in st.session_state:
            
                dt = st.session_state.data_frames
                st.dataframe(dt)
                
                st.subheader(":blue[Prédire la note d'un utilisateur pour lui recommander un film.]")                
                user_selected = st.selectbox("Choisir l'utilisateur: ", data_frames.columns, key=f"user_selected_{uuid.uuid4()}")
                movie_selected = st.selectbox("Choisir le film: ", data_frames.index, key=f"movie_selected_{uuid.uuid4()}")
                
                st.write(f"La note de {user_selected} sur le film {movie_selected} est **:green[{dt.loc[movie_selected, user_selected]}]**")
                    
                
        
if __name__ == "__main__":
    main()