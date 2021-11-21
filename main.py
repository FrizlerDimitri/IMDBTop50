import pandas as pd


class Movie:

    def __init__(self, actor_id, movie_id, name, year, rating, genres):
        self.actor_id = actor_id
        self.movie_id = movie_id
        self.name = name
        self.year = year
        self.rating = rating
        self.genres = genres


class Award:

    def __init__(self, award_imdb_id, award_name, year, outcome, description):
        self.award_imdb_id = award_imdb_id
        self.award_name = award_name
        self.year = year
        self.outcome = outcome
        self.description = description


class Actor:

    def __init__(self, imdb_id, name, pic_link, pos, birth_name, birth_info, nickname, hight, bio, movies=[],
                 awards=[]):
        self.imdb_id = imdb_id
        self.name = name
        self.pic_link = pic_link
        self.pos = pos
        self.birth_name = birth_name
        self.birth_info = birth_info
        self.nickname = nickname
        self.hight = hight
        self.bio = bio
        self.movies = movies
        self.awards = awards

    def __str__(self):
        return f'actor ( name = {self.name})'

    def __repr__(self):
        return f'actor ( name = {self.name})'

    # call load_movie() methode before using this methode
    def get_all_unique_movie_genres(self):
        genres_set = set()
        movies = self.movies
        for mo in movies:
            genres = mo.genres
            for genre in genres:
                genres_set.add(genre)

        genre_list = list(genres_set)
        return genre_list

    # loading movies from csv, needed to be called before using movie related functions
    def load_movies(self):
        movies_df = pd.read_csv('movies.csv')
        movies = []
        movies_df = movies_df[movies_df['actor_id'] == self.imdb_id]
        for i, movies_row in movies_df.iterrows():
            actor_id = movies_row['actor_id']
            movie_id = movies_row['movie_id']
            movie_name = movies_row['name']
            year = movies_row['year']
            rating = movies_row['rating']
            genres = eval(movies_row['genres'])  # eval -> convert '[ a,b,c ]' from  one String to a list of Strings
            move = Movie(actor_id, movie_id, movie_name, year, rating, genres)
            movies.append(move)

        self.movies = movies

    def load_awards(self):

        awards_df = pd.read_csv('awards.csv')
        awards = []
        awards_df = awards_df[awards_df['actor_id'] == self.imdb_id]
        for i, award_row in awards_df.iterrows():
            actor_id = award_row['actor_id']
            award_name = award_row['award_name']
            year = award_row['year']
            award_outcome = award_row['award_outcome']
            award_description = award_row['award_description']
            award = Award(actor_id, award_name, year, award_outcome, award_description)
            awards.append(award)

        self.awards = awards

    # call load_movie() methode before using this methode
    def calc_average_rating_aver_all(self):
        avg = 0
        count = 0
        for m in self.movies:
            if not pd.isna(m.rating):
                avg = avg + m.rating
                count = count + 1

        avg = avg / count
        return avg

    def calc_average_for_all_years(self):

        df = pd.read_csv('movies.csv')
        df = df[df['actor_id'] == self.imdb_id]

        yr_df = df[['year', 'rating']]

        # drop none and nan from df
        yr_df = yr_df.dropna()

        # group by year calc avr and sort by a descending order
        avg_per_year = yr_df.groupby(['year']).mean(['rating'])
        avg_per_year_df = avg_per_year.reset_index()
        return avg_per_year_df

    # call load_movie() methode before using this methode
    def get_top_X_movies(self, number):

        rated_movies = []

        for mov in self.movies:
            # remove movies without rating
            if not pd.isna(mov.rating):
                rated_movies.append(mov)

        sorted_movies = sorted(rated_movies, key=lambda Movie: Movie.rating, reverse=True)
        if len(sorted_movies) <= number:
            return sorted_movies

        return_list = []
        for x in range(0, number):
            return_list.append(sorted_movies[x])
        return return_list

    # for performance sake will not load the movies, you need to call the load_movies() methode for each actor first


def get_all_actor_info():
    actors_df = pd.read_csv('actors.csv')

    acts = []

    for index, row in actors_df.iterrows():
        imdb_id = row['imdb_id']
        name = row['name']
        pic_link = row['pic_link']
        pos = row['pos']
        birth_name = row['birth_name']
        birth_info = row['birth_info']
        nickname = row['nickname']
        hight = row['hight']
        bio = row['bio']

        actor1 = Actor(imdb_id, name, pic_link, pos, birth_name, birth_info, nickname, hight, bio)
        acts.append(actor1)

    return acts
