from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
import requests
import sys

app = Flask(__name__)

# Configure SQLAlchemy ORM to the flask app
app.config['SQL_ALCHEMY_DATABASE_URI'] = "sqlite:///weather.sqlite3"
# db connection
db = SQLAlchemy(app)


# table city with its columns
class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)


# create db and tables
db.create_all()


# home page
@app.route('/')
def index():
    db_data = retrieve_data()
    return render_template('index.html', my_city=db_data)


# add city to our webpage
@app.route('/add', methods=['POST'])
def add_city():
    input_city = request.form.get('city_name').capitalize()
    api_response = get_api_data(input_city)['cod']
    if input_city is None or api_response == "404":
        flash("The city doesn't exist!")
    elif City.query.filter_by(name=input_city).first():
        flash("The city has already been added to the list!")
    else:
        new_city = City(name=input_city)
        db.session.add(new_city)
        db.session.commit()
    return redirect("/")


# delete city add from our webpage
@app.route("/delete/<city_id>", methods=['GET','POST'])
def delete(city_id):
    city = City.query.filter_by(id=city_id).first()
    db.session.delete(city)
    db.session.commit()
    return redirect('/')


def retrieve_data():
    cities = City.query.all()
    retrieved_data = []
    if cities:
        for city in cities:
            weather_info = {}
            weather_api_data = get_api_data(city.name)
            weather_info['id'] = city.id
            weather_info['city'] = city.name
            weather_info['state'] = weather_api_data['weather'][0]['main']
            weather_info['degree'] = weather_api_data['main']['temp']
            retrieved_data.append(weather_info)
    return retrieved_data


def get_api_data(city_name):
    api_key = "3d1a37a5047f8e437a214960dff29a67"
    res = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&units=metric")
    return res.json()


if __name__ == '__main__':
    app.secret_key = 'a4v6n73vverth'
    app.config['SESSION_TYPE'] = 'filesystem'

    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()
