import pandas as pd
from flask import Flask, redirect, url_for, render_template
import pathlib
from main import get_all_actor_info


app = Flask(__name__)

def list_to_str(list ):
    s = ""
    for i,item in enumerate(list):
        s = s+str(item)
        if(i != len(list)-1):
            s = s+', '
    return s

@app.route("/Top50/<actor_id>")
def detail(actor_id):

    if actor_id not in actors_dict.keys():
        return redirect(url_for('home'))

    actor=actors_dict[actor_id]
    actor.load_movies()

    return render_template("actorDetail.html", actor=actor)

@app.route("/")
@app.route("/Top50")
def home():

    actors = actors_dict.values()

    for a in actors:
        if pd.isna(a.nickname):
            a.nickname='None'
        if pd.isna(a.birth_name):
            a.birth_name = a.name
        if pd.isna(a.birth_date):
            a.birth_date = 'None'
        if pd.isna(a.hight):
            a.hight = 'None'

    return render_template("index.html", actors = actors)

actors_dict={}

if __name__ == "__main__":

    #load actor list to dict
    for a in get_all_actor_info():
        actors_dict[a.imdb_id] = a

    app.run(host='localhost', port=8080)
