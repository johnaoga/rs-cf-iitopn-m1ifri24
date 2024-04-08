import streamlit as st
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# Setting up the title and header
st.title("Système de Recommandation")
st.header('👨🏾‍💻Travaux Pratique')

# Subheader
st.subheader('Connexion')

# Input for user's name
user_name = st.text_input("Entrez du nom ou pseudo")

# Load data
data = pd.read_csv('data.csv')  
products = ['T-SHIRT', 'Basket', 'Talon', 'NIKE', 'Robe de soirée', 'Robe de plage']

# Function to recommend products
# Return the dictionary of recommended products
def recommend_products():
    # Extracting data of the current user from the dataset based on their name
    user_data = data[data['Nom_utilisateur'] == user_name]

    # Finding similar users based on the cosine similarity of their ratings with the current user
    similar_users = cosine_similarity(user_data.iloc[:, 2:]).argsort()[0][-num_similar_users-1:-1][::-1]  

    # Initializing an empty dictionary to store recommended products and their ratings
    recommended_products = {}

    # Collecting ratings of products from similar users that current user hasn't rated yet.
    # Loop through each similar user
    for user in similar_users:
        # Extract data of similar user from the dataset
        similar_user_data = data[data['Nom_utilisateur'] == data.iloc[user]['Nom_utilisateur']]
        # Iterate through the rows of the similar user's data
        for index, row in similar_user_data.iterrows():
            # Check if the product of this row is not in the user's data
            if row['Produit'] not in user_data['Produit'].values:
                # If the product is not in the recommended list, add it else append its rating
                if row['Produit'] not in recommended_products:
                    recommended_products[row['Produit']] = [row['Note']]
                else:
                    recommended_products[row['Produit']].append(row['Note'])
    
    # Calculate the average rating for each recommended product
    recommended_products = {product: sum(notes) / len(notes) for product, notes in recommended_products.items()} 
    # Sort the recommended products by their average ratings in descending order  
    recommended_products = dict(sorted(recommended_products.items(), key=lambda item: item[1], reverse=True))

    return recommended_products

# Display input for number of similar users
if user_name:
    st.success(f'Vous êtes connecté en tant que {user_name}')
    num_similar_users = st.number_input("Nombre d'utilisateurs similaires à considérer", min_value=1, max_value=5, value=1, step=1)

    # User interface for rating products
    st.info("Vous devez au moins noter deux produits!😎")
    categories = ["Habillement", "Chaussure", "Robe"]
    tab__1 , tab__2 ,tab__3 = st.tabs(categories)

    # Generates UI for users to rate products and saves their ratings.
    # Iterate through tabs for different categories (e.g., "Clothes", "Food")           
    for i, tab_name in enumerate(categories, start=1):
        # Accessing dynamically named variables for each tab
        with locals()[f"tab__{i}"]:
            # Iterate through products within each tab
            for j, product in enumerate(products[i*2-2:i*2], start=1):
                with st.expander(product):
                    # Display product name and image
                    st.header(product)
                    st.image(f"images/{product.lower().replace(' ', '_')}.jpg")
                    note = st.number_input("Saisissez la note pour ce produit si vous êtes intéressé!", min_value=0.0, max_value=5.0, value=0.0, step=1.0, key=product)

                    # Display the rating entered by the user
                    st.write(f"Vous avez saisi : **{int(note)}**")
                    st.write("Nombre d'étoiles : " + '⭐' * int(note))
                    
                    button = st.button('Enregistrer', key=f"cta_{product.lower().replace(' ', '_')}")
                    
                    # If the button is clicked, save the rating to the dataset
                    if button:
                        new_data = pd.DataFrame({'Nom_utilisateur': [user_name], 'Produit': [product], 'Note': [int(note)]})
                        data = pd.concat([data, new_data], ignore_index=True)
                        data.to_csv('data.csv', index=False)
                        st.success('Enrégistrement effectué avec succès')

    # Display user's ratings and recommendations
    if st.button('Voir les notes'):
        table = data.pivot_table(index='Produit', columns='Nom_utilisateur', values='Note', aggfunc='first', fill_value='')
        st.table(table)

    # Displays recommended products if the user clicks the button,
    # or informs the user if no recommendations are available.
    if st.button('Voir les recommandations'):
        recommended_products = recommend_products()
        if recommended_products:
            st.write("Produits recommandés :")
            for product, rating in recommended_products.items():
                st.write(f"{product}: {rating}")
        else:
            st.write("Aucune recommandation disponible pour le moment.")
