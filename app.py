import streamlit as st
import pandas as pd
import math

def main():
    st.title("Système de recommandation")

    # Charger le fichier (XLSX ou CSV)
    uploaded_file = st.file_uploader("Chargez un fichier XLSX ou CSV", type=["xlsx", "csv"])

    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith(".xlsx") else pd.read_csv(uploaded_file)
            st.write("Contenu du fichier :")
            st.dataframe(df)

            df_new = pd.DataFrame()
            df_new["Somme"] = df.apply(lambda row: row.dropna().sum(), axis=1)
            df_new["Total"] = df.apply(lambda row: row.count(), axis=1)
            df_new["Moyenne"] = df_new["Somme"] / df_new["Total"]
                
            for i in range(len(df)):
                resultat = []
                for i2 in range(len(df)):
                    a = 0
                    b = 1
                    b1 = 0
                    b2 = 0
                    for col in range(len(df.columns)):
                        if pd.notna(df.iloc[i, col]) and pd.notna(df.iloc[i2, col]) :
                            difference1 = df.iloc[i, col]-df_new["Moyenne"].iloc[i]
                            difference2 = df.iloc[i2, col]-df_new["Moyenne"].iloc[i2]
                            a += (difference1)*(difference2)
                            b1 += math.pow(difference1, 2)
                            b2 += math.pow(difference2, 2)
                    b *=  math.sqrt(b1)*math.sqrt(b2)
                    resultat.append(a/b)       
                df_new[f"Sim f{i+1}"] = resultat
            
            st.write("Tableau des calculs intermédiares :")
            st.dataframe(df_new)
            
            for i in range(len(df)):
                for j in range(len(df.columns)):
                    a = 0
                    b = 0

                    if pd.isna(df.iloc[i, j]) :
                        filtered_values = df_new[f"Sim f{i+1}"][(df_new[f"Sim f{i+1}"] > 0) & (df_new[f"Sim f{i+1}"] != df_new[f"Sim f{i+1}"][i] )]
                        b = filtered_values.sum()

                        index_rows = filtered_values.index.tolist()
                        for k in range(len(index_rows)) :
                            if pd.notna(df.iloc[index_rows[k], j]) :
                                a += df_new[f"Sim f{i+1}"][index_rows[k]]*df.iloc[index_rows[k], j]
                            else :
                                b -= df_new[f"Sim f{i+1}"][index_rows[k]]
                        df.iloc[i, j] = round(a/b, 0)

            st.write("Tableau avec mis à jour :")
            st.dataframe(df)
            
            st.markdown("---")
            
            st.title("Top n")
            topn = st.number_input("Entrez le n du top n des films", min_value=1, step=1)
            if st.button("Afficher résultat top n"):
                df_sorted = df_new.sort_values(by='Moyenne', ascending=False)
                top_n_indices = df_sorted.index[:topn]
                if (topn > len(df)) :
                    st.write("Le n entré est trop grand")
                st.write("*************** Le top ", str(topn), " des films ***************")
                st.write("Il existe ", str(len(df)), " films numeroté de 1 à ", str(len(df)))
                
                for i in range(len(top_n_indices)):
                    st.write("- Le top n° ", str(i+1), " des films est le film numéro << ", str(top_n_indices[i]+1), " >>")

            st.markdown("---")
            
            st.title("Rechecher une note")
            num_user = st.number_input("Entrez le numero de l'utilisateur", min_value=1, step=1)
            num_films = st.number_input("Entrez le numero du films", min_value=1, step=1)

            if st.button("Afficher résultat recherche"):
                if num_films > len(df) :
                    st.error(f"Il n'existe de film lié au numéro fournir ! ")
                if num_user > len(df.columns) :
                    st.error(f"Il n'existe pas d'utilisateur lié au numéro fournir ! ")

                note = df.iloc[num_films-1, num_user-1]

                st.write("Note : ", str(note))
                if (note > 2) :
                    st.write("Nous vous recommandons ce film ")
                else :    
                    st.write("Nous ne vous recommandons pas ce film ")
            
        except Exception as e:
            st.error(f"Erreur lors de la lecture du fichier : {e}")
    else:
        st.warning("Veuillez charger un fichier pour afficher son contenu.")

if __name__ == "__main__":
    main()
