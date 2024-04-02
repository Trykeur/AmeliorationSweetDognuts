import pandas as pd
from mca import MCA

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sb
import re

from profil import Profil
from fonctions import *


pd.options.mode.chained_assignment = None  # default='warn'


# Création du profil

def recommandation(profil_id):
    profil = Profil(int(profil_id))

    # Sélection des films avec les artistes

    appreciated_artists = profil.get_artists_to_request()

    request = """SELECT _oeuvre.id_oeuvre AS idoeuvre, english_title, profession, primary_name FROM _oeuvre 
    INNER JOIN _oeuvre_artist ON _oeuvre.id_oeuvre = _oeuvre_artist.id_oeuvre 
    INNER JOIN _artist ON _oeuvre_artist.id_artist = _artist.id_artist 
    WHERE _artist.id_artist IN (""" + appreciated_artists + ");"

    engine = get_engine()
    mo_req = pd.read_sql(request, engine)

    # Sélection des genres de films

    """SELECT DISTINCT ON (_oeuvre.id_oeuvre, genre_name) _oeuvre.id_oeuvre AS idoeuvre, genre_name FROM _oeuvre 
    INNER JOIN _oeuvre_artist ON _oeuvre.id_oeuvre = _oeuvre_artist.id_oeuvre 
    INNER JOIN _artist ON _oeuvre_artist.id_artist = _artist.id_artist 
    INNER JOIN _oeuvre_genre ON _oeuvre.id_oeuvre = _oeuvre_genre.id_oeuvre 
    INNER JOIN _genre ON _oeuvre_genre.id_genre = _genre.id_genre 
    WHERE _artist.id_artist IN (""" + appreciated_artists + ");"

    engine = get_engine()
    mo_ge_req = pd.read_sql(request, engine)


    # Compte du nombre de colonne nécessaire pour les artistes de chaque profession

    nbMaxProfession = {}
    nbProf = {}
    currentId = 0


    for i in range(len(mo_req)):
        if currentId != mo_req["idoeuvre"][i]:

            for keyA, valueA in nbProf.items():
                if keyA not in nbMaxProfession:
                    nbMaxProfession[keyA] = 0

                if valueA > nbMaxProfession[keyA]:
                    nbMaxProfession[keyA] = valueA


            nbProf = {}
            currentId = mo_req["idoeuvre"][i]


        if mo_req["profession"][i] not in nbProf:
            nbProf[mo_req["profession"][i]] = 0
        
        nbProf[mo_req["profession"][i]] += 1


    # Compte du nombre de colonne necessaires pour les genres

    nbMaxGenre = 0
    nbGenre = 0
    currentId = 0

    for i in range(len(mo_ge_req)):
        if currentId != mo_ge_req["idoeuvre"][i]:
            currentId = mo_ge_req["idoeuvre"][i]
            nbGenre = 0

        nbGenre += 1

        if nbGenre > nbMaxGenre:
            nbMaxGenre = nbGenre


    # Creation de la structure du Dataframe

    blanckLine = pd.DataFrame({"idoeuvre": ["0"], "primary_name": [""], "watched_movie": ["False"], "english_title": [""]})


    for keyA, valueA in nbMaxProfession.items():
        for i in range(valueA):
            blanckLine.insert(0, keyA + " " + str(i + 1), "Null " + keyA + " " + str(i + 1))

    for i in range(nbMaxGenre):
        blanckLine.insert(0, "Genre " + str(i + 1), "Null genre " + str(i + 1))

    df = blanckLine.copy().drop([0], axis=0)


    # Remplissage du Dataframe

    currentId = 0
    i = -1

    nbProfTemp = {}


    ## Ajout des lignes et des artistes

    for j in range(len(mo_req)):
        if currentId != mo_req["idoeuvre"][j]:
            currentId = mo_req["idoeuvre"][j]

            i += 1

            newLine = blanckLine.copy()

            newLine["idoeuvre"][0] = str(mo_req["idoeuvre"][j])
            newLine["english_title"][0] = str(mo_req["english_title"][j])
            newLine.index = [len(df)]

            df = pd.concat([df, newLine], ignore_index=False)
            
            nbProfTemp = {}


        if mo_req["profession"][j] not in nbProfTemp:
            nbProfTemp[mo_req["profession"][j]] = 0

        nbProfTemp[mo_req["profession"][j]] += 1

        df[mo_req["profession"][j] + " " + str(nbProfTemp[mo_req["profession"][j]])][i] = mo_req["primary_name"][j]
        
    del i


    ## Ajout des genres

    current_id_oeuvre = 0
    n_genre = 1

    for i in range(len(mo_ge_req)):
        if mo_ge_req["idoeuvre"][i] != current_id_oeuvre:
            current_id_oeuvre = mo_ge_req["idoeuvre"][i]
            n_genre = 1

        for j in range(len(df)):
            if df["idoeuvre"][j] == current_id_oeuvre:
                df["Genre " + str(n_genre)][j] = mo_ge_req["genre_name"][i]

        n_genre += 1


    ## Ajout des visionnages

    watched_movies = profil.get_movies().keys()

    for i in range(len(df)):
        if int(df["idoeuvre"][i]) in watched_movies:
            df["watched_movie"][i] = "True"



    # Génération de l'ACM

    MCA_array = pd.DataFrame(pd.get_dummies(df))
    MCA_fig=MCA(MCA_array, benzecri = False)

    movie_with_rate = watched_movies = profil.get_movies()
    array_watched_movies = []
    array_unwatched_movies = []

    for i, j, nom in zip(MCA_fig.fs_c()[:,0], MCA_fig.fs_c()[:,1], MCA_array.columns):
        if re.search("^idoeuvre_[1-9]+", nom):
            id_temp = int(re.findall('\d+', nom)[0])

            if id_temp in movie_with_rate.keys():
                array_watched_movies.append({"id": id_temp, "x": i, "y": j, "mark": movie_with_rate[id_temp]})
            else:
                array_unwatched_movies.append({"id": id_temp, "x": i, "y": j})

            plt.text(i, j, nom)
            plt.scatter(i,j)

    # plt.show()

    # Classement des films

    array_ranked_movies = {}

    for I_movie in array_unwatched_movies:
        tabTempDistance = []

        for J_movie in array_watched_movies:
            tabTempDistance.append(dis(I_movie["x"], I_movie["y"], J_movie["x"], J_movie["y"]) * (1/J_movie["mark"]))


        array_ranked_movies[I_movie["id"]] = min(tabTempDistance)


    # Création de la recommandation

    recommandation_array = []

    while len(array_ranked_movies) > 0:
        min_distance_temp = min(array_ranked_movies.values())
        id_min_distance_temp = list(array_ranked_movies.keys())[list(array_ranked_movies.values()).index(min_distance_temp)]

        indexOeuvreDf = df.index[df["idoeuvre"] == str(id_min_distance_temp)].to_list()[0]
        
        nomTemp = df["english_title"][indexOeuvreDf]
        recommandation_array.append([id_min_distance_temp, nomTemp, min_distance_temp])

        del array_ranked_movies[id_min_distance_temp]

    return recommandation_array

print(recommandation(1))