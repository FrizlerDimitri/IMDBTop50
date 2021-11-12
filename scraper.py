import pandas as pd
from bs4 import BeautifulSoup as bs
import requests as rq
import re
import threading


class MovieScraper:

    def __init__(self, movie_id):

        self.movie_id = movie_id

        uml = f'https://www.imdb.com/title/{self.movie_id}/'
        result = rq.get(uml)
        self.doc = bs(result.text,"html.parser")

    def get_movie_name(self):

        h1 = self.doc.find('h1')
        return h1.text.strip()

    def get_year(self):

        li = self.doc.find('li', {'role':'presentation'})

        a = li.find('a')

        if a is None:
            return

        return a.text.strip()

    def get_rating(self):

        regex = re.compile('.*AggregateRatingButton.*')

        span = self.doc.find('span', class_=regex)

        if span is None:
            return

        return span.text.strip()

    def get_genres(self):

        genres = []

        a_genres = self.doc.find_all('a',class_='GenresAndPlot__GenreChip-cum89p-3 fzmeux ipc-chip ipc-chip--on-baseAlt')
        for gen in a_genres:
            genre= gen.find('span', class_='ipc-chip__text').text
            genres.append(genre)
        return genres


class ActorScraper:

    def __init__(self, actor_id):
        self.actor_id = actor_id

        uml=f'https://www.imdb.com/name/{self.actor_id}/bio?ref_=nm_ov_bio_sm'
        result = rq.get(uml)

        self.doc = bs(result.text,"html.parser")

    def get_birth_date(self):
        return self.doc.find("time")["datetime"]

    def get_birth_name(self):
        table = self.doc.find('table', id='overviewTable')
        birth_name=table.find('td',text='Birth Name')

        if birth_name is None:
            return

        return birth_name.find_next_sibling().text.strip()

    def get_nickname(self):
        table = self.doc.find('table', id='overviewTable')
        nickname=table.find('td',text='Nickname')

        if nickname is None:
            return

        return nickname.find_next_sibling().text.strip()

    def get_name(self):
         return self.doc.find('h3').findChild().text.strip()

    def get_hight(self):

        table = self.doc.find('table', id='overviewTable')

        height=table.find('td',text='Height')

        if height is None:
            return
        return height.find_next_sibling().text.strip()

    def get_born_place(self):

        table = self.doc.find('table', id='overviewTable')

        place = table.find_all('a')[2]

    def get_pic_link(self):
        img = self.doc.find('img', class_='poster')
        return img['src']

    def get_mini_bio(self):
        div=self.doc.find('div', class_='soda odd')
        bio = div.findChild().text
        return bio




def get_actor_movie_ids(actor_id):
    actor_movie_ids=[]

    uml = f'https://www.imdb.com/name/{actor_id}/'
    result = rq.get(uml)
    doc = bs(result.text, "html.parser")


    actor_div = doc.find('div', class_='filmo-category-section')

    odd = actor_div.find_all('div', class_='filmo-row odd')
    even = actor_div.find_all('div', class_='filmo-row even')
    movie_list = []
    movie_list.extend(odd)
    movie_list.extend(even)

    for movie_id in movie_list:
        movie_imdb_id = re.findall('tt[0-9][0-9][0-9][0-9][0-9][0-9][0-9]', movie_id['id'])[0]
        actor_movie_ids.append(movie_imdb_id)

    return actor_movie_ids



def get_top50_actor_ids():

    actor_ids = []
    uml = f'https://www.imdb.com/list/ls053501318/'

    result = rq.get(uml)
    open('actors.html','wb').write(result.content);
    top_50_actor_html=open('actors.html','r')
    doc = bs(top_50_actor_html,"html.parser")

    top_50_list = doc.find_all("div",{'class':'lister-item mode-detail'})

    for item in top_50_list:
        a_tag = item.find('a')

        # get imdb id with regex expression , for example nm0000136 -> Johnny Depp
        imdb_actor_id = re.findall('nm[0-9][0-9][0-9][0-9][0-9][0-9][0-9]',a_tag['href'])[0]
        actor_ids.append(imdb_actor_id)

    return actor_ids


def scrape_movies_df(actor_ids):

    columns = ['actor_id','movie_id','name','year','rating','genres']
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
            print(row)

    df = pd.DataFrame(rows,columns=columns)
    df.to_csv('movies.csv',index=False)







def scrape_actors_df(actor_ids):

    columns = ['imdb_id', 'name', 'pic_link', 'pos', 'birth_name', 'birth_date', 'nickname', 'hight','bio']
    rows = []

    for pos,actor_id in enumerate(actor_ids,start=1):

        row = []
        actor_scraper = ActorScraper(actor_id)

        row.append(actor_id)

        row.append((actor_scraper.get_name()))

        row.append(actor_scraper.get_pic_link())

        row.append(pos)

        row.append(actor_scraper.get_birth_name())

        row.append(actor_scraper.get_birth_date())

        row.append(actor_scraper.get_nickname())

        row.append(actor_scraper.get_hight())

        row.append(actor_scraper.get_mini_bio())

        rows.append(row)

    df = pd.DataFrame(rows,columns=columns)
    df.to_csv('actors.csv',index=False)




def start_scraping():
    print('Start scraping ...')
    actor_ids = get_top50_actor_ids()

    #scrape_actors_df(actor_ids)
    #print('finished with actors')

    scrape_movies_df(actor_ids)
    print('finished with movies')


    print('Scraping finished')












