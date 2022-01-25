import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save references to the tables
Station = Base.classes.station
Measurement = Base.classes.measurement

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    return (
        f"<b>Welcome to the Climate App!</b><br/>"
        f"<br/>"
        f"<i><b>Available Routes:</b></i><br/>"
        f"/api/v1.0/precipitation - Return dictionary of precipitation measurements for all dates.<br/>"
        f"/api/v1.0/stations - Return list of stations.<br/>"
        f"/api/v1.0/tobs - Return a list of temperature observations for the last year from the most active station, USC00519281.<br/>"
        f"/api/v1.0/<i>start_date</i> - Return minimum temperature, average temperature, and max temperature for all dates between selected date and most recent date (use format yyyy-mm-dd).<br/>"
        f"/api/v1.0/<i>start_date</i>/<i>end_date</i> - Return minimum temperature, average temperature, and max temperature for all dates in selected date range (use format yyyy-mm-dd).<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return precipitation dictionary as JSON."""
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()
    all_prcp_measurements = []
    for date, prcp in results:
        prcp_dict = {date: prcp}
        all_prcp_measurements.append(prcp_dict)
    return jsonify(all_prcp_measurements)

@app.route("/api/v1.0/stations")
def stations():
    """Return JSON list of stations."""
    session = Session(engine)
    results = session.query(Station.station).all()
    session.close()
    station_list = list(np.ravel(results))
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a JSON list of temperature observations for the last year from the most active station."""
    session = Session(engine)
    most_recent = dt.date(2017,8,18)
    year_prior = most_recent - dt.timedelta(days=365)
    results = session.query(Measurement.tobs).filter(Measurement.station == 'USC00519281').filter(Measurement.date >= year_prior).filter(Measurement.date <= most_recent).all()
    session.close()
    tobs_list = list(np.ravel(results))
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def start_date(start):
    """Return minimum temperature, the average temperature, and the max temperature for all dates between selected date and most recent date."""
    session = Session(engine)
    most_recent_date = dt.date(2017,8,23)
    start_date_dt = dt.datetime.strptime(start,'%Y-%m-%d')
    TMIN = session.query(Measurement.tobs).filter(Measurement.date >= start_date_dt).filter(Measurement.date <= most_recent_date).order_by(Measurement.tobs.asc()).first()
    TMAX = session.query(Measurement.tobs).filter(Measurement.date >= start_date_dt).filter(Measurement.date <= most_recent_date).order_by(Measurement.tobs.desc()).first()
    TAVG = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start_date_dt).filter(Measurement.date <= most_recent_date).first()
    tmin_list = list(np.ravel(TMIN))
    tmax_list = list(np.ravel(TMAX))
    tavg_list = list(np.ravel(TAVG))
    return jsonify("Minimum temperature:",tmin_list,"Maximum temperature:",tmax_list,"Average temperature:",tavg_list)

@app.route("/api/v1.0/<start>/<end>")
def start_end_range(start,end):
    """Return minimum temperature, the average temperature, and the max temperature for all dates in selected date range."""
    session = Session(engine)
    most_recent_date = dt.date(2017,8,23)
    start_date_dt = dt.datetime.strptime(start,'%Y-%m-%d')
    end_date_dt = dt.datetime.strptime(end,'%Y-%m-%d')
    TMIN = session.query(Measurement.tobs).filter(Measurement.date >= start_date_dt).filter(Measurement.date <= end_date_dt).order_by(Measurement.tobs.asc()).first()
    TMAX = session.query(Measurement.tobs).filter(Measurement.date >= start_date_dt).filter(Measurement.date <= end_date_dt).order_by(Measurement.tobs.desc()).first()
    TAVG = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start_date_dt).filter(Measurement.date <= end_date_dt).first()
    tmin_list = list(np.ravel(TMIN))
    tmax_list = list(np.ravel(TMAX))
    tavg_list = list(np.ravel(TAVG))
    return jsonify("Minimum temperature:",tmin_list,"Maximum temperature:",tmax_list,"Average temperature:",tavg_list)

if __name__ == "__main__":
    app.run(debug=True)
