import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(layout='wide')

def create_table(num_movies, num_users):
    return pd.DataFrame(0, index=range(1, num_movies+1), columns=range(1, num_users+1))


def calculate_values(data):
    # Calculer la moyenne pour chaque film en fonction du nombre de valeurs non nulles par ligne
    data['Moyenne'] = data.apply(lambda row: row.sum() / row.astype(bool).sum() if row.astype(bool).sum() != 0 else 0, axis=1)
    return data

def calculate_similarity(data):
    num_movies = data.shape[0]  # Nombre de films
    similarities = {}
    for i in range(1, num_movies + 1):
        col_i = data.loc[i]
        for j in range(1, num_movies + 1):
            col_j = data.loc[j]
            non_null_indices = (col_i != 0) & (col_j != 0)
            numerator = ((col_i - data['Moyenne'][i]) * (col_j - data['Moyenne'][j])).loc[non_null_indices].sum()
            denominator = np.sqrt(((col_i - data['Moyenne'][i]) ** 2).loc[non_null_indices].sum()) * np.sqrt(((col_j - data['Moyenne'][j]) ** 2).loc[non_null_indices].sum())
            similarity = numerator / denominator if denominator != 0 else 0
            similarities[(i, j)] = similarity
    return similarities

def calculate_values_with_formula(table_data):
    # Cette fonction va remplir les cellules contenant des zéros avec la formule spécifiée
    
    for film in range(1, 6):
        for user in range(1, 10):
            # Vérifier si la valeur initiale de la cellule était non nulle
            was_non_zero = table_data.loc[film, user] != 0
            
            if table_data.loc[film, user] == 0:
                # Exclure la similitude entre un film et lui-même
                similarity_col = table_data[f"Similitude F{film}"]
                sim_without_self = similarity_col.drop(film)
                
                # Trouver les deux plus grandes similitudes pour le film actuel
                top_similarities = sim_without_self.nlargest(2).copy().values
                indices = sim_without_self.nlargest(2).copy().index
                
                # Utiliser les indices des films correspondant aux deux plus grandes similitudes pour calculer la nouvelle valeur de la cellule
                new_value = (top_similarities[0] * table_data.loc[indices[0], user] + 
                             top_similarities[1] * table_data.loc[indices[1], user]) / (top_similarities[0] + top_similarities[1])
                
                # Arrondir la nouvelle valeur à deux décimales
                table_data.loc[film, user] = round(new_value, 2)
            
    return table_data



def main():
    st.title("Systeme de récommandation")

    st.title("Parametrage")

    num_movies = st.number_input("Nombre de films :", min_value=1, step=1)
    num_users = st.number_input("Nombre d'utilisateurs :", min_value=1, step=1)

    table_data = create_table(num_movies, num_users)

    for i in range(num_movies):
        row_widgets = st.columns(num_users)
        for j in range(num_users):
            with row_widgets[j]:
                cell_value = st.text_input(f"F{i+1}, U{j+1}", key=f"{i}-{j}", value=str(table_data.loc[i+1, j+1]))

                table_data.loc[i+1, j+1] = int(cell_value) if cell_value else 0

    if st.button("Prédire les cases vides"):
        table_data = calculate_values(table_data)
        similarities = calculate_similarity(table_data)

        for film in range(1, num_movies + 1):
            col_name = f"Similitude F{film}"
            table_data[col_name] = [similarities.get((film, f), 0) for f in range(1, num_movies + 1)]
        
        table_data = calculate_values_with_formula(table_data)
    
    # Afficher le tableau
    st.write(table_data)

if __name__ == "__main__":
    main()
