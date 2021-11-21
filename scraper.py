import pandas as pd
from bs4 import BeautifulSoup as bs
import requests as rq
import re


# helper class to scrape a movie
class MovieScraper:

    def __init__(self, movie_id):

        self.movie_id = movie_id

        uml = f'https://www.imdb.com/title/{self.movie_id}/'
        result = rq.get(uml)
        self.doc = bs(result.text, "html.parser")

    def get_movie_name(self):

        h1 = self.doc.find('h1')
        return h1.text.strip()

    def get_year(self):

        lis = self.doc.find_all('li', {'role': 'presentation'})

        for li in lis:
            if li.find('span') is not None:
                year = li.find('span').text.strip()
                if re.match('[0-9][0-9][0-9][0-9]', year):
                    return year
        return None

    def get_rating(self):

        regex = re.compile('.*AggregateRatingButton.*')

        span = self.doc.find('span', class_=regex)

        if span is None:
            return

        return span.text.strip()

    def get_genres(self):

        genres = []

        a_genres = self.doc.find_all('a',
                                     class_='GenresAndPlot__GenreChip-cum89p-3 fzmeux ipc-chip ipc-chip--on-baseAlt')
        for gen in a_genres:
            genre = gen.find('span', class_='ipc-chip__text').text
            genres.append(genre)
        return genres


# helper class to scrape a actor
class ActorScraper:

    def __init__(self, actor_id):
        self.actor_id = actor_id

        uml = f'https://www.imdb.com/name/{self.actor_id}/bio?ref_=nm_ov_bio_sm'
        result = rq.get(uml)

        self.doc = bs(result.text, "html.parser")

    # def get_birth_date(self):
    #     return self.doc.find("time")["datetime"]

    def get_birth_name(self):
        table = self.doc.find('table', id='overviewTable')
        birth_name = table.find('td', text='Birth Name')

        if birth_name is None:
            return

        return birth_name.find_next_sibling().text.strip()

    def get_nickname(self):
        table = self.doc.find('table', id='overviewTable')
        nicknames_td = table.find('td', text=['Nickname','Nicknames'])


        print(nicknames_td)
        if nicknames_td is None:
            return

        print(nicknames_td)
        nichkname_row = nicknames_td.find_next_sibling()
        nickname = nichkname_row.text

        return nickname



    def get_name(self):
        return self.doc.find('h3').findChild().text.strip()

    def get_hight(self):

        table = self.doc.find('table', id='overviewTable')

        height = table.find('td', text='Height')

        if height is None:
            return
        return height.find_next_sibling().text.strip()

    # def get_born_place(self):
    #
    #     table = self.doc.find('table', id='overviewTable')
    #
    #     place = table.find_all('a')[2]

    def get_pic_link(self):
        img = self.doc.find('img', class_='poster')
        return img['src']

    def get_mini_bio(self):
        div = self.doc.find('div', class_='soda odd')
        bio = div.findChild().text
        return bio

    def get_born_info(self):

        table = self.doc.find('table', class_='dataTable labelValueTable', id ='overviewTable')
        td = table.find('td',text='Born')
        td_born_info = td.find_next_sibling('td')

        return td_born_info.text.strip()



def get_actor_movie_ids(actor_id):
    actor_movie_ids = []

    uml = f'https://www.imdb.com/name/{actor_id}/'
    result = rq.get(uml)
    doc = bs(result.text, "html.parser")

    # search with regex expression for something like id = "actor-tt1234567"
    actor_id_list = doc.find_all(id=re.compile('actor-tt[0-9]+'
                                               '|actress-tt[0-9]+'))

    for a_id in actor_id_list:
        actor_movie_ids.append(re.findall('tt[0-9]+', a_id['id'])[0])

    return actor_movie_ids


def get_top50_actor_ids():
    actor_ids = []
    uml = f'https://www.imdb.com/list/ls053501318/'

    result = rq.get(uml)
    doc = bs(result.text, "html.parser")

    top_50_list = doc.find_all("div", {'class': 'lister-item mode-detail'})

    for item in top_50_list:
        a_tag = item.find('a')

        # get imdb id with regex expression , for example nm0000136 -> Johnny Depp
        imdb_actor_id = re.findall('nm[0-9]+', a_tag['href'])[0]
        actor_ids.append(imdb_actor_id)

    return actor_ids


# scrape movies, build dataframe and save the dataframe in a csv file (movies.csv)
def scrape_movies_df(actor_ids):
    columns = ['actor_id', 'movie_id', 'name', 'year', 'rating', 'genres']
    rows = []

    for actor_id in actor_ids:
        movie_ids = get_actor_movie_ids(actor_id)

        for movie_id in movie_ids:
            row = []
            movie_scraper = MovieScraper(movie_id)

            row.append(actor_id)
            row.append(movie_id)
            row.append(movie_scraper.get_movie_name())
            row.append(movie_scraper.get_year())
            row.append(movie_scraper.get_rating())
            row.append(movie_scraper.get_genres())
            rows.append(row)

    df = pd.DataFrame(rows, columns=columns)
    df.to_csv('movies.csv', index=False)


# scrape actors, build dataframe and save the dataframe in a csv file (actors.csv)
def scrape_actors_df(actor_ids):
    columns = ['imdb_id', 'name', 'pic_link', 'pos', 'birth_name', 'birth_info', 'nickname', 'hight', 'bio']
    rows = []

    for pos, actor_id in enumerate(actor_ids, start=1):
        row = []
        actor_scraper = ActorScraper(actor_id)

        row.append(actor_id)
        row.append((actor_scraper.get_name()))
        row.append(actor_scraper.get_pic_link())
        row.append(pos)
        row.append(actor_scraper.get_birth_name())
        row.append(actor_scraper.get_born_info())
        row.append(actor_scraper.get_nickname())
        row.append(actor_scraper.get_hight())
        row.append(actor_scraper.get_mini_bio())

        rows.append(row)

    df = pd.DataFrame(rows, columns=columns)
    df.to_csv('actors.csv', index=False)


# scrape awards, build dataframe and save the dataframe in a csv file (awards.csv)
def scrape_awards_df(actor_ids):
    columns = ['actor_id', 'award_name', 'year', 'award_outcome', 'award_description']
    rows = []

    for actor_id in actor_ids:
        uml = f'https://www.imdb.com/name/{actor_id}/awards?ref_=nm_awd'
        result = rq.get(uml)
        doc = bs(result.text, "html.parser")

        award_tables = doc.find_all('table', class_='awards')

        for award_table in award_tables:

            # find award name from previous h3 tag
            award_name = award_table.find_previous('h3').text.strip()
            trs = award_table.find_all('tr')

            for tr in trs:
                award_year = tr.find('td', class_='award_year')
                award_outcome = tr.find('td', class_='award_outcome')
                award_description = tr.find('td', class_='award_description')

                # if more than one award description is in the same column try to find data in previous ones
                if ((award_year is None) and (award_outcome is None) and (award_description is not None)):
                    temp1 = tr
                    temp2 = tr
                    while temp1.find('td', class_='award_year') is None:
                        temp1 = temp1.find_previous('tr')

                    while temp2.find('td', class_='award_outcome') is None:
                        temp2 = temp2.find_previous('tr')

                    award_year = temp1.find('td', class_='award_year')
                    award_outcome = temp2.find('td', class_='award_outcome')

                # if year column is shared for more than one row try to find data in previous ones
                if (award_year is None and award_outcome is not None and award_description is not None):
                    temp3 = tr
                    while temp3.find('td', class_='award_year') is None:
                        temp3 = temp3.find_previous('tr')

                    award_year = temp3.find('td', class_='award_year')

                # check for None values before method call
                if (award_year is not None):
                    award_year = award_year.text.strip()
                if (award_outcome is not None):
                    award_outcome = award_outcome.text.strip()
                if (award_description is not None):
                    award_description = award_description.text.strip()

                row = [actor_id, award_name, award_year, award_outcome, award_description]
                rows.append(row)

    df = pd.DataFrame(rows, columns=columns)
    df.to_csv('awards.csv', index=False)


def start_scraping():
    print('Start scraping ...')

    actor_ids = get_top50_actor_ids()


    scrape_actors_df(actor_ids)
    print('finished with actors')
    #
    # scrape_movies_df(actor_ids)
    # print('finished with movies')
    #
    # scrape_awards_df(actor_ids)
    # print('finished with awards')

    print('Scraping finished')


if __name__ == "__main__":
    start_scraping()
