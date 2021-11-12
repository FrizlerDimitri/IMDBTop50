import pandas as pd
from bs4 import BeautifulSoup as bs, ResultSet
import requests as rq
import re
from matplotlib import pyplot as plt


import scraper


class Movie:

    def __init__(self, actor_id, movie_id, name, year, rating, genres):
        self.actor_id = actor_id
        self.movie_id = movie_id
        self.name = name
        self.year = year
        self.rating = rating
        self.genres = genres


class Award:

    def __init__(self, award_imdb_id, year, outcome, description):
        self.award_imdb_id = award_imdb_id
        self.year = year
        self.outcome = outcome
        self.description = description

    def get_award_name(self):
        uml = f'https://www.imdb.com/event/{self.award_imdb_id}/{self.year}/1'
        result = rq.get(uml)

        doc = bs(result.text, 'html.parser')

        name = doc.find('h1').text.strip()

        return name


class Actor:

    def __init__(self, imdb_id, name, pic_link, pos, birth_name, birth_date, nickname, hight, bio, movies):
        self.imdb_id = imdb_id
        self.name = name
        self.pic_link = pic_link
        self.pos = pos
        self.birth_name = birth_name
        self.birth_date = birth_date
        self.nickname = nickname
        self.hight = hight
        self.bio = bio
        self.movies = movies

    def __str__(self):
        return f'actor ( name = {self.name})'

    def __repr__(self):
        return f'actor ( name = {self.name})'

    def get_all_unique_movie_genres(self):
        genres_set = set()
        movies = self.movies
        for movie in movies:
            genres = movie.genres
            for genre in genres:
                genres_set.add(genre)

        genre_list = list(genres_set)
        return genre_list

    # Todo Remove method after implemant awards
    def get_awards(self):
        uml = f'https://www.imdb.com/name/{self.imdb_id}/awards?ref_=nm_awd'
        result = rq.get(uml)
        doc = bs(result.text, "html.parser")
        awards = []

        tables = doc.find_all('table', class_='awards')

        for table in tables:
            tr = table.find('tr')

            # get award year
            td = tr.find('td', class_='award_year')
            a = td.find('a')
            award_imdb_id = re.findall('ev[0-9][0-9][0-9][0-9][0-9][0-9][0-9]', a['href'])[0]

            year = a.text.strip()

            td = tr.find('td', class_='award_outcome')
            b = td.find('b')
            outcome = b.text.strip()

            td = tr.find('td', class_='award_description')
            description = td.text

            award = Award(award_imdb_id, year, outcome, description)

            awards.append(award)
        return awards

    def calc_average_rating_aver_all(self):
        avg = 0
        count = 0
        for movie in self.movies:
            if not pd.isna(movie.rating):
                avg = avg + movie.rating
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
        # avg_per_year_sorted_after_year=avg_per_year.sort_values(by=['year'],ascending=False)
        # print(avg_per_year_sorted_after_year)

        avg_per_year_df = avg_per_year.reset_index()

        x = avg_per_year_df['year']
        y = avg_per_year_df['rating']

        plt.title(f'Average of {self.name}s movie Rating per year')
        plt.ylabel(f'Rating')
        plt.xlabel('year')
        plt.plot(x, y)
        plt.show()

    def get_top_X_movies(self, number):

        rated_movies = []

        for mov in self.movies:
            if not pd.isna(mov.rating):
                rated_movies.append(mov)

        sorted_movies = sorted(rated_movies, key=lambda Movie: Movie.rating,reverse=True)
        if len(sorted_movies) <= number:
            return sorted_movies

        return_list = []
        for x in range(0, number + 1):
            return_list.append(sorted_movies[x])
        return return_list


def get_all_actor_info():
    actors_df = pd.read_csv('actors.csv')
    movies_df = pd.read_csv('movies.csv')

    # Todo implemant and scrabe Awards

    actors = []

    for index, row in actors_df.iterrows():
        imdb_id = row['imdb_id']
        name = row['name']
        pic_link = row['pic_link']
        pos = row['pos']
        birth_name = row['birth_name']
        birth_date = row['birth_date']
        nickname = row['nickname']
        hight = row['hight']
        bio = row['bio']

        movies = []
        movies_df = movies_df[movies_df['actor_id'] == imdb_id]

        for i, movies_row in movies_df.iterrows():
            actor_id = movies_row['actor_id']
            movie_id = movies_row['movie_id']
            movie_name = movies_row['name']
            year = movies_row['year']
            rating = movies_row['rating']
            genres = eval(movies_row['genres'])  # eval -> convert '[ a , b, c ]' from  String to a list
            movie = Movie(actor_id, movie_id, movie_name, year, rating, genres)
            movies.append(movie)

        # TODO same for awards

        actor1 = Actor(imdb_id, name, pic_link, pos, birth_name, birth_date, nickname, hight, bio, movies)

        actors.append(actor1)

    return actors


def fuctiTest():
    return "test 123 123"


if __name__ == '__main__':
    # scraper.start_scraping()

    actors = get_all_actor_info()
    actor = actors[0]
    # actor.get_all_unique_movie_genres()
    # print(actor.calc_average_rating_aver_all())
    # actor.calc_average_for_all_years()

    for movie in actor.get_top_X_movies(1000):
        print(f"Movie : {movie.name} ranking {movie.rating}/10 ")

    print('End')
