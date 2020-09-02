import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of all prcp names"""
    # Query all prcp
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= '2016-10-01').\
        group_by(Measurement.date).all()

    all_precipitation = []

    # Query for the dates and temperature observations from the last year.
    for result in results:
        precipitation_dict = {}
        precipitation_dict["date"] = result[0]
        precipitation_dict["prcp"] = result[1]
        all_precipitation.append(precipitation_dict)
    
    return jsonify(all_precipitation)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of all the stations"""
    # Query all stations
    results = session.query(Measurement.station).group_by(Measurement.station).all()
    all_sessions = list(np.ravel(results))
    return jsonify(all_sessions)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of temperature observations (tobs) for the previous year"""
    # Query all tobs for the previous year
    results = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.date >= '2016-10-01').all()

    all_tobs = []

    for result in results:
        tobs_dict = {}
        tobs_dict["date"] = result[0]
        tobs_dict["tobs"] = result[1]
        all_tobs.append(tobs_dict)
    return jsonify(all_tobs)

@app.route("/api/v1.0/<start>")
def start(start):
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a given start date"""
    year, month, date = map(int, start.split('-'))
    date_start = dt.date(year,month,date)
    # Query for tobs of defined start date
    results = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs).\
                            func.avg(Measurement.tobs)).filter(Measurement.date >= date_start).all()
    data = list(np.ravel(results))
    return jsonify(data)

@app.route("/api/v1.0/<start>/<end>")
def range_temp(start,end):
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given range"""
    year, month, date = map(int, start.split('-'))
    date_start = dt.date(year,month,date)
    year2, month2, date2 = map(int, end.split('-'))
    date_end = dt.date(year2,month2,date2)
    # Query for tobs for defined date range
    results = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs).\
                            func.avg(Measurement.tobs)).filter(Measurement.date >= date_start).filter(Measurement.date <= date_end).all()
    data = list(np.ravel(results))
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)