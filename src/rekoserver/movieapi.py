from tmdbv3api import TMDb, Movie, Configuration


class MovieApi:
    def __init__(self):
        self.__tmdb = TMDb()
        self.__tmdb.language = 'pl'

        self.movie = Movie()
        self.__amount = 12
        self.popular = self.movie.popular()[:self.__amount]

        self.__conf = Configuration()
        self.info = self.__conf.info()

        self.base_url = self.info.images['base_url']
        self.size = self.info.images['poster_sizes'][3]
        self.full_url = self.base_url + self.size
        self.paths = [path for path in [self.popular[mov]['poster_path'] for mov in range(len(self.popular))]]


m_api = MovieApi()
