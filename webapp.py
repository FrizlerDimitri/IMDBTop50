from flask import Flask, redirect, url_for, render_template
import pathlib
from main import get_all_actor_info


app = Flask(__name__)

def dostuff():
    return "abcedfghijklmnop"



@app.route("/")
@app.route("/Top50")
def home():

    actors = get_all_actor_info()

    return render_template("index.html", actors = actors)


if __name__ == "__main__":
    app.run(host='localhost', port=80)
