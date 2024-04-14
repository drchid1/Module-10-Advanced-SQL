# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

from pathlib import Path

import datetime as dt

#################################################
# Database Setup
#################################################
database_path = Path("resources/hawaii.sqlite")
engine = create_engine(f"sqlite:///{database_path}")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

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
def start():
    """All available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp_summary/<start_date> or /api/v1.0/temp_summary/<start_date>/<end_date>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return precipitation data for the last 12 months"""
    # Find the most recent date in the data set.
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    # Calculate the date one year from the last date in data set.
    # Coverting Row Type to String and subsequently to Date
    date_value = recent_date.date
    date_obj = dt.date.fromisoformat(date_value)
    # Subtracting 1 year (365 days) from the queried 'recent date'
    year_from_date = date_obj - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    one_year_data = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= year_from_date).order_by(Measurement.date).all()

    # Closing session
    session.close()

    # Convert list of tuples into normal list
    one_year_precpitation_results = list(np.ravel(one_year_data))

    return jsonify(one_year_precpitation_results)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all stations"""
    # Query all stations
    stations = session.query(Station.station).distinct().all()
     
    # Closing session
    session.close()

    # Convert list of tuples into normal list
    station_results = list(np.ravel(stations))

    return jsonify(station_results)


@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all passenger names"""
    # Query for most active station
    sel = [Measurement.station, func.count(Measurement.station)]
    most_active_station = session.query(sel[0]).group_by(Measurement.station).order_by(sel[1].desc()).first()

    # Oldest date for this station
    oldest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    
    # Coverting Row Type to String and subsequently to Date
    date_value = oldest_date.date
    date_obj = dt.date.fromisoformat(date_value)
    
    # Subtracting 1 year (365 days) from the queried 'recent date'
    one_year_from_date = date_obj - dt.timedelta(days=365)

    # Query of 12 months temp data for specific station
    one_year_temp_data = session.query(Measurement.tobs).\
                     filter(Measurement.station == most_active_station).\
                     filter(Measurement.date >= one_year_from_date)

    # Closing session
    session.close()

    # Convert list of tuples into normal list
    temp_results = list(np.ravel(one_year_temp_data))

    return jsonify(temp_results)


@app.route("/api/v1.0/temp_summary/<start_date>/<end_date>")

# <start_date> and <start_date/end_date> run in one function
# by setting default end date to todays date if no <end_date> input
def temp_summary(start_date, end_date=dt.date.today()):

    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Retreive the specified date range else provide a error"""
    # Query for specified date range and 
    sel = [func.min(Measurement.tobs),
           func.max(Measurement.tobs),
           func.avg(Measurement.tobs)]
    temp_summary_stats = session.query(*sel).\
            filter(Measurement.date >= start_date).\
            filter(Measurement.date <= end_date)

    # Convert list of tuples into normal list
    temp_summary_results = list(np.ravel(temp_summary_stats))

    # Error Output
    if len(temp_summary_results) == 0:
        return jsonify({"error": "No data available for specified date range"}), 404


    return jsonify(temp_summary_results)


