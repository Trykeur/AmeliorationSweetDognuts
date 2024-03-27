import pandas as pd
import numpy as np

from zg_fonctions import *

    
class Profil:
    artists = {}
    genres = []
    films = []
    id = 0

    def __init__(self, id):
        self.id = id

        artists = self.get_watched_artist()

        self.films = self.get_watched_movie()

        for keyA, valueA in artists.items():
            rateSum = 0
            i = 0

            for note in artists[keyA]:
                rateSum += note[0]
                i += 1

            rateSum /= i

            self.artists[keyA] = ind(rateSum)

        
    def get_watched_artist(self):
        engine = get_engine()

        request = "SET SEARCH_PATH='public'; SELECT _artist.id_artist, profession, know_for_title, rating FROM _artist LEFT JOIN _oeuvre_artist ON _artist.id_artist = _oeuvre_artist.ID_artist LEFT JOIN _oeuvre ON _oeuvre_artist.ID_oeuvre = _oeuvre.ID_oeuvre LEFT JOIN _profil_oeuvre ON _oeuvre.ID_oeuvre = _profil_oeuvre.id_oeuvre LEFT JOIN _profil ON _profil_oeuvre.ID_profil = _profil.ID_profil WHERE _profil.ID_profil = "
        request += str(self.id)
        request += ";"

        artists = pd.read_sql(request, engine)

        ar = {}

        for i in range(len(artists.index)):
            if artists["id_artist"][i] not in ar:
                ar[artists["id_artist"][i]] = []

            ar[artists["id_artist"][i]].append([artists["rating"][i], artists["know_for_title"][i]])

        return ar
    
    def get_watched_movie(self):
        engine = get_engine()

        request = "SET SEARCH_PATH='public'; SELECT _oeuvre.id_oeuvre, rating FROM _oeuvre LEFT JOIN _profil_oeuvre ON _oeuvre.ID_oeuvre = _profil_oeuvre.id_oeuvre LEFT JOIN _profil ON _profil_oeuvre.ID_profil = _profil.ID_profil WHERE _profil.ID_profil = "
        request += str(self.id)
        request += ";"

        movies_request = pd.read_sql(request, engine)
        movie_array = {}

        for i in range(len(movies_request)):
            if not np.isnan(movies_request["rating"][i]):
                movie_array[movies_request["id_oeuvre"][i]] = ind(movies_request["rating"][i])
            else:
                movie_array[movies_request["id_oeuvre"][i]] = ind(6)


        return movie_array
    

    def get_artists_to_request(self):
        appreciated_artists = ""

        for keyA, valueA in self.artists.items():
            if valueA >= 0.3:
                appreciated_artists += str(keyA) + ", "

        return appreciated_artists[:-2]
    

    def get_movie_to_request(self):
        watched_movies = ""


        for id in self.films:
            watched_movies += str(id) + ", "

        return watched_movies[:-2]


    def get_movies(self):
        return self.films
    