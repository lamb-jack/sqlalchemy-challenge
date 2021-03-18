
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create session from Python to the DB
session = Session(engine)

# Flask Setup
app = Flask(__name__)

# * Home page.
# * List all routes that are available.
@app.route("/")
def Home():
    return (
        f"Welcome! Here are the available routes:<br>"
        f"(If an error shows up try refreshing ^^')<br>"
        f"<br>"
        f"Last 12 months of precipitation data starting from the most recent data point in the database:<br>"
        f"/api/v1.0/precipitation<br>"
        f"<br>"
        f"List of stations from the dataset:<br>"
        f"/api/v1.0/stations<br>"
        f"<br>"
        f"Dates and temperature observations of the most active station for the last year of data:<br>"
        f"/api/v1.0/tobs<br>"
        f"<br>"
        f"`TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date:<br>"
        f"/api/v1.0/<start><br>"
        f"<br>"
        f"`TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive:<br>"
        f"/api/v1.0/<start>/<end><br>"
        )

# * Convert the query results to a dictionary using `date` as the key and `prcp` as the value.
# * Return the JSON representation of your dictionary.

@app.route("/api/v1.0/precipitation")
def precipitation():

    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    last_12 = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago).order_by(Measurement.date).all()

    dictionary = {}
    for i in last_12:
        dictionary[str(i.date)] = i.prcp
    
    return jsonify(dictionary)

# * `/api/v1.0/stations`
# * Return a JSON list of stations from the dataset.

@app.route("/api/v1.0/stations")
def stations():
    stations_list = session.query(Station.station)
    stations_pd = pd.read_sql(stations_list.statement, stations_list.session.bind)
    return jsonify(stations_pd.to_dict())


# * `/api/v1.0/tobs`
# * Query the dates and temperature observations of the most active station for the last year of data.
# * Return a JSON list of temperature observations (TOBS) for the previous year.

@app.route("/api/v1.0/tobs")
def tobs():
    most_active_one = session.query(Measurement.station).group_by(Measurement.station)\
                        .order_by(func.count(Measurement.station).desc()).first()
    # to get it as a string
    for i in most_active_one:
        MAO = i
    
    most_active_temp = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == MAO).all()

    return jsonify(most_active_temp)

# * `/api/v1.0/<start>` and `/api/v1.0/<start>/<end>`
# * Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# * When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.
# * When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.

@app.route("/api/v1.0/<start>")
def start(start):
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    end_date =  dt.date(2017, 8, 23)

    temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
                .filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    temps_data = list(np.ravel(temps))

    return jsonify(temps_data)

@app.route("/api/v1.0/<start>/<end>")
def range(start,end):   
    start_date= dt.datetime.strptime(start, '%Y-%m-%d')
    end_date= dt.datetime.strptime(end,'%Y-%m-%d')
    
    temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
                    .filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    temps_data = list(np.ravel(temps))
    
    return jsonify(temps_data)


if __name__ == "__main__":
    app.run(debug=True)