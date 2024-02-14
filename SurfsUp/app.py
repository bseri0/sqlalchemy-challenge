# Import the dependencies.

from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from datetime import datetime as dt, timedelta
import numpy as np
import pandas as pd

#################################################
# Database Setup
#################################################


# reflect an existing database into a new model

# Database setup (adjust the database URI)
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(autoload_with=engine)
#Base.prepare(engine, reflect=True)


# Create our session (link) from Python to the DB
session = Session(engine)
measurement = Base.classes.measurement
station = Base.classes.station
#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )
# Define other routes as per your analysis above, using session to query the database and jsonify to return JSON data


@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    # Calculate the date 1 year ago from the last data point in the database
    max_date = session.query(func.max(measurement.date)).scalar()
    max_date = dt.strptime(max_date, "%Y-%m-%d")
    one_year_ago = max_date - timedelta(days=365)
    
    # Perform a query to retrieve the data and precipitation scores
    results = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >= one_year_ago).all()
    
    # Convert the query results to a dictionary using date as the key and prcp as the value
    precipitation_dict = {date: prcp for date, prcp in results}
    return jsonify(precipitation_dict)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
   #all_stations = session.query(measurement.station).all()
    all_stations = session.query(station.name.distinct()).all()   
    stations_list = list(np.ravel(all_stations))
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    most_active_station_id = 'USC00519281'
    session = Session(engine)
    # Assuming you have a variable `most_active_station_id` holding the ID of the most active station
    query_date = dt.date(2017, 8, 23) - timedelta(days=365)
    results = session.query(measurement.date, measurement.tobs).\
        filter(measurement.station == most_active_station_id).\
        filter(measurement.date >= query_date).all()
    tobs_list = list(np.ravel(results))
    return jsonify(tobs_list)


@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temp_stats(start, end=None):
    session = Session(engine)
    sel = [func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]
    if end:
        results = session.query(*sel).filter(measurement.date >= start).filter(measurement.date <= end).all()
    else:
        results = session.query(*sel).filter(measurement.date >= start).all()
    temps = list(np.ravel(results))
    return jsonify(temps)

if __name__ == '__main__':
    app.run(debug=True)