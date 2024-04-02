import pandas as pd
import sqlalchemy as sql
import matplotlib.pyplot as plt
import numpy as np
import math
import MathFunction as mathF

# ---------------------------------------- CHARGEMENT DU JEU DE DONNEE ----------------------------------------
username='postgres'
password='1234'
host='localhost'
database= 'SAE'

# Connexion
engine = sql.create_engine(f'postgresql://{username}:{password}@{host}/{database}')




with engine.connect() as connection :
	GENRE_LIST = pd.read_sql_query(sql.text(f"SELECT id_genre,genre_name FROM _genre"),connection)[["id_genre","genre_name"]].values	
	OEUVRE_NAME = pd.read_sql_query(sql.text(f"""SELECT id_oeuvre,original_title FROM _movie """),connection)
	OEUVRE_GENRE = pd.read_sql_query(sql.text(f"""SELECT _movie.id_oeuvre,id_genre FROM _movie INNER JOIN _oeuvre_genre ON _movie.id_oeuvre=_oeuvre_genre.id_oeuvre"""),connection)
	connection.commit()

GENRE_LIST = {GENRE_LIST[i][0]: GENRE_LIST[i][1] for i in range(len(GENRE_LIST))}

GENRE_LIST_ID = {id_genre: 0 for id_genre in GENRE_LIST.keys()}
cpt = 0
for k in GENRE_LIST_ID.keys():
    GENRE_LIST_ID[k] = cpt
    cpt+=1

# ---------------------------------------- REQUEST PROFIL----------------------------------------
def ProfilRequest(id_profil): 
    with engine.connect() as connection :
        PROFIL_MOVIE = pd.read_sql_query(sql.text(f"""SELECT _Profil_Oeuvre.id_oeuvre,id_genre FROM _Profil_Oeuvre
                                                    LEFT JOIN _oeuvre_genre ON _oeuvre_genre.id_oeuvre = _Profil_Oeuvre.id_oeuvre
                                                    WHERE id_profil = {id_profil}"""),connection)
        
        PROFIL_GENRE_LIST = pd.read_sql_query(sql.text(f"""SELECT genre_name,COUNT(_oeuvre_genre.id_oeuvre) FROM _Profil_Oeuvre
                                                            LEFT JOIN _oeuvre_genre ON _oeuvre_genre.id_oeuvre = _Profil_Oeuvre.id_oeuvre
                                                            LEFT JOIN _genre ON _genre.id_genre = _oeuvre_genre.id_genre
                                                            WHERE id_profil = {id_profil}
                                                            GROUP BY genre_name"""),connection)[["genre_name","count"]].values
    PROFIL_GENRE_LIST = [[x[0],x[1]]for x in PROFIL_GENRE_LIST]
    PROFIL_GENRE_LIST.sort(reverse = True,key = lambda i: i[1])
    return PROFIL_MOVIE,PROFIL_GENRE_LIST[0:4]


# ---------------------------------------- VECTEUR PROFIL_GENRE ----------------------------------------
def Vecteur_Profil_Genre(df_profil):
    PROFIL_LIST = [] # Movie see by this profil

    dfTemp = df_profil[['id_oeuvre',"id_genre"]].groupby(by=["id_oeuvre","id_genre"]).sample(n=1).groupby(by=["id_oeuvre"])
    VECTEUR_PROFIL_GENRE = [0 for i in range(len(GENRE_LIST))]

    for group in dfTemp.groups.keys():
        PROFIL_LIST.append(group)
        for genre in dfTemp.get_group(group)['id_genre']:
            VECTEUR_PROFIL_GENRE[GENRE_LIST_ID[genre]] += 1
    
    return PROFIL_LIST, VECTEUR_PROFIL_GENRE
    
def Vecteur_Genre(df_genre):
    dfTemp = df_genre.groupby(by=["id_oeuvre"])
    

    MATRICE_VECTEUR_GENRE = [[None]+[[0 for i in range(len(GENRE_LIST))]]+[[]] for j in range(len(dfTemp.groups.keys()))]
    cpt = 0
    for group in dfTemp.groups.keys():
        MATRICE_VECTEUR_GENRE[cpt][0] = group
        
        for genre in dfTemp.get_group(group)['id_genre']:
            MATRICE_VECTEUR_GENRE[cpt][1][GENRE_LIST_ID[genre]] = 1
            MATRICE_VECTEUR_GENRE[cpt][2].append(GENRE_LIST[genre])
        cpt+=1
    return MATRICE_VECTEUR_GENRE

MATRICE_VECTEUR_GENRE = Vecteur_Genre(OEUVRE_GENRE)


# ---------------------------------------- RESULTAT ----------------------------------------
def Result(MatriceVecteur,VecteurProfil,user_list=[],seuil=0.6):
    RESULTAT= []
    for movie in MatriceVecteur:
        if(movie[0] not in user_list):
            res = mathF.Sim_Cos(VecteurProfil,movie[1])
            if(res >= seuil): RESULTAT.append([movie[0],res*100,movie[2]])

    RESULTAT.sort(reverse = True,key = lambda i: i[1])
    return RESULTAT

print('\nEnter a profil ID: (or STOP)')
ProfilID = input()
STOP = "STOP"

while ProfilID != STOP:
    PROFIL,PROFIL_GENRE_LIST = ProfilRequest(int(ProfilID))
    print(f"--- PROFIL N°{ProfilID} {PROFIL_GENRE_LIST}---\n")
    PROFIL_LIST,VECTEUR_PROFIL_GENRE= Vecteur_Profil_Genre(PROFIL)

    result = Result(MATRICE_VECTEUR_GENRE,VECTEUR_PROFIL_GENRE,user_list=PROFIL_LIST)
    N = 8
    cpt = 1
    for movie in result[0:N]:
        name = OEUVRE_NAME.loc[OEUVRE_NAME['id_oeuvre'] == movie[0]]["original_title"].iloc[0]
        print(f'{cpt}. FILM N°{movie[0]} : {mathF.truncate(movie[1],4)} % -- {name}\t{movie[2]}')
        cpt+=1
    
    print('\nEnter a profil ID: (or STOP)')
    ProfilID = input()