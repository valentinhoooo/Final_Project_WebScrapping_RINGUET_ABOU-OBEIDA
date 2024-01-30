import streamlit as st
import pandas as pd
import pydeck as pdk

df_animals = pd.read_csv(r'C:\Users\valen\Documents\PORTABLE TD A5S1\Webscrap\datasetfinal.csv')

# Page d'accueil avec la liste des animaux
def home_page():
    st.title("Liste des Animaux")
    for index, row in df_animals.iterrows():
        # Ratios de colonnes pour contrôler la largeur des images et du texte
        col1, col2, col3 = st.columns([3, 1, 5])  
        with col1:
            image_url = row['Image_URL']
            if isinstance(image_url, str) and "https" in image_url:
                st.image(image_url, width=300)  
        with col2:
            # Colonne est utilisée comme espace entre l'image et le texte
            st.write("")  
        with col3:
            st.subheader(row['name'])  # Augmentation de la taille du texte
            if st.button('Voir plus', key=str(index)):
                st.session_state['selected_animal_index'] = index
                st.session_state['current_page'] = 'details'

df_cleaned = df_animals.copy()

# Supprimer les lignes avec des valeurs non désirées dans "Zone"
df_cleaned = df_cleaned[~df_cleaned['Zone'].isin(['Texte non trouvé', '', pd.NA, 'nan', 'NaN', None , "None"])]
df_cleaned.dropna(subset=['Zone'], inplace=True)

def map_page():
    st.title("Carte des Animaux par Zone Géographique")
    st.text("On affiche uniquement les zones avec des animaux en danger.")

    
    # Dictionnaire de correspondance des zones à leurs coordonnées géographiques.
    zone_to_coords = {
        'Océanie': [-25.274398, 133.775136],
        'Afrique': [-8.783195, 34.508523],
        'Europe': [54.5260, 15.2551],
        'Amérique du Nord': [54.5260, -105.2551],
        'Amérique du Sud': [-8.783195, -55.491477],
        'Asie': [34.047863, 100.619655],
        'Océan Atlantique': [0.0000, -30.0000],
        'Océan Arctique': [90.0000, 0.0000],
        'Eurasie': [55.0000, 60.0000],
        'Amérique Centrale': [8.7832, -80.7821],
        'Asie du Sud-est': [-8.3405, 115.0920],
        'Îles Galapagos': [-0.3832, -90.4233],
        'Australie': [-25.274398, 133.775136],
        'Île de Madagascar': [-18.766947, 46.869107],
        'Antarctique': [-82.862752, 135.0000],
        'Pacifique Nord': [45.0000, -140.0000],
        'Atlantique Nord': [45.0000, -40.0000],
        'Alpes': [47.368650, 9.702580],
        'Chine': [35.861660, 104.195397],
        'Sud Afrique': [-30.559482, 22.937506],
        'Nord Afrique Subsaharienne': [17.607789, -8.081666],
        'Est Afrique': [9.145, 40.489673],
        'Afrique Subsaharienne': [-8.783195, 34.508523],
        'Sud-Est Afrique': [-20.348404, 34.907574],
        'Océan Pacifique Nord': [0.0000, -135.0000],
        'Océan Mondial': [0.0000, 0.0000],
    }

    # Dictionnaire de nettoyage pour les valeurs de la colonne 'Zone'.
    zone_mapping = {
    'Océanie.': 'Océanie',
    'Océanie,': 'Océanie',
    '’Océanie': 'Océanie',
    'Amérique du Nord ': 'Amérique du Nord',
    ' Amérique du Nord': 'Amérique du Nord',
    'Amérique du Sud ': 'Amérique du Sud',
    ' Amérique du Sud': 'Amérique du Sud',
    'Amérique du Sud.': 'Amérique du Sud',
    'Asie ': 'Asie',
    'Asie.': 'Asie',
    'Asie du Sud-est': 'Asie du Sud-est',
    'Asie du Sud Est': 'Asie du Sud-est',
    'Asie du Sud Est.': 'Asie du Sud-est',
    'Asie de l’Est.': 'Asie',
    'Afrique.': 'Afrique',
    'Afrique ': 'Afrique',
    'sud de l’Afrique': 'Sud Afrique',
    'nord de l’Afrique Subsaharienne': 'Nord Afrique Subsaharienne',
    'Afrique de l’Est': 'Est Afrique',
    'Afrique Subsaharienne.': 'Afrique Subsaharienne',
    'Afrique du Sud-Est': 'Sud-Est Afrique',
    'océan Atlantique': 'Océan Atlantique',
    'Atlantique': 'Océan Atlantique',
    'océan Arctique': 'Océan Arctique',
    'Arctique': 'Océan Arctique',
    'Pacifique Nord': 'Océan Pacifique Nord',
    'île de Madagascar': 'Île de Madagascar',
    ' l’île de Madagascar': 'Île de Madagascar',
    '’île de Madagascar': 'Île de Madagascar',
    'îles Galapagos': 'Îles Galapagos',
    'Eurasie': 'Eurasie',
    'Europe.': 'Europe',
    'Europe de l’Ouest': 'Europe',
    'Antarctique': 'Antarctique',
    'Alpes': 'Alpes',
    'Chine': 'Chine',
    'tous les océans': 'Océan Mondial'
    }


    df_cleaned['Zone'] = df_cleaned['Zone'].replace(zone_mapping)
    df_cleaned['coords'] = df_cleaned['Zone'].apply(zone_to_coords.get)

    # Filtrage des données pour exclure les zones inconnues ou non mappées.
    df_mapped_animals = df_cleaned.dropna(subset=['coords'])
    df_mapped_animals = df_mapped_animals[df_mapped_animals['coords'].notnull()]
    df_mapped_animals[['longitude', 'latitude']] = pd.DataFrame(df_mapped_animals['coords'].tolist(), index=df_mapped_animals.index)

    valid_vulnerabilities = ['Least Concern', 'Aucun résultat', 'Data Deficient']
    df_mapped_animals = df_mapped_animals[df_mapped_animals['Vulnerability'].isin(valid_vulnerabilities)]

    # Couche pour PyDeck
    layer = pdk.Layer(
        'ScatterplotLayer',
        df_mapped_animals,
        get_position=['longitude', 'latitude'],  # Utiliser les colonnes 'longitude' et 'latitude'
        get_color='[200, 30, 0, 160]',
        get_radius=50000,
    )

    # état initial de la vue de la carte.
    view_state = pdk.ViewState(latitude=0, longitude=0, zoom=1)

    # Affichage de la carte.
    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state))

    st.text("Les Zones les plus à l'Est et à l'Ouest ne sont malheureusement pas affichées")
    st.text("donc nous affichons la liste complète du nombre d'animaux menacés par Zone:")
    st.title("Nombre d'animaux grandement menacés par Zone ")

    # Affichage de la liste complète du nombre d'animaux par Zone et du nombre total d'animaux menacés
    st.write(f"Nombre total d'animaux menacés scrappés : 148 ")
    animals_by_zone = df_mapped_animals.groupby('Zone').size().reset_index(name='Nombre d\'animaux menacés')
    st.dataframe(animals_by_zone,width=800,height=700)

def animal_page(index):
    animal = df_animals.iloc[index]
    st.title(animal['name'])
    
    col1, col2 = st.columns([2, 3])
    with col1:
        st.image(animal['Image_URL'], use_column_width=True)
    with col2:
        st.markdown(f"**Nom Latin:** {animal['Nom latin']}")
        st.markdown(f"**Règne:** {animal['Règne']}")
        st.markdown(f"**Embranchement:** {animal['Embranchement']}")
        st.markdown(f"**Classe:** {animal['Classe']}")
        st.markdown(f"**Ordre:** {animal['Ordre']}")
        st.markdown(f"**Famille:** {animal['Famille']}")
        st.markdown(f"**Genre:** {animal['Genre']}")
        st.markdown(f"**Espèce:** {animal['Espèce']}")
        st.markdown(f"**Zone Géographique:** {animal['Zone']}")

        # Mise en évidence de la vulnérabilité avec différentes couleurs
        vulnerability = animal['Vulnerability']
        color = 'white'  

        if vulnerability in ['Endangered', 'Critically Endangered']:
            color = 'red'
        elif vulnerability in ['Near Threatened', 'Vulnerable', 'Lower Risk/conservation dependent']:
            color = 'orange'

        st.markdown(f"<span style='color: {color}'>**Statut de conservation:** {vulnerability}</span>", unsafe_allow_html=True)

        st.write("Légende des couleurs du statut de conservation:")
        st.write("- Rouge: En danger ou En danger critique")
        st.write("- Orange: Quasi menacé, Vulnérable ou Menacé")
        st.write("- Blanc: Préoccupation mineure ou Données insuffisantes")


def main():
    st.sidebar.title("Navigation")

    # Initialisation des états de session si nécessaire
    if 'current_page' not in st.session_state:
        st.session_state['current_page'] = 'home'
    if 'selected_animal_index' not in st.session_state:
        st.session_state['selected_animal_index'] = None

    # Choix de la page dans la sidebar
    page_choice = st.sidebar.radio(
        "Choisissez une page :",
        ["Page d'accueil", "Carte des Animaux"],
        index=0 if st.session_state['current_page'] == 'home' else 1
    )

    # Bouton pour appliquer le choix de la page
    apply_button = st.sidebar.button("Appliquer")

    if apply_button:
        if page_choice == "Page d'accueil":
            st.session_state['current_page'] = 'home'
            st.session_state['selected_animal_index'] = None
        elif page_choice == "Carte des Animaux":
            st.session_state['current_page'] = 'map'

        st.rerun()

    if st.session_state['current_page'] == 'home':
        home_page()
    elif st.session_state['current_page'] == 'map':
        map_page()
    elif st.session_state['selected_animal_index'] is not None:
        animal_page(st.session_state['selected_animal_index'])
if __name__ == "__main__":
    main()


#python -m streamlit run "C:\Users\valen\Documents\PORTABLE TD A5S1\Webscrap\streamlit.py"
