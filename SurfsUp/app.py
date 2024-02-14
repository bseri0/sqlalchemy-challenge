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
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
#Base.prepare(autoload_with=engine)
Base.prepare(engine, reflect=True)

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
        f"http://localhost:5000/api/v1.0/precipitation<br/>"
        f"http://localhost:5000/api/v1.0/stations<br/>"
        f"http://localhost:5000/api/v1.0/tobs<br/>"
        f"http://localhost:5000/api/v1.0/temp/start/end"
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
    
    session.close()
    return jsonify(precipitation_dict)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(station.name).all()
    stations = list(np.ravel(results))
    #station_dict = {stations: name for name in results}
    session.close()
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():

    session = Session(engine)

    temperature_data = (
        session.query(measurement.date, measurement.prcp, measurement.tobs)
        .filter(measurement.station == 'USC00519281')
        .all()
)

    session.close

    all_temp_data = []
    # Create a dictionary from the row data and append to a list of last_12_list
    for date, prcp, tobs in temperature_data:
        temp_dict = {}
        temp_dict["Date"] = date
        temp_dict["Precipitation"] = prcp
        temp_dict["Tobs"] = tobs
        all_temp_data.append(temp_dict)

    return jsonify(all_temp_data)

@app.route("/api/v1.0/<start>")
def start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    start_date_tobs = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs))\
        .filter(Measurement.date >= start).all()
    session.close()

    start_tobs = []
    for min, max, avg in start_date_tobs:
        start_dict = {}
        start_dict['min_temp'] = min
        start_dict['max_temp'] = max
        start_dict['avg_temp'] = round(avg, 2)

        start_tobs.append(start_dict)

    return jsonify (f"Start date:{start}", (start_tobs))

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    start_end_date_tobs = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs))\
        .filter(Measurement.date >= start)\
        .filter(Measurement.date<= end).all()
    session.close()

    start_end_tobs = []
    for min, max, avg in start_end_date_tobs:
        start_dict = {}
        start_dict['min_temp'] = min
        start_dict['max_temp'] = max
        start_dict['avg_temp'] = round(avg, 2)

        start_end_tobs.append(start_dict)

    return jsonify (f"Start date:{start} // End date:{end}", (start_end_tobs))

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    sel = [func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]
    if not end:
        results = session.query(*sel).\
            filter(measurement.date >= start).\
            filter(measurement.date <= end).all()
        temps = list(np.ravel(results))
        return jsonify(temps)
    results = session.query(*sel).\
        filter(measurement.date >= start).\
        filter(measurement.date <= end).all()
    temps = list(np.ravel(results))
    return jsonify(temps = temps)

if __name__ == '__main__':
    app.run(debug=True)