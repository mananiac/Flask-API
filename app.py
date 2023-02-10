from flask import Flask, request, make_response, g,  render_template,  jsonify 
import pandas 
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from flask_migrate import Migrate
import os
from csv import reader
import datetime as datetime
from flask import request

db = pandas.read_csv("DivvyChallenge.csv")
# db = open("DivvyChallenge.csv","r")
engine = create_engine('sqlite:///DivvyChallenge.db', echo=True)
# sqlite_connection = engine.raw_connection()
sqlite_table = "Trips"
db.to_sql(sqlite_table,engine,if_exists='append')
# engine.close()

class Config():
    SQLALCHEMY_DATABASE_URI = "sqlite:///DivvyChallenge.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

app = Flask(__name__)
app.config.from_object(Config)
db= SQLAlchemy(app)
migrate=Migrate(app,db)

class Trips(db.Model):
    trip_id = db.Column(db.Integer, primary_key=True)
    starttime = db.Column(db.DateTime)
    stoptime = db.Column(db.DateTime)
    bikeid = db.Column(db.Integer)
    from_station_id = db.Column(db.Integer)
    from_station_name = db.Column(db.String)
    to_station_id = db.Column(db.Integer)
    to_station_name = db.Column(db.String)
    usertype	= db.Column(db.String)
    trip_duration = db.Column(db.Integer)
    


@app.before_first_request
def create_tables():
    db.create_all()

@app.route("/")
def home():
    return render_template("home.html")

@app.get('/trips')
def get_average_trip_time():

    start = request.args.get('starttime')
    stop = request.args.get('endtime')
    from_station_id = request.args.get('from_station_id')
    to_station_id = request.args.get('to_station_id')
   
    if (from_station_id and to_station_id):
        from_station_name = Trips.query.filter(Trips.from_station_id == from_station_id).first().from_station_name
        to_station_name = Trips.query.filter(Trips.to_station_id == to_station_id).first().to_station_name
        valid_rows = Trips.query.filter(Trips.from_station_id == from_station_id,
                                        Trips.to_station_id == to_station_id,
                                        Trips.starttime >= datetime.datetime.strptime(start, '%Y-%m-%d'),
                                        Trips.stoptime <= datetime.datetime.strptime(stop, '%Y-%m-%d') ).all()
        # print(valid_rows)


    elif from_station_id:
        from_station_name = Trips.query.filter(Trips.from_station_id == from_station_id).first().from_station_name
        valid_rows = Trips.query.filter(Trips.from_station_id == from_station_id, 
                                            Trips.starttime >= datetime.datetime.strptime(start, '%Y-%m-%d'),
                                            Trips.stoptime <= datetime.datetime.strptime(stop, '%Y-%m-%d') ).all()
    else:

        valid_rows = Trips.query.filter(Trips.starttime >= datetime.datetime.strptime(start, '%Y-%m-%d'),
                                            Trips.stoptime <= datetime.datetime.strptime(stop, '%Y-%m-%d') ).all()
        

    avg_duration = sum(record.trip_duration for record in valid_rows) / len(valid_rows)

    if from_station_id and to_station_id :
        return jsonify({
            'averageDuration': avg_duration,
            'fromStationId': from_station_id,
            'fromStationName': from_station_name,
            'toStationId': to_station_id,
            'toStationName': to_station_name

        })
    elif from_station_id:
        return jsonify({
            'averageDuration': avg_duration,
            'fromStationId': from_station_id,
            'fromStationName': from_station_name
        })
    else:
        return jsonify({
            'averageDuration': avg_duration
        })

@app.get('/tripsbike')    
def get_average_trip_time_bike():
    start = request.args.get('starttime')
    stop = request.args.get('endtime')
    bike_id = request.args.get('bike_id')

    valid_rows = Trips.query.filter(Trips.bikeid == bike_id, 
                                    Trips.starttime >= datetime.datetime.strptime(start, '%Y-%m-%d'),
                                    Trips.stoptime <= datetime.datetime.strptime(stop, '%Y-%m-%d') ).all()

    avg_duration = sum(record.trip_duration for record in valid_rows) / len(valid_rows)

    # print(valid_rows)

    return jsonify({
            'bike_id': bike_id,
            'total trips' : len(valid_rows),
            'averageDuration': avg_duration
        })

if __name__ == "__main__":
    app.run(debug=True)
