import pandas as pd
from flask import Flask, redirect, url_for, render_template
import numpy as np

from main import get_all_actor_info
from matplotlib.figure import Figure
import base64
from io import BytesIO

app = Flask(__name__)


def rating_years_plot(actor):
    avg_per_year_df = actor.calc_average_for_all_years()

    x = avg_per_year_df['year']
    y = avg_per_year_df['rating']

    fig = Figure(figsize=(7.5,5))
    ax = fig.subplots()

    ax.plot(x, y)
    ax.set_title(f'Average of {actor.name}s movie rating per year')
    ax.set_ylabel(f'Rating')
    ax.set_xlabel('year')
    ax.figure.autofmt_xdate()

    buf = BytesIO()
    fig.savefig(buf, format='png')

    data = base64.b64encode(buf.getbuffer()).decode('ascii')

    return data


@app.route("/Top50/<actor_id>")
def detail(actor_id):
    if actor_id not in actors_dict.keys():
        return redirect(url_for('home'))

    actor = actors_dict[actor_id]
    actor.load_movies()
    actor.load_awards()

    avg_over_all = round(actor.calc_average_rating_aver_all(), 1)
    top_5_movies = actor.get_top_X_movies(5)
    genres = actor.get_all_unique_movie_genres()


    return render_template("actorDetail.html", actor=actor,
                           avg_over_all=avg_over_all, top_5_movies=enumerate(top_5_movies,start=1),
                           genres=list(genres), rating_all_years=rating_years_plot(actor), np=np, pd=pd)




@app.route("/")
@app.route("/Top50")
def home():
    actors = actors_dict.values()

    for actor in actors:
        if pd.isna(actor.nickname):
            actor.nickname = 'None'
        if pd.isna(actor.birth_name):
            actor.birth_name = actor.name
        if pd.isna(actor.birth_info):
            actor.birth_info = 'None'
        if pd.isna(actor.hight):
            actor.hight = 'None'

    return render_template("index.html", actors=actors)


actors_dict = {}

if __name__ == "__main__":

    # load actor list to dict
    for a in get_all_actor_info():
        actors_dict[a.imdb_id] = a

    # start webapp on localhost:8080
    app.run(host='localhost', port=8080)
