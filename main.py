
from bs4 import BeautifulSoup as bs, ResultSet
import requests as rq
import re


class Movie:

    def __init__(self, imdb_id):
        self.imdb_id = imdb_id

    def get_movie_name(self):

        uml = f'https://www.imdb.com/title/{self.imdb_id}/'
        result = rq.get(uml)
        doc = bs(result.text,'html.parser')

        h1 = doc.find('h1')
        return h1.text.strip()

    def get_year(self):
        uml = f'https://www.imdb.com/title/{self.imdb_id}/'
        result = rq.get(uml)
        doc = bs(result.text,'html.parser')

        li = doc.find('li', {'role':'presentation'})

        a = li.find('a')
        return a.text.strip()

    def get_rating(self):
        uml = f'https://www.imdb.com/title/{self.imdb_id}/'
        result = rq.get(uml)
        doc = bs(result.text,'html.parser')

        regex = re.compile('.*AggregateRatingButton.*')

        span = doc.find('span', class_= regex)

        if span is None:
            return

        return span.text.strip()

    def get_genres(self):
        uml = f'https://www.imdb.com/title/{self.imdb_id}/'
        result = rq.get(uml)
        doc = bs(result.text,'html.parser')

        genres = []

        a_genres = doc.find_all('a',class_='GenresAndPlot__GenreChip-cum89p-3 fzmeux ipc-chip ipc-chip--on-baseAlt')
        for gen in a_genres:
            genre= gen.find('span', class_='ipc-chip__text').text
            genres.append(genre)
        return genres




class Award:

    def __init__(self,award_imdb_id, year, outcome, description):
        self.award_imdb_id = award_imdb_id
        self.year = year
        self.outcome = outcome
        self.description = description

    def get_award_name(self):
        uml =f'https://www.imdb.com/event/{self.award_imdb_id}/{self.year}/1'
        result = rq.get(uml)

        doc = bs(result.text,'html.parser')

        name = doc.find('h1').text.strip()

        return name







class Actor:

    def __init__(self, name , pic, pos, imdb_id ):
        self.name=name
        self.pic=pic
        self.pos=pos
        self.imdb_id=imdb_id



    def __str__(self):
        return f'actor(name={self.name}, pic={self.pic}, pos={self.pos}, imdb_id= {self.imdb_id} )'

    def __repr__(self):
        return f'actor(name={self.name}, pic={self.pic}, pos={self.pos}, imdb_id= {self.imdb_id} )'

    def get_birth_date(self):
        uml=f'https://www.imdb.com/name/{self.imdb_id}/bio?ref_=nm_ov_bio_sm'

        result = rq.get(uml)
        doc = bs(result.text,"html.parser")
        return doc.find("time")["datetime"]

    def get_birth_name(self):
        uml = f'https://www.imdb.com/name/{self.imdb_id}/bio?ref_=nm_ov_bio_sm'
        result = rq.get(uml)
        doc = bs(result.text, "html.parser")

        table = doc.find('table', id='overviewTable')
        birth_name=table.find('td',text='Birth Name')

        if birth_name is None:
            return

        return birth_name.find_next_sibling().text.strip()

    def get_nickname(self):
        uml = f'https://www.imdb.com/name/{self.imdb_id}/bio?ref_=nm_ov_bio_sm'
        result = rq.get(uml)
        doc = bs(result.text, "html.parser")

        table = doc.find('table', id='overviewTable')

        nickname=table.find('td',text='Nickname')

        if nickname is None:
            return

        return nickname.find_next_sibling().text.strip()

    def get_hight(self):
        uml = f'https://www.imdb.com/name/{self.imdb_id}/bio?ref_=nm_ov_bio_sm'
        result = rq.get(uml)
        doc = bs(result.text, "html.parser")

        table = doc.find('table', id='overviewTable')

        height=table.find('td',text='Height')

        if height is None:
            return
        return height.find_next_sibling().text.strip()

    def get_born_place(self):
        uml = f'https://www.imdb.com/name/{self.imdb_id}/bio?ref_=nm_ov_bio_sm'
        result = rq.get(uml)
        doc = bs(result.text, "html.parser")

        table = doc.find('table', id='overviewTable')

        place = table.find_all('a')[2]

        return place.text.strip()

    def get_movies(self):

        uml = f'https://www.imdb.com/name/{self.imdb_id}/'
        result = rq.get(uml)
        doc = bs(result.text, "html.parser")

        movies = []

        actor_div = doc.find('div', class_='filmo-category-section')

        odd = actor_div.find_all('div', class_= 'filmo-row odd')
        even = actor_div.find_all('div', class_= 'filmo-row even')
        movie_list = []
        movie_list.extend(odd)
        movie_list.extend(even)

        for movie_id in movie_list:
            movie_imdb_id = re.findall('tt[0-9][0-9][0-9][0-9][0-9][0-9][0-9]', movie_id['id'])[0]
            movie = Movie(movie_imdb_id)
            movies.append(movie)

        return movies

    def get_awards(self):
        uml=f'https://www.imdb.com/name/{self.imdb_id}/awards?ref_=nm_awd'
        result = rq.get(uml)
        doc = bs(result.text, "html.parser")
        awards = []



        tables = doc.find_all('table', class_='awards')

        for table in tables:
            tr = table.find('tr')

            # get award year
            td = tr.find('td',class_='award_year')
            a =td.find('a')
            award_imdb_id = re.findall('ev[0-9][0-9][0-9][0-9][0-9][0-9][0-9]',a['href'])[0]

            year = a.text.strip()

            td=tr.find('td',class_='award_outcome')
            b=td.find('b')
            outcome=b.text.strip()

            td = tr.find('td', class_='award_description')
            description = td.text

            award = Award(award_imdb_id,year,outcome,description)

            awards.append(award)
        return awards



def get_top50_actors(uml):


    result = rq.get(uml)
    open('actors.html','wb').write(result.content);

    top_50_actor_html=open('actors.html','r')

    doc = bs(top_50_actor_html,"html.parser")
    top_50_list = doc.find_all("div",{'class':'lister-item mode-detail'})

    actors=[]
    pos = 0
    for item in top_50_list:

        a_tag = item.find('a')
        img = a_tag.find('img')

        alt = img['alt']
        src = img['src']
        # get imdb id with regex expression , for example nm0000136 -> Johnny Depp
        imdb_id = re.findall('nm[0-9][0-9][0-9][0-9][0-9][0-9][0-9]',a_tag['href'])[0]

        name = alt
        pic_link = src
        pos += 1
        a = Actor(name=name, pos=pos, pic=pic_link, imdb_id=imdb_id)
        actors.append(a)


    return actors



if __name__=='__main__':
    uml = f'https://www.imdb.com/list/ls053501318/'
    actors = get_top50_actors(uml)

    for actor in  actors:
        print(actor.get_birth_name())


    #movies = actors[0].get_movies()



    #for movie in movies:
     #   print(movie.get_genres())


