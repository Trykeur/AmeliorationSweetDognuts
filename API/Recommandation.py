import MathFunction as mathF
from numpy import nan as NaN
from pandas import merge as pd_merge
import re

from Profil import Profil
from MathFunction import distance
import pandas as pd
from mca import MCA

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sb

import time

# pd.options.mode.chained_assignment = None  # default='warn'


"""---------------------------------------- USER BASED ----------------------------------------"""

def UserBased_Vecteur(GENRE,MOVIE,MOVIE_PROFIL,ID_OEUVRE,ratingMin=5,seuilScore=0.4):
    MOVIE_GENRE = MOVIE[['id_oeuvre','id_genre_list']]
    
    def Vecteur_Genre(GENRE,MOVIE_GENRE,MovieList):
        dfTemp = MovieList.groupby(by=["id_oeuvre"])
        RATING_LIST = {group: dfTemp.get_group(group)['rating'].mean() for group in dfTemp.groups.keys()}
        
        # MATRICE_VECTEUR_GENRE modele : [ {'id_oeuvre' : <ID> , 'vecteur' : [0,1,0,1,1,...] , 'genres' : ['drama',...]} ]
        vecteur = [0 for i in range(len(GENRE))]
        MATRICE_VECTEUR_GENRE = {id_oeuvre : vecteur for id_oeuvre in dfTemp.groups.keys()}
        
        for id_oeuvre in MATRICE_VECTEUR_GENRE.keys():
            listGenre_ID = list(MOVIE_GENRE.loc[MOVIE_GENRE['id_oeuvre'] == id_oeuvre]['id_genre_list'].values)
            MATRICE_VECTEUR_GENRE[id_oeuvre] = [1 if(genre in listGenre_ID) else 0 for genre in GENRE.keys()]
        
        return MATRICE_VECTEUR_GENRE,RATING_LIST


    def Result(MatriceVecteur,RatingList,VecteurMovie,seuilScore):
        result= []
        for id_oeuvre in MatriceVecteur.keys():
            score = mathF.Sim_euclidienne(VecteurMovie,MatriceVecteur[id_oeuvre])
            if(score >= seuilScore): result.append({'id_oeuvre':id_oeuvre,'score':score*100})
        
        result.sort(reverse = True,key = lambda movie: (movie['score'],RatingList[movie['id_oeuvre']]))
        
        recommandation = []
        for movie_res in result:
            movie_info = MOVIE.loc[MOVIE['id_oeuvre'] == movie_res['id_oeuvre']]
            movie_info.replace(NaN, None,inplace=True)
            movie_info.drop(['id_genre_list'], axis=1,inplace=True)
            movie_info.rename(columns={'genre_name_list': 'genres'},inplace=True)

            score = mathF.truncate(movie_res['score'],3)
            recommandation.append({'score':score,'movie':movie_info.to_dict('records')[0]}) 
        
        return recommandation

    # List of movie genre of this Movie (Movie With 'ID_OEUVRE')
    GENRE_LIST_MOVIE = list(MOVIE_GENRE.loc[MOVIE_GENRE['id_oeuvre'] == ID_OEUVRE]['id_genre_list'].values)[0]
    
    # List of user who see this movie and note greater or equal than 'ratingMin'
    USER_LIST_MOVIE = list(MOVIE_PROFIL.loc[(MOVIE_PROFIL['id_oeuvre'] == ID_OEUVRE) & (MOVIE_PROFIL['rating'] >= ratingMin)].drop_duplicates(subset='id_profil')['id_profil'].values)
    
    # List of movie see by an user in 'USER_LIST_MOVIE' (movies except this)
    USER_MOVIE_LIST = MOVIE_PROFIL.loc[(MOVIE_PROFIL['id_oeuvre'] != ID_OEUVRE) & (MOVIE_PROFIL['id_profil'].isin(USER_LIST_MOVIE)) & (MOVIE_PROFIL['rating'] >= 5) ][['id_oeuvre','rating']]
    
    # Make a vecteur of this Movie
    VECTEUR_MOVIE = [1 if(id_genre in GENRE_LIST_MOVIE) else 0 for id_genre in GENRE.keys()]
    
    MATRICE_VECTEUR_GENRE,RATING_LIST = Vecteur_Genre(GENRE,MOVIE_GENRE,MovieList=USER_MOVIE_LIST)

    return Result(MATRICE_VECTEUR_GENRE,RATING_LIST,VECTEUR_MOVIE,seuilScore)






"""---------------------------------------- ITEM BASED ----------------------------------------"""
def RecommandationByProfil(MOVIE, MOVIE_PROFIL, MOVIE_ARTIST, ARTIST, GENRE, MOVIE_GENRE, ID_PROFIL):
    # Selection des artistes

    artist_join_3 = pd_merge(ARTIST, MOVIE_ARTIST,how="inner",on="id_artist").replace(NaN, None)
    movie_join_3 = pd_merge(artist_join_3, MOVIE,how="inner",on="id_oeuvre").replace(NaN, None)
    movie_profil_join_3 = pd_merge(movie_join_3, MOVIE_PROFIL[MOVIE_PROFIL["id_profil"] == ID_PROFIL],how="inner",on="id_oeuvre").replace(NaN, None)
    enjoyed_artist_df = movie_profil_join_3["id_artist"]

    # Requette principale (récupération des films joints aux artistes)
    movies_join_1 = pd_merge(MOVIE, MOVIE_ARTIST,how="inner",on="id_oeuvre").replace(NaN, None)
    artist_join_1 = pd_merge(movies_join_1, ARTIST[ARTIST["id_artist"].isin(enjoyed_artist_df.array)],how="inner",on="id_artist").replace(NaN, None)
    
    movie_artist_df = artist_join_1[["id_oeuvre", "english_title", "profession", "primary_name"]]
    movie_artist_df.rename(columns={"id_oeuvre": "id_oeuvre_original"}, inplace=True) # Etape obligatoire pour la fonction RecommandationItemBased() cet alais était inclus pour renommer la colonne oeuvre.id_oeuvre
    
    # Requette de récupération des genres associés aux films
    movies_join_2 = pd_merge(MOVIE, MOVIE_ARTIST,how="inner",on="id_oeuvre").replace(NaN, None)
    artist_join_2 = pd_merge(movies_join_2, ARTIST[ARTIST["id_artist"].isin(enjoyed_artist_df.array)],how="inner",on="id_artist").replace(NaN, None)
    movie_genre_join_2 = pd_merge(artist_join_2, MOVIE_GENRE,how="inner",on="id_oeuvre").replace(NaN, None)
    genre_join_2 = pd_merge(movie_genre_join_2, GENRE,how="inner",on="id_genre").replace(NaN, None)

    genre_movie_df = genre_join_2.drop_duplicates(subset = ["id_oeuvre", "genre_name"])[["id_oeuvre", "genre_name"]]
    genre_movie_df.reset_index(drop=True, inplace=True)
    genre_movie_df.rename(columns={"id_oeuvre": "id_oeuvre_original"}, inplace=True)

    # Selection des films regardés et notés par l'utilisateur
    oeuvre_join_4 = pd_merge(MOVIE, MOVIE_PROFIL[MOVIE_PROFIL["id_profil"] == ID_PROFIL],how="inner",on="id_oeuvre").replace(NaN, None)
    watched_movie_df = oeuvre_join_4[["id_oeuvre", "rating"]]
    
    data = {"movie_artist": movie_artist_df, "genre_movie": genre_movie_df, "enjoyed_artist": enjoyed_artist_df, "watched_movie": watched_movie_df}

    return RecommandationItemBased(ID_PROFIL, data)


# Création du profil
def RecommandationItemBased(profil_id, data):
    profil = Profil(int(profil_id), data["enjoyed_artist"], data["watched_movie"])

    # Compte du nombre de colonne nécessaire pour les artistes de chaque profession

    nbMaxProfession = {}
    nbProf = {}
    currentId = 0


    for i in range(len(data["movie_artist"])):
        if currentId != data["movie_artist"]["id_oeuvre_original"][i]:

            for keyA, valueA in nbProf.items():
                if keyA not in nbMaxProfession:
                    nbMaxProfession[keyA] = 0

                if valueA > nbMaxProfession[keyA]:
                    nbMaxProfession[keyA] = valueA


            nbProf = {}
            currentId = data["movie_artist"]["id_oeuvre_original"][i]


        if data["movie_artist"]["profession"][i] not in nbProf:
            nbProf[data["movie_artist"]["profession"][i]] = 0
        
        nbProf[data["movie_artist"]["profession"][i]] += 1


    # Compte du nombre de colonne necessaires pour les genres

    nbMaxGenre = 0
    nbGenre = 0
    currentId = 0

    for i in range(len(data["genre_movie"])):
        if currentId != data["genre_movie"]["id_oeuvre_original"][i]:
            currentId = data["genre_movie"]["id_oeuvre_original"][i]
            nbGenre = 0

        nbGenre += 1

        if nbGenre > nbMaxGenre:
            nbMaxGenre = nbGenre


    # Creation de la structure du Dataframe

    blanckLine = pd.DataFrame({"id_oeuvre_original": ["0"], "primary_name": [""], "watched_movie": ["False"], "english_title": [""]})


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

    for j in range(len(data["movie_artist"])):
        if currentId != data["movie_artist"]["id_oeuvre_original"][j]:
            currentId = data["movie_artist"]["id_oeuvre_original"][j]

            i += 1

            newLine = blanckLine.copy()

            newLine["id_oeuvre_original"][0] = str(data["movie_artist"]["id_oeuvre_original"][j])
            newLine["english_title"][0] = str(data["movie_artist"]["english_title"][j])
            newLine.index = [len(df)]

            df = pd.concat([df, newLine], ignore_index=False)
            
            nbProfTemp = {}


        if data["movie_artist"]["profession"][j] not in nbProfTemp:
            nbProfTemp[data["movie_artist"]["profession"][j]] = 0

        nbProfTemp[data["movie_artist"]["profession"][j]] += 1

        df[data["movie_artist"]["profession"][j] + " " + str(nbProfTemp[data["movie_artist"]["profession"][j]])][i] = data["movie_artist"]["primary_name"][j]
        
    del i


    ## Ajout des genres

    current_id_oeuvre = 0
    n_genre = 1

    for i in range(len(data["genre_movie"])):
        if data["genre_movie"]["id_oeuvre_original"][i] != current_id_oeuvre:
            current_id_oeuvre = data["genre_movie"]["id_oeuvre_original"][i]
            n_genre = 1

        for j in range(len(df)):
            if df["id_oeuvre_original"][j] == current_id_oeuvre:
                df["Genre " + str(n_genre)][j] = data["genre_movie"]["genre_name"][i]

        n_genre += 1


    ## Ajout des visionnages

    movie_profil = profil.get_movies()
    watched_movies = movie_profil.keys()

    for i in range(len(df)):
        if int(df["id_oeuvre_original"][i]) in watched_movies:
            df["watched_movie"][i] = "True"


    # Génération de l'ACM

    MCA_array = pd.DataFrame(pd.get_dummies(df))
    MCA_fig=MCA(MCA_array, benzecri = False)

    movie_with_rate = watched_movies = movie_profil

    ###############

    array_watched_movies = []
    array_unwatched_movies = []

    for i, j, nom in zip(MCA_fig.fs_c()[:,0], MCA_fig.fs_c()[:,1], MCA_array.columns):
        if re.search("^id_oeuvre_original_[1-9]+", nom):
            id_temp = int(re.findall('\d+', nom)[0])

            if id_temp in movie_with_rate.keys():
                array_watched_movies.append({"id": id_temp, "x": i, "y": j, "rating": movie_with_rate[id_temp]})
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
            tabTempDistance.append(distance(I_movie["x"], I_movie["y"], J_movie["x"], J_movie["y"]) * (1/J_movie["rating"]))

        
        array_ranked_movies[I_movie["id"]] = min(tabTempDistance)


    # Création de la recommandation

    recommandation_array = []

    while len(array_ranked_movies) > 0:
        min_distance_temp = min(array_ranked_movies.values())
        id_min_distance_temp = list(array_ranked_movies.keys())[list(array_ranked_movies.values()).index(min_distance_temp)]

        indexOeuvreDf = df.index[df["id_oeuvre_original"] == str(id_min_distance_temp)].to_list()[0]
        
        nomTemp = df["english_title"][indexOeuvreDf]
        recommandation_array.append([id_min_distance_temp, nomTemp, min_distance_temp])

        del array_ranked_movies[id_min_distance_temp]

    return recommandation_array






"""---------------------------------------- ELASTIC SEARCH ----------------------------------------"""

def ElasticSearch(ES, MOVIE, movieID : int):
    def search(titre, listeGenre): #Recherche des oeuvres par rapport au titre et aux genres de l'oeuvre donnée
        res = ES.search(
            index="movie_full",
            query={
                "bool":{
                    "must":[
                        {"match":{"original_title":titre}},
                        {"terms":{
                            "id_genre_list" : listeGenre,
                        }}
                    ]
                }, 
            }       
        )
        return res
    movie = MOVIE.loc[MOVIE['id_oeuvre'] == movieID]
    titre = movie["original_title"].iloc[0]
    genres = movie["id_genre_list"].iloc[0]
    
    resp = search(titre, genres)
    resp = resp['hits']['hits'][1:6]

    rep = []
    for i in range(len(resp)):
        movie = resp[i]['_source']
        movie['genres'] = movie['genre_name_list']
        del movie['id_genre_list']
        del movie['genre_name_list']

        rep.append({
            "score": resp[i]['_score'],
            "movie": resp[i]['_source']
        })
    
    return rep



