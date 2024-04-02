# Import Fast API
import uvicorn
from fastapi import FastAPI, Query, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List

# Connection to Data base
from connect import initialisationDB as initDB
from connect import CreateAccount, AddProfilOeuvre, RemoveProfilOeuvre

# Connection to ElasticSearch
from connect import ES
from connect import initialisationCache as initES

#  Recommandation functions
import Recommandation
from pandas import merge as pd_merge ,Categorical
from old_fonction_recommandation_ACM import *

LIMIT = 10
GENRE, MOVIE, MOVIE_PROFIL, ARTIST, MOVIE_ARTIST, MOVIE_GENRE, PROFIL, CLIENT= initDB()


# Initialisazion of ElasticSearch cache
initES(MOVIE)

#API
print("-- API starting ...")
app = FastAPI()

# Settings used for the web site connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
"""---------------------------------------- FUNCTIONS ----------------------------------------"""
def RequestFilter(data,dataName,field=None,limit=False):
    if(field):
        for f in field:
            if(f not in data.columns): return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=f"{dataName} not contains '{f}' field.") 
        data = data[field]
    
    if(limit):
        try : limit = int(limit)
        except : return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="'limit' must be an integer")
        
        if(limit < 1):return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="'limit' must be an positive and not null")
        data = data.head(limit)

    return JSONResponse(status_code=status.HTTP_200_OK, content=data.to_dict('records'))

def RequestFilterWithScore(data,dataName,field=None,limit=False):
    if(field):
        for f in field:
            if(f not in data[0]['movie']): return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=f"{dataName} not contains '{f}' field.") 
        for d in data:
            d['movie'] = {k:d['movie'][k] for k in field if k in d['movie']}
    
    if(limit):
        try : limit = int(limit)
        except : return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="'limit' must be an integer")
        
        if(limit < 1):return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="'limit' must be an positive and not null")
        data = data[:limit]

    return JSONResponse(status_code=status.HTTP_200_OK, content=data)

"""---------------------------------------- API ----------------------------------------"""
@app.get("/")
def read_root():
    return "API Système de recommandation : Les donuts sucrés au sucre"

"""---------------------------------------- API - GENRE ----------------------------------------"""
@app.get("/genres") 
def GetAllGenres(limit = False):
    """
    GET all genres sort by NbMovies (with field in optionnal parameters)
    EXAMPLE : 
    - http://127.0.0.1:8000/genres
    - http://127.0.0.1:8000/genres?limit=10
    """

    genres = MOVIE_GENRE.groupby(by=["id_genre"]).count().rename(columns={'id_oeuvre':'NbMovies'}).merge(GENRE, how='inner', on='id_genre')
    
    genres = genres.sort_values(by='NbMovies', ascending=False)
    if(genres.empty) :return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content='No recorded genres')
    
    genres = genres.drop(['NbMovies'], axis=1)

    Response = RequestFilter(genres,'Genres',None,limit)
    return Response


"""---------------------------------------- API - CLIENT ----------------------------------------"""
@app.post("/login") 
def login(data:dict):
    """
    Login authorization. Return HTTP_200_OK (with his id_client & id_profil) if the email and password are correct
    EXAMPLE : 
    - http://127.0.0.1:8000/login
    """

    if(CLIENT.empty) : return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content='No recorded clients')
    
    if(data['email'] == None or data['password'] == None):return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST)
    
    id_client = CLIENT.loc[(CLIENT['email'] == data['email']) & (CLIENT['pwd'] == data['password'])]
    if(id_client.empty) :return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=f"email or password incorrect")
    id_client = int(id_client.index[0])

    id_profil = [item[1] for item in list(PROFIL.index) if item[0]==id_client][0]

    return JSONResponse(status_code=status.HTTP_200_OK, content={'Client':id_client,'Profil':id_profil})


@app.post("/register") 
def register(data:dict):
    global CLIENT
    global PROFIL
    """
    Create new account. Return HTTP_200_OK if the email not already registered.
    - http://127.0.0.1:8000/register
    """
    
    if(data['name'] == None or data['email'] == None or data['password'] == None):return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST)

    verif_email = CLIENT.loc[CLIENT['email'] == data['email']]
    if(not verif_email.empty) :return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=f"email already registered")
    
    id_client,id_profil = CreateAccount(data['name'],data['email'],data['password'])

    CLIENT.loc[id_client] = [data['email'],data['password']]
    PROFIL.loc[(id_client,id_profil),:] = [data['name'],None]
    
    return JSONResponse(status_code=status.HTTP_200_OK, content="Successful registration")
    

@app.post("/client/add/movie") 
def AddMovieProfil(data:dict):
    global PROFIL
    global MOVIE_PROFIL
    """
        Add new movie to the list of a profil.
        EXAMPLE : 
        - http://127.0.0.1:8000/client/add/movie
    """
    if(data['id_profil'] == None or data['id_oeuvre'] == None):return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST)

    try : 
        data['id_client'] = int(data['id_client'])
        data['id_profil'] = int(data['id_profil'])
    except : 
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="'id_profil' and 'id_client' must be an integer")

    if((data['id_client'],data['id_profil']) not in PROFIL.index) :return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=f"Unknown profil")
    
    verif_movie = MOVIE.loc[MOVIE['id_oeuvre'] == data['id_oeuvre']]
    if(verif_movie.empty) :return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=f"Unknown movie")
    
    verif_movieProfil = MOVIE_PROFIL.loc[(MOVIE_PROFIL['id_profil'] == data['id_profil']) & (MOVIE_PROFIL['id_oeuvre'] == data['id_oeuvre'])]
    if(not verif_movieProfil.empty) :return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=f"Movie already registered")

    AddProfilOeuvre(data['id_profil'],data['id_oeuvre']) # TODO : Commenter pour ne pas enregistrer dans la BDD (Si les comptes temporaires ne sont pas utilisé (décommenté VOIR TODO dans connect.py))
    MOVIE_PROFIL = MOVIE_PROFIL._append({'id_profil':data['id_profil'],'id_oeuvre':data['id_oeuvre'],'rating':None}, ignore_index=True)

    return JSONResponse(status_code=status.HTTP_200_OK, content="Successful")

@app.post("/client/remove/movie") 
def RemoveMovieProfil(data:dict):
    global PROFIL
    global MOVIE_PROFIL
    """
        Remove existing movie to the list of a profil.
        EXAMPLE : 
        - http://127.0.0.1:8000/client/remove/movie
    """
    if(data['id_profil'] == None or data['id_oeuvre'] == None):return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST)

    try : 
        data['id_client'] = int(data['id_client'])
        data['id_profil'] = int(data['id_profil'])
    except : 
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="'id_profil' and 'id_client' must be an integer")
    
    if((data['id_client'],data['id_profil']) not in PROFIL.index) :return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=f"Unknown profil")
    
    verif_movie = MOVIE.loc[MOVIE['id_oeuvre'] == data['id_oeuvre']]
    if(verif_movie.empty) :return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=f"Unknown movie")

    verif_movieProfil = MOVIE_PROFIL.loc[(MOVIE_PROFIL['id_profil'] == data['id_profil']) & (MOVIE_PROFIL['id_oeuvre'] == data['id_oeuvre'])]
    if(verif_movieProfil.empty) :return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=f"Movie not registered")

    RemoveProfilOeuvre(data['id_profil'],data['id_oeuvre'])
    MOVIE_PROFIL.drop(MOVIE_PROFIL[(MOVIE_PROFIL['id_profil'] == data['id_profil']) & (MOVIE_PROFIL['id_oeuvre'] == data['id_oeuvre'])].index, inplace = True)

    return JSONResponse(status_code=status.HTTP_200_OK, content="Successful")

@app.get("/client/{id_profil}/get/movie") 
def GetMovieProfil(id_profil,field: List[str] = Query(None),limit = False):
    """
        Get all movies in the list of a profile.
        EXAMPLE : 
        - http://127.0.0.1:8000/client/5/get/movie
        - http://127.0.0.1:8000/client/85/get/movie
    """
    try : id_profil = int(id_profil)
    except : return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="'id_profil' must be an integer")
    
    if(MOVIE.empty) :return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content='No recorded movies')
    
    if(id_profil not in MOVIE_PROFIL['id_profil'].values) :return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=f"No recorded movies for user : '{id_profil}'")
    movieListe = MOVIE_PROFIL.loc[MOVIE_PROFIL['id_profil'] == id_profil].sort_values(by='rating', ascending=False)['id_oeuvre'].values
    
    Movies = MOVIE.loc[MOVIE['id_oeuvre'].isin(movieListe)]
    Movies["id_oeuvre"] = Categorical(Movies["id_oeuvre"], categories=movieListe)
    Movies.sort_values(by="id_oeuvre", inplace=True)
    
    Movies = Movies.drop(['id_genre_list'], axis=1)
    Movies.rename(columns={'genre_name_list': 'genres'},inplace=True)
    
    Response = RequestFilter(Movies,'Movie',field,limit)
    return Response

"""---------------------------------------- API - MOVIE ----------------------------------------"""
# GET all Movies (with field in optionnal parameters)
@app.get("/movie") 
def GetAllMovie(field: List[str] = Query(None),limit = False):
    """
    GET all Movies (with field in optionnal parameters)
    EXAMPLE : 
    - http://127.0.0.1:8000/movie
    - http://127.0.0.1:8000/movie?limit=10
    - http://127.0.0.1:8000/movie?field=id_oeuvre&field=original_title
    """
    if(MOVIE.empty) :return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content='No recorded movies')
    
    Movies = MOVIE.drop(['id_genre_list'], axis=1)
    Movies.rename(columns={'genre_name_list': 'genres'},inplace=True)
    Response = RequestFilter(Movies,'Movie',field,limit)
    return Response
    

# GET a movie by ID (with field in optionnal parameters)
@app.get("/movie/id/{id_oeuvre}")
def GetMovieByID(id_oeuvre,field: List[str] = Query(None)):
    """
    GET a movie by ID (with field in optionnal parameters)
    EXAMPLE : 
    - http://127.0.0.1:8000/movie/id/7160238
    - http://127.0.0.1:8000/movie/id/7160238?field=id_oeuvre&field=original_title
    """
    try : id_oeuvre = int(id_oeuvre)
    except : return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="'id_oeuvre' must be an integer")

    Movie = MOVIE.loc[MOVIE['id_oeuvre'] == id_oeuvre]
    if(Movie.empty) :return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=f"No recorded movies with ID : '{id_oeuvre}'")

    # Movie.drop(['id_genre_list'], axis=1,inplace=True)
    Movie.rename(columns={'genre_name_list': 'genres'},inplace=True)

    Response = RequestFilter(Movie,'Movie',field)
    return Response


# GET a movie by ID with artists list
@app.get("/movie/id/{id_oeuvre}/artists")
def GetMovieByIDWithArtist(id_oeuvre):
    try : id_oeuvre = int(id_oeuvre)
    except : return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="'id_oeuvre' must be an integer")

    Movie = MOVIE.loc[MOVIE['id_oeuvre'] == id_oeuvre]
    if(Movie.empty) :return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=f"No recorded movies with ID : '{id_oeuvre}'")
    
    Movie.drop(['id_genre_list'], axis=1,inplace=True)
    Movie.rename(columns={'genre_name_list': 'genres'},inplace=True)
    Movie = Movie.to_dict('records')

    Artists = MOVIE_ARTIST.loc[MOVIE_ARTIST['id_oeuvre'] == id_oeuvre]
    
    Artists_info = ARTIST.loc[ARTIST['id_artist'].isin(Artists['id_artist'].values)]
    
    Artists = pd_merge(Artists, Artists_info,how="left",on="id_artist")
    Artists.drop(['id_oeuvre'], axis=1,inplace=True)

    Movie[0]['Artists'] = Artists.to_dict('records')
    
    return JSONResponse(status_code=status.HTTP_200_OK, content=Movie)




"""---------------------------------------- ARTISTS ----------------------------------------"""
# GET all Artists (with field in optionnal parameters)
@app.get("/artist") 
def GetAllArtist(field: List[str] = Query(None),limit = False):
    """
    GET all Artist (with field in optionnal parameters)
    EXAMPLE : 
    - http://127.0.0.1:8000/artist
    - http://127.0.0.1:8000/artist?field=id_artist&field=primary_name
    """
    Response = RequestFilter(ARTIST,'Artist',field,limit)
    return Response


# GET Artists by ID (with field in optionnal parameters)
@app.get("/artist/id/{id_artist}")
def GetArtistByID(id_artist,field: List[str] = Query(None)):
    """
    GET an artist by ID (with field in optionnal parameters)
    EXAMPLE : 
    - http://127.0.0.1:8000/artist/id/158342
    - http://127.0.0.1:8000/artist/id/158342?field=id_artist&field=primary_name
    """
    try : id_artist = int(id_artist)
    except : return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, detail="'id_artist' must be an integer")

    Artist = ARTIST.loc[ARTIST['id_artist'] == id_artist]
    if(Artist.empty) :return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=f"No recorded Artists with ID : '{id_artist}'")

    Response = RequestFilter(Artist,'Artist',field)
    return Response


# GET an artist by ID with movie list
@app.get("/artist/id/{id_artist}/movies")
def GetArtistByIDWithMovies(id_artist):
    """
    GET an artist by ID (with field in optionnal parameters)
    EXAMPLE : 
    - http://127.0.0.1:8000/artist/id/158342/movies
    """
    try : id_artist = int(id_artist)
    except : return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, detail="'id_artist' must be an integer")

    Artist = ARTIST.loc[ARTIST['id_artist'] == id_artist].to_dict('records')
    if(not Artist) :return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=f"No recorded Artists with ID : '{id_artist}'")

    Movies = MOVIE_ARTIST.loc[MOVIE_ARTIST['id_artist'] == id_artist]

    Movies_info = MOVIE.loc[MOVIE['id_oeuvre'].isin(Movies['id_oeuvre'].values)]
    
    Movies = pd_merge(Movies, Movies_info,how="left",on="id_oeuvre")
    Movies.drop(['id_artist'], axis=1,inplace=True)

    Movies.drop(['id_genre_list'], axis=1,inplace=True)
    Movies.rename(columns={'genre_name_list': 'genres'},inplace=True)

    Artist[0]['Movies'] = Movies.to_dict('records')
    
    return JSONResponse(status_code=status.HTTP_200_OK, content=Artist)




"""---------------------------------------- RECOMMANDATION ----------------------------------------"""
@app.get("/recommandation/by/id_oeuvre/{id_oeuvre}/id_profil/{id_profil}")
def RecommandationByOeuvre(id_oeuvre,id_profil,field: List[str] = Query(None),limit = LIMIT):
    """
    You have watched this movie, others have also enjoyed
    EXAMPLE : 
    - http://127.0.0.1:8000/recommandation/by/id_oeuvre/2655467/id_profil/5
    """
    try : id_oeuvre = int(id_oeuvre)
    except : return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="'id_oeuvre' must be an integer")
    
    try : id_profil = int(id_profil)
    except : id_profil = None

    if(id_oeuvre not in MOVIE['id_oeuvre'].values) :return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=f"No recorded movies with ID : '{id_oeuvre}'")
    genre = GENRE[["id_genre","genre_name"]].values
    genres = {genre[i][0]: genre[i][1] for i in range(len(genre))}
    data = Recommandation.UserBased_Vecteur(genres,MOVIE,MOVIE_PROFIL,ID_OEUVRE=id_oeuvre,ID_PROFIL=id_profil,ratingMin=5,seuilScore=0.4)
    
    response = RequestFilter(data,'Movie',field,limit)
    return response


@app.get("/recommandation/by/id_profil/{id_profil}")
def RecommandationByProfil(id_profil):
    """
    Recommendation from a user's movie list
    EXAMPLE : 
    - http://127.0.0.1:8000/recommandation/by/id_profil/38
    """
    try : id_profil = int(id_profil)
    except : return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="'id_profil' must be an integer")
    
    if(id_profil not in MOVIE_PROFIL['id_profil'].values) :return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=f"No recorded movies for user : '{id_profil}'")

    data = Recommandation.RecommandationByProfil(MOVIE, MOVIE_PROFIL, MOVIE_ARTIST, ARTIST, GENRE, MOVIE_GENRE, ID_PROFIL=id_profil)
    return JSONResponse(status_code=status.HTTP_200_OK, content=data)

@app.get("/old_recommandation/by/id_profil/{id_profil}")
def RecommandationByProfil_OLD(id_profil):
    """
    Recommendation from a user's movie list
    EXAMPLE : 
    - http://127.0.0.1:8000/old_recommandation/by/id_profil/38
    """
    try : id_profil = int(id_profil)
    except : return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="'id_profil' must be an integer")
    
    if(id_profil not in MOVIE_PROFIL['id_profil'].values) :return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=f"No recorded movies for user : '{id_profil}'")

    id_recommanded_movies = recommandation_OLD(id_profil)
    recommanded_movies = []

    # Récupération des films dans le DataFrame MOVIE
    recommanded_movies = MOVIE.loc[MOVIE["id_oeuvre"].isin(id_recommanded_movies)]

    recommanded_movies = recommanded_movies.drop(['id_genre_list'], axis=1)
    recommanded_movies.rename(columns={'genre_name_list': 'genres'},inplace=True)
        
    return JSONResponse(status_code=status.HTTP_200_OK, content=recommanded_movies.to_dict('records'))


@app.get("/recommandation/nextMovie/{movieID}")
def recommandationES(movieID, field: List[str] = Query(None),limit = False):
    try : movieID = int(movieID)
    except : return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="'movieID' must be an integer")

    res = Recommandation.ElasticSearch(ES, MOVIE, movieID)
    response = RequestFilterWithScore(res,'Movie',field, limit)
    return response


@app.get("/recommandation/by/genre/{id_genre}") 
def recommandationGenre(id_genre,limit = 10):
    """
    GET all Movies with a speific genre sort by num_votes(with field in optionnal parameters)
    EXAMPLE : 
    - http://127.0.0.1:8000/recommandation/by/genre/1
    - http://127.0.0.1:8000/recommandation/by/genre/1?limit=10
    """
    try : id_genre = int(id_genre)
    except : return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="'id_genre' must be an integer")

    if(MOVIE.empty) :return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content='No recorded movies')
    if(GENRE.empty) :return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content='No recorded genre')
    
    Movies = MOVIE[MOVIE['id_genre_list'].apply(lambda x: id_genre in x)].sort_values(by='num_votes', ascending=False)
    
    
    Movies = Movies.drop(['id_genre_list'], axis=1)
    Movies.rename(columns={'genre_name_list': 'genres'},inplace=True)
    Response = RequestFilter(Movies,'Movie',None,limit)
    
    return Response

"""---------------------------------------- RECOMMANDATION (Statistiques) ----------------------------------------"""
@app.get("/recommandation/TopRatedMovies")
def TopRatedMovies(field: List[str] = Query(None), limit : int = LIMIT):
    """
    Top Rated Movies
    EXAMPLE : 
    - http://127.0.0.1:8000/recommandation/TopRatedMovies
    - http://127.0.0.1:8000/recommandation/TopRatedMovies?field=original_title&field=realease_year&field=average_rating
    """
    try : limit = int(limit)
    except : return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="'limit' must be an integer")

    df_temp = MOVIE.sort_values(by=['average_rating','num_votes'],ascending=False).head(n=limit)
    
    df_temp.drop(['id_genre_list'], axis=1,inplace=True)
    df_temp.rename(columns={'genre_name_list': 'genres'},inplace=True)
    
    Response = RequestFilter(df_temp,'Movie',field,limit)
    return Response


@app.get("/recommandation/TopPopularMovies")
def TopPopularMovies(field: List[str] = Query(None), limit : int = LIMIT):
    """
    Top Popular Movies
    EXAMPLE : 
    - http://127.0.0.1:8000/recommandation/TopPopularMovies
    - http://127.0.0.1:8000/recommandation/TopPopularMovies?field=original_title&field=realease_year&field=average_rating
    """
    try : limit = int(limit)
    except : return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="'limit' must be an integer")

    df_temp = MOVIE.sort_values(by=['num_votes'],ascending=False).head(n=limit) # Change NB RESULT to var()
    
    df_temp.drop(['id_genre_list'], axis=1,inplace=True)
    df_temp.rename(columns={'genre_name_list': 'genres'},inplace=True)
    
    Response = RequestFilter(df_temp,'Movie',field,limit)
    return Response

@app.get("/recommandation/TopYears")
def TopYears(limit : int = LIMIT):
    print(limit,LIMIT)
    df_temp = MOVIE.dropna(subset=['realease_year'])

    # partitionnement
    YearsRange = (df_temp['realease_year'].min(),df_temp['realease_year'].max())
    YearsRange = [int(y-y%10) for y in YearsRange]
    partitionnementByYears = [(x,x+10) for x in range(YearsRange[0],YearsRange[1],10)]
    for inter in partitionnementByYears:
        df_temp.loc[(df_temp.realease_year >= inter[0]) & (df_temp.realease_year < inter[1]), 'YEAR_GROUP'] = inter[0]
    
    df_temp = df_temp.groupby('YEAR_GROUP')
    
    # Find average rating by group
    NbMovies = 0
    partitioningData = {}
    for group in df_temp.groups.keys(): # 287 165 films sur 574 512
        NbMoviesInGroup = df_temp.get_group(group)['id_oeuvre'].count()
        averageRating = df_temp.get_group(group)['average_rating'].mean()
        NbMovies+=NbMoviesInGroup
        
        partitioningData[group] = {'NbMovies':NbMoviesInGroup,'averageRating':averageRating,'YearsRange':[group,group+10]}

    NbPartitions = len(partitioningData.keys())
    NbMoviesMeanByPartition = NbMovies/NbPartitions
    
    for group in partitioningData.copy():
        if(partitioningData[group]['NbMovies'] < NbMoviesMeanByPartition):
            del partitioningData[group]
    
    year = max(partitioningData, key=lambda k: partitioningData[k]['averageRating'])
    yearGroup = df_temp.get_group(year)
    yearGroup.drop(['id_genre_list'], axis=1,inplace=True)
    yearGroup.rename(columns={'genre_name_list': 'genres'},inplace=True)
    yearGroup.drop(['YEAR_GROUP'], axis=1,inplace=True)
    
    data = yearGroup.loc[yearGroup['average_rating'] > 5].sample(n=limit)
    response = RequestFilter(data,'Movie')
    return response


"""----------------------------------------------- ADVANCED SEARCH -----------------------------------------------"""
@app.get("/Advancedsearch")
def Advancedsearch(title = False, reg = False, runtimeMIN = False, runtimeMAX = False, ratingMIN = False, ratingMAX = False, yearMIN = False, yearMAX = False, listeGenre : List[int] = Query(None), field: List[str] = Query(None),limit = False):
    def searchES(title = False, reg = False, runtimeMIN = False, runtimeMAX = False, ratingMIN = False, ratingMAX = False, yearMIN = False, yearMAX = False, listeGenre = False): #Recherche avancée d'oeuvres par rapport au titre, genre, notes, etc.
        must = []
        if(title and not reg):
            must.append({"match":{"original_title":title}})
        if(title and reg):
            must.append({"regexp":{"original_title":{"value":title, "flags":"ALL", "case_insensitive": True}}})
        if(runtimeMIN):
            must.append({"range":{'runtime_minutes':{'gte':runtimeMIN}}})
        if(runtimeMAX):
            must.append({"range":{'runtime_minutes':{'lte':runtimeMAX}}})
        if(ratingMIN):
            must.append({"range":{'average_rating':{'gte':ratingMIN}}})
        if(ratingMAX):
            must.append({"range":{'average_rating':{'lte':ratingMAX}}})
        if(yearMIN):
            must.append({"range":{'realease_year':{'gte':yearMIN}}})
        if(yearMAX):
            must.append({"range":{'realease_year':{'lte':yearMAX}}})
        if(listeGenre):
            must.append({"terms":{"id_genre_list" : listeGenre}})
        
        res = ES.search(
            index="movie_full",
            
            query={
                "bool":{
                    "must": must
                }, 
            }       
        )

        res = res['hits']['hits']
        resp = []
        for i in range(len(res)):
            movie = res[i]['_source']
            movie['genres'] = movie['genre_name_list']
            del movie['id_genre_list']
            del movie['genre_name_list']

            resp.append(
                res[i]['_source']
            )
        
        return resp

    liste = {'runtimeMIN':runtimeMIN,'runtimeMAX':runtimeMAX,'ratingMIN':ratingMIN,'ratingMAX':ratingMAX,'yearMIN':yearMIN,'yearMAX':yearMAX}
    for key in liste.keys():
        if(liste[key]):
            try : liste[key] = float(liste[key])
            except : return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=f"'{key}' must be an integer")
    reg = bool(int(reg))
    resp = searchES(title, reg, liste['runtimeMIN'], liste['runtimeMAX'], liste['ratingMIN'], liste['ratingMAX'], liste['yearMIN'], liste['yearMAX'], listeGenre)

    return RequestFilterWithScore(resp,'Movie',field, limit)

if __name__ == "__main__":
    uvicorn.run(app, host='127.0.0.1', port=8000, log_level="debug")
