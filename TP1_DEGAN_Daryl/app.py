import streamlit as st
import pandas as pd 
import os
st.title("Decouvrez nos films et tendances ")
st.title("Films d'actions ")
col1, col2, col3 , col4, col5 = st.columns(5)

with col1:
 st.image('images/un.png', caption='NCIS')
with col2:
 st.image('images/deux.jpg', caption='Into the Badlands')
with col3:
 st.image('images/cinq.png', caption='Damsel')
with col4:
 st.image('images/quatre.png', caption='Madame web')
with col5:
 st.image('images/quinze.png', caption='Night Agent')


st.title("Films d'humour")
col6, col7, col8 , col9, col10 = st.columns(5)
with col6:
 st.image('images/six.jpg', caption='Love')
 with col7:
  st.image('images/sept.jpg', caption='Law')
 with col8:
  st.image('images/huit.jpg', caption='Cols')
with col9:
 st.image('images/neuf.jpg', caption='Friends')
with col10:
 st.image('images/seize.jpg', caption='More')
st.title("Films d'horreurs")
col11, col12, col13 , col14, col15 = st.columns(5)
with col11:
 st.image('images/trois.jpg', caption='Reus')
 with col12:
  st.image('images/quatrieme.jpg', caption='Push')
with col13:
  st.image('images/onze.jpg', caption='Ritter')
with col14:
  st.image('images/douze.jpg', caption='Sam')
with col15:
  st.image('images/treize.jpg', caption='Sweet Rome')
  

# Vérifier si le nombre de films a déjà été initialisé dans la session
if 'num_films' not in st.session_state:
    st.session_state.num_films = 0

# Interface utilisateur Streamlit
st.title('Donnez nous votre appreciation de nos films')

# Liste pour stocker les données des films
films_data = []

# Vérifier si le fichier CSV existe
if 'films_notes.csv' in os.listdir():
    # Lire les données existantes du fichier CSV
    existing_df = pd.read_csv('films_notes.csv')
    # Ajouter les données existantes à la liste
    films_data.extend(existing_df.to_dict(orient='records'))

# Boucle pour permettre à l'utilisateur de saisir plusieurs films
while True:
    # Champ pour le nom de l'utilisateur
    user_name = st.text_input('Votre nom')

    # Champ pour le nom du film avec une clé unique
    film_name = st.text_input(f'Nom du film {st.session_state.num_films}', '')

    # Champ pour la note du film avec une clé unique
    film_rating = st.number_input(f'Votre note concernant le film {st.session_state.num_films}', min_value=0, max_value=10, value=0, step=1)

    # Options pour la catégorie du film
    options = ['Action', 'Humour', 'Horreur']
    film_category = st.radio(f'De quelle catégorie est le film {st.session_state.num_films}', options)

    # Ajouter les données du film à la liste si le nom du film n'est pas vide
    if film_name.strip():
        films_data.append({'Nom de l\'utilisateur': user_name, 'Nom du film': film_name, 'Note': film_rating, 'Catégorie': film_category})

    # Bouton pour ajouter un autre film ou terminer avec une clé unique
    add_another = st.button(f'Ajouter un autre film {st.session_state.num_films}')
    if not add_another:
        break

    # Incrémenter le nombre de films
    st.session_state.num_films += 1

# Convertir la liste des données des films en DataFrame
films_df = pd.DataFrame(films_data)


if not films_df.empty:
    if st.button('Terminer'):
        # Enregistrer les données dans un fichier CSV
        films_df.to_csv('films_notes.csv', index=False)
        st.success('Les données des films ont été enregistrées dans le fichier films_notes.csv avec succès!')
else:
    st.warning('Aucune donnée de film saisie!')

  




