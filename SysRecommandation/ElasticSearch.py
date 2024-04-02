"""
Commande à faire avant lancement :

docker run --rm -p 9200:9200 -p 9300:9300 -e "xpack.security.enabled=false" -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch:8.7.0
"""

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import pandas as pd
import sqlalchemy as sql


engine_uri = sql.URL.create(
    drivername="postgresql",
    username="postgres",
    password="L@nnion56220",
    host="localhost",
    database="SAE",
    port="3306"
)

engine = sql.create_engine(engine_uri)
conn = engine.connect()

query = sql.text("select id_oeuvre, original_title, id_genre from _movie natural join _oeuvre_genre natural join _genre;")
df = pd.read_sql_query(query,conn) # récupération des infos dans la BDD sous forme de DataFrame

df = df.groupby(by=["id_oeuvre"]) 


############################# IMPORT DONNÉES #############################

es = Elasticsearch("http://localhost:9200")

# Tentative trop couteuse en temps d'exécution
"""
# Structuration des données pour l'import
mappings = {
        "properties": {
            "id": {"type": "integer"},
            "title": {"type": "text", "analyzer": "standard"},
            "genre": {"type": "integer"}
    }
}

# Création de l'index pour l'import des données
es.indices.create(index="movies", mappings=mappings) # mettre en commentaire une fois le programme lancé pour la première fois

# Import des données dans le cache
for i, row in df.iterrows():
    doc = {
        "id": row["id_oeuvre"],
        "title": row["original_title"]
    }
            
    es.index(index="movies", id=i, document=doc)
"""

# Import des données dans le cache
bulk_data = []
for id_oeuvre in df.groups.keys():
    genres = df.get_group(id_oeuvre)["id_genre"]
    bulk_data.append(
        {
            "_index": "movies",
            "_id": id_oeuvre,
            "_source": {
                "id": id_oeuvre,
                "title": df.get_group(id_oeuvre)["original_title"].iloc[0],
                "genre": genres
            }
        }
    )
bulk(es, bulk_data)


########################### RECHERCHE ###########################

def search(titre, listeGenre): #Recherche des oeuvres par rapport au titre et aux genres de l'oeuvre donnée
    res = es.search(
        index="movies",
        query={
            "bool":{
                "must":[
                    {"match":{"title":titre}},
                    {"terms":{
                        "genre" : listeGenre,
                    }}
                ]
            }, 
        }       
    )
    return res

print('\nEnter a movie ID: (or STOP)')
movieID = input()
STOP = "STOP"

while movieID != STOP:
    movieID = int(movieID)
    # récupération des données importantes
    titre = df.get_group(movieID)["original_title"].iloc[0]
    genres = list(df.get_group(movieID)["id_genre"])
    
    # recherche
    resp = search(titre, genres)

    # affichage des résultats
    print("\n================ RESULTAT ================\n")
    print(f"Résultat de la recherche pour {titre} :\n")
    for rep in resp['hits']['hits'][1:6]:
        print(f"résultat : {rep['_source']['title']}, Score : {rep['_score']}")

    print('\nEnter a movie ID: (or STOP)')
    movieID = input()
