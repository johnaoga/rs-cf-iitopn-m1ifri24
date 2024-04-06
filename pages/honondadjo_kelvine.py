import streamlit as st
import numpy as np
import pandas as pd
import math

def similarite(x, y):
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

def note(user, film, data, n = 3) -> float:
    if math.isnan(float(data.loc[film, user])):
        x = np.array(data.loc[film])

        similarities = {}
        for key, value in data.iterrows():
            if key != film:
                sim = similarite(x, value.values)
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
            if math.isnan(float(data.loc[key,user])):
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
        

def main():
    st.title("Système de Recommandation de Films")

    option = st.selectbox(" Selectionner le systeme de filtrage ", 
    ["Personnalisation", "Téléversement"])

    if option == "Personnalisation" :
        st.markdown("<h4 style='font-weight:bold; color:#red;'>Formulaire</h4>", unsafe_allow_html=True)
        nbre_user = st.number_input('Entrer le nombre d\'utilisateurs : ', min_value=3, step=1)
        nbre_film = st.number_input('Entrer le nombre de films : ', min_value=3, step=1)

        users, films = [], []
        st.markdown("<h4 style='font-weight:bold;'>Insertion des utilisateurs</h4>", unsafe_allow_html=True)
        for i in range(int(nbre_user)):
            u = st.text_input(f"Nom de l'utilisateur {i+1}: ", key=f"user_{i}")
            users.append(u)

        st.markdown("<h4 style='font-weight:bold;'>Insertion des films</h4>", unsafe_allow_html=True)
        for j in range(int(nbre_film)):
            f = st.text_input(f"Nom du film {j+1}: ", key=f"film_{j}")
            films.append(f)
        
        empty_users = [value for value in users if value == '']
        
        
        
        empty_films = [index for index in films if index == '']

        if not empty_users and not empty_films: 
            data = pd.DataFrame(
                columns=users,
                index=films
            )

            st.markdown("<h4 style='font-weight:bold;'>Création du tableau vide</h4>", unsafe_allow_html=True)
            st.dataframe(data)
            
            st.markdown("<h4 style='font-weight:bold;'>Insertion de certaines notes</h4>", unsafe_allow_html=True)
            for index, row in data.iterrows():
                for user in data.columns:
                    film = index
                    cel = st.selectbox(f"Choisir la note de l'utilisateur {user} pour le film {film}: ", ['Pas de note',1,2,3,4,5], key=f"select_{index}_{user}") 
                    if cel == 'Pas de note':
                        cell = float('nan')
                    else:
                        cell = float(cel)
                    data.loc[film, user] = cell

            st.write("Les notes des utilisateurs sur quelques films")
            st.dataframe(data)

            n = st.number_input("Entrer le n du top n:", min_value=1, step=1, format="%d")

            button_data_filled = st.button("Actualiser le tableau complété")
      
            if button_data_filled:
                
                st.markdown("<h4 style='font-weight:bold;'>Affichage du tableau complété</h4>", unsafe_allow_html=True)
                for index, row in data.iterrows():
                    for user in data.columns:
                        value = row[user]
                        if math.isnan(value):
                            film = index
                            note_u_f = note(user, film, data,n)
                            data.loc[film, user] = note_u_f

                st.write("Le tableau complété est le suivant: ")        
                
                st.session_state.data = data
            
            if 'data' in st.session_state:
                dt = st.session_state.data
                st.dataframe(dt)
                
                st.markdown("<h4 style='font-weight:bold;'>Affichage de la note d'un utilisateur sur un film spécifique</h4>", unsafe_allow_html=True)
                    
                user_choice = st.selectbox("Choisir l'utilisateur: ", data.columns, key=f"user_choice")
                film_choice = st.selectbox("Choisir le film: ", data.index, key=f"film_choice")
                
                st.write(f"La note de {user_choice} sur le film {film_choice} est **:green[{dt.loc[film_choice, user_choice]}]**")

    elif option == "Téléversement" :

        st.markdown("<h4 style='font-weight:bold;'>Importation de CSV</h4>", unsafe_allow_html=True)
        file = st.file_uploader("Importer le fichier CSV", type="csv")
        
        if file is not None:
            data = pd.read_csv(file, index_col=0)
            st.dataframe(data)
        
            n = st.number_input("Entrer le n du top n:", min_value=1, step=1, format="%d")
            
            button_data_filled = st.button("Actualiser le tableau complété")

            if button_data_filled:
                
                st.markdown("<h4 style='font-weight:bold;'>Affichage du tableau complété</h4>", unsafe_allow_html=True)
                for index, row in data.iterrows():
                    for user in data.columns:
                        value = row[user]
                        if math.isnan(value):
                            film = index
                            note_u_f = note(user, film, data,n)
                            data.loc[film, user] = note_u_f

                st.write("Le tableau complété est le suivant: ")        
                
                st.session_state.dt = data
            
            if 'dt' in st.session_state:
                dt = st.session_state.dt
                st.dataframe(dt)
                
                st.markdown("<h4 style='font-weight:bold;'>Affichage de la note d'un utilisateur sur un film spécifique</h4>", unsafe_allow_html=True)
                    
                user_choice = st.selectbox("Choisir l'utilisateur: ", data.columns, key=f"user_choice")
                film_choice = st.selectbox("Choisir le film: ", data.index, key=f"film_choice")
                
                st.write(f"La note de {user_choice} sur le film {film_choice} est **:green[{dt.loc[film_choice, user_choice]}]**")
    
main()