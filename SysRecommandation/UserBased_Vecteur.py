import pandas as pd
import sqlalchemy as sql
import matplotlib.pyplot as plt
import numpy as np
import math
import MathFunction as mathF

username='postgres'
password='1234'
host='localhost'
database= 'SAE'

# Connexion
engine = sql.create_engine(f'postgresql://{username}:{password}@{host}/{database}')


# ---------------------------------------- CHARGEMENT DU JEU DE DONNEE ----------------------------------------
with engine.connect() as connection :
    GENRE_LIST = pd.read_sql_query(sql.text(f"SELECT id_genre,genre_name FROM _genre"),connection)[["id_genre","genre_name"]].values
    OEUVRE_NAME = pd.read_sql_query(sql.text(f"""SELECT id_oeuvre,original_title FROM _movie """),connection)
    MOVIE_LIST = pd.read_sql_query(sql.text(f"""SELECT id_profil,_Profil_Oeuvre.id_oeuvre,id_genre,rating FROM _Profil_Oeuvre
                                            LEFT JOIN _oeuvre_genre ON _oeuvre_genre.id_oeuvre = _Profil_Oeuvre.id_oeuvre"""),connection)
    connection.commit()

GENRE_LIST = {GENRE_LIST[i][0]: GENRE_LIST[i][1] for i in range(len(GENRE_LIST))}

GENRE_LIST_ID = {id_genre: 0 for id_genre in GENRE_LIST.keys()}
cpt = 0
for k in GENRE_LIST_ID.keys():
    GENRE_LIST_ID[k] = cpt
    cpt+=1

def Vecteur_Genre(df_genre):
    dfTemp = df_genre.groupby(by=["id_oeuvre"])
    RATING_LIST = {group: dfTemp.get_group(group)['rating'].max() for group in dfTemp.groups.keys()}

    MATRICE_VECTEUR_GENRE = [[None]+[[0 for i in range(len(GENRE_LIST))]]+[[]] for j in range(len(dfTemp.groups.keys()))]
    cpt = 0
    for group in dfTemp.groups.keys():
        MATRICE_VECTEUR_GENRE[cpt][0] = group
        
        for genre in dfTemp.get_group(group)['id_genre']:
            MATRICE_VECTEUR_GENRE[cpt][1][GENRE_LIST_ID[genre]] = 1
            MATRICE_VECTEUR_GENRE[cpt][2].append(GENRE_LIST[genre])
        cpt+=1
    return MATRICE_VECTEUR_GENRE,RATING_LIST

def Result(MatriceVecteur,RatingList,VecteurMovie,seuil=0.4):
    RESULTAT= []
    for movie in MatriceVecteur:
        res = mathF.Sim_euclidienne(VecteurMovie,movie[1])
        if(res >= seuil): RESULTAT.append([movie[0],res*100,movie[2]])

    RESULTAT.sort(reverse = True,key = lambda i: (i[1],RatingList[i[0]]))
    return RESULTAT

# ---------------------------------------- RESULTAT ----------------------------------------
print('\nEnter a Movie ID: (or STOP)')
ID_OEUVRE = input()
STOP = "STOP"

while (ID_OEUVRE != STOP):
    ID_OEUVRE = int(ID_OEUVRE)
    # Search Movies
    GENRE_LIST_MOVIE = list(MOVIE_LIST.loc[MOVIE_LIST['id_oeuvre'] == ID_OEUVRE].drop_duplicates(subset='id_genre')['id_genre'].values)
    USER_LIST_MOVIE = MOVIE_LIST.loc[(MOVIE_LIST['id_oeuvre'] == ID_OEUVRE) & (MOVIE_LIST['rating'] >= 5)].drop_duplicates(subset='id_profil')['id_profil']
    USER_MOVIE_LIST = MOVIE_LIST.loc[(MOVIE_LIST['id_oeuvre'] != ID_OEUVRE) & (MOVIE_LIST['id_profil'].isin(USER_LIST_MOVIE)) & (MOVIE_LIST['rating'] >= 5) ][['id_oeuvre','id_genre','rating']]
    VECTEUR_MOVIE = [1 if(i in GENRE_LIST_MOVIE) else 0 for i in range(len(GENRE_LIST))]

    MATRICE_VECTEUR_GENRE,RATING_LIST = Vecteur_Genre(USER_MOVIE_LIST)
    result = Result(MATRICE_VECTEUR_GENRE,RATING_LIST,VECTEUR_MOVIE)

    # Show Result
    name = OEUVRE_NAME.loc[OEUVRE_NAME['id_oeuvre'] == ID_OEUVRE]["original_title"].iloc[0]
    print(f"----- MOVIE N°{ID_OEUVRE} : {name} - {[GENRE_LIST[id_genre] for id_genre in GENRE_LIST_MOVIE]} -----\n")

    N = 8
    cpt = 1
    for movie in result[0:N]:
        name = OEUVRE_NAME.loc[OEUVRE_NAME['id_oeuvre'] == movie[0]]["original_title"].iloc[0]
        print(f'{cpt}. FILM N°{movie[0]} : \t{mathF.truncate(movie[1],4)} % / {RATING_LIST[movie[0]]}/10\t-- {name}\t{movie[2]}')
        cpt+=1
    
    print('\nEnter a Movie ID: (or STOP)')
    ID_OEUVRE = input()
