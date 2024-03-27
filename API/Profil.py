import pandas as pd
import numpy as np

from MathFunction import enjoyIndex
from MathFunction import distance

    
class Profil:
    enjoyed_artist_df = pd.DataFrame()
    watched_movie_df = pd.DataFrame()
    artists = {}
    genres = []
    films = []
    id = 0

    def __init__(self, id, enjoyed_artist, watched_movie):
        self.id = id

        self.enjoyed_artist = enjoyed_artist
        self.watched_movie = watched_movie

        artists = self.enjoyed_artist_df

        self.films = self.get_watched_movie()

        for keyA, valueA in artists.items():
            rateSum = 0
            i = 0

            for note in artists[keyA]:
                rateSum += note[0]
                i += 1

            rateSum /= i

            self.artists[keyA] = enjoyIndex(rateSum)

        
    def get_watched_movie(self):
        movies_request = self.watched_movie

        movie_array = {}

        for i in range(len(movies_request)):
            if not np.isnan(movies_request["rating"][i]):
                movie_array[movies_request["id_oeuvre"][i]] = enjoyIndex(movies_request["rating"][i])
            else:
                movie_array[movies_request["id_oeuvre"][i]] = enjoyIndex(6)


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
    