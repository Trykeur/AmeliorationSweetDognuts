import pandas as pd
import sqlalchemy as sql
import numpy as np
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

#TODO : Faire un fichier de connection 
username='postgres'
password='admin'
host='localhost'
database= 'Sae'
schema = ""

# HELLO I AM UNDER WATER
# PLEASE HELP ME

# Connexion SQL
print("-- Database connexion ...")
engine = sql.create_engine(f'postgresql://{username}:{password}@{host}/{database}')

# Connexion ElasticSearch
print("-- ElasticSearch connexion ...")
# Prérequis pour ElasticSearch :
# docker run --rm -p 9200:9200 -p 9300:9300 -e "xpack.security.enabled=false" -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch:8.7.0
ES = Elasticsearch("http://localhost:9200")


def initialisationDB():
    print("-- Data initialisation ...")
    with engine.connect() as connection :
        MOVIE_QUERY = """ WITH oeuvre_genre_list AS (
                                SELECT id_oeuvre,array_agg(id_genre) as id_genre_list ,array_agg(genre_name) as genre_name_list FROM oeuvre_genre GROUP BY id_oeuvre
                            )SELECT _movie.id_oeuvre,original_title,english_title,runtime_minutes,num_votes,average_rating,realease_year,id_genre_list,genre_name_list FROM _movie INNER JOIN oeuvre_genre_list on oeuvre_genre_list.id_oeuvre = _movie.id_oeuvre;
                        """
        MOVIE = pd.read_sql_query(sql.text(MOVIE_QUERY),connection)
        GENRE = pd.read_sql_query(sql.text("SELECT id_genre,genre_name FROM _genre"),connection)
        MOVIE_PROFIL = pd.read_sql_query(sql.text("""SELECT * FROM _profil_oeuvre """),connection)
        MOVIE_GENRE = pd.read_sql_query(sql.text("""SELECT * FROM _oeuvre_genre """),connection)
        ARTIST = pd.read_sql_query(sql.text("""SELECT * FROM _artist """),connection)
        MOVIE_ARTIST = pd.read_sql_query(sql.text("SELECT * FROM _oeuvre_artist"),connection) 
        PROFIL = pd.read_sql_query(sql.text("SELECT * FROM _profil"),connection).set_index(['id_client', 'id_profil'])
        CLIENT = pd.read_sql_query(sql.text("SELECT * FROM _client"),connection).set_index('id_client')
    
    

    # conversion + gestion des null
    print("-- Data formating ...")
    MOVIE_ARTIST['movie_characters'] = MOVIE_ARTIST['movie_characters'].str.replace(r'[",\[,\]]', '', regex=True)
    
    ARTIST["birth_year"] = pd.to_numeric(ARTIST["birth_year"],downcast="integer")
    ARTIST["death_year"] = pd.to_numeric(ARTIST["death_year"],downcast="integer")
    ARTIST.replace(np.nan, None,inplace=True)
    
    MOVIE.replace(np.nan, -1,inplace=True)
    MOVIE["runtime_minutes"] = pd.to_numeric(MOVIE["runtime_minutes"],downcast="integer")
    MOVIE["num_votes"] = pd.to_numeric(MOVIE["num_votes"],downcast="integer")
    MOVIE["realease_year"] = pd.to_numeric(MOVIE["realease_year"],downcast="integer")
    MOVIE["average_rating"] = pd.to_numeric(MOVIE["average_rating"],downcast="float")
    MOVIE.replace(-1, None,inplace=True)

    MOVIE_ARTIST.replace(np.nan, None,inplace=True)
    
    connection.commit()

    return GENRE,MOVIE,MOVIE_PROFIL,ARTIST,MOVIE_ARTIST, MOVIE_GENRE, PROFIL, CLIENT


def initialisationCache(MOVIE): 
    MOVIE.replace(np.nan, None,inplace=True)
    # Import des données dans le cache
    bulk_data = []
    for index in MOVIE.index:
        genres = MOVIE.at[index, 'id_genre_list']
        id_oeuvre = MOVIE.at[index, 'id_oeuvre']
        title = MOVIE.at[index, 'original_title']
        runtime = MOVIE.at[index, 'runtime_minutes']
        rating = MOVIE.at[index,'average_rating']
        realease = MOVIE.at[index,'realease_year']
        genre_name = MOVIE.at[index,'genre_name_list']
        bulk_data.append(
            {
                "_index": "movie_full",
                "_id": id_oeuvre,
                "_source": {
                    "id_oeuvre": id_oeuvre,
                    "original_title": title,
                    "runtime_minutes" : runtime,
                    "average_rating" : rating,
                    "realease_year" : realease,
                    "id_genre_list": genres,
                    "genre_name_list": genre_name
                }
            }
        )
    bulk(ES, bulk_data)

    return {"ElasticSearch" : "L'insert dans le cache a bien été réalisé"}


def CreateAccount(name,email,password):
    global CLIENT, PROFIL
    with engine.connect() as connection :
        connection.execute(sql.text(f"INSERT INTO Client_ (email, pwd, profil_name) values ('{email}', '{password}', '{name}');"))
        id_client = pd.read_sql_query(sql.text(f"SELECT * FROM _Client WHERE email = '{email}'"),connection)['id_client'].values[0]
        id_profil = pd.read_sql_query(sql.text(f"SELECT * FROM _Profil WHERE id_client = '{id_client}'"),connection)['id_profil'].values[0]
        connection.commit()
        
    return id_client, id_profil

def AddProfilOeuvre(id_profil,id_oeuvre):
    with engine.connect() as connection :
        connection.execute(sql.text(f"INSERT INTO _profil_oeuvre (id_profil, id_oeuvre) values ('{id_profil}', '{id_oeuvre}');"))

        connection.commit() # TODO : commenter pour ne pas enregistrer dans la BDD (sinon ce sont des comptes temporaires j'usqu'a relancement de API)
    return

def RemoveProfilOeuvre(id_profil,id_oeuvre):
    with engine.connect() as connection :
        connection.execute(sql.text(f"DELETE FROM _profil_oeuvre WHERE id_profil='{id_profil}' AND id_oeuvre='{id_oeuvre}' ;"))

        connection.commit() # TODO : commenter pour ne pas enregistrer dans la BDD (sinon ce sont des comptes temporaires j'usqu'a relancement de API)
    return