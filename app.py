from flask import Flask, request, make_response, g,  render_template,  jsonify 
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from flask_migrate import Migrate
import os
import datetime as datetime
from flask import request

db = pd.read_csv("DivvyChallenge.csv")
engine = create_engine('sqlite:///DivvyChallenge.db', echo=True)
sqlite_connection = engine.connect()
sqlite_table = "Trips"
db.to_sql(sqlite_table, sqlite_connection)
sqlite_connection.close()

class Config():
    SQLALCHEMY_DATABASE_URI = "sqlite:///DivvyChallenge.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get("SQLALCHEMY_TRACK_MODIFICATIONS")
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
    
    def from_dict(self, data):
        self.trip_id = data['trip_id'],
        self.starttime = data['starttime'],
        self.stoptime = data['stoptime'],
        self.bikeid = data['bikeid'],
        self.from_station_id = data['from_station_id'],
        self.from_station_name = data['from_station_name'],
        self.to_station_id = data['to_station_id'],
        self.to_station_name = data['to_station_name'],
        self.usertype = data['usertype'],
        self.trip_duration = data['trip_duration']
    
    def to_dict(self):
        return {"trip_id ": self.trip_id
        , "starttime":self.starttime," stoptime":self.stoptime,
        "bikeid":self. bikeid,"from_station_id":self.from_station_id, 
        "from_station_name":self.from_station_name,"to_station_id":self.to_station_id, 
        "to_station_name":self.to_station_name,"usertype":self.usertype
        }



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
