import numpy as np
import os

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt
from dateutil.relativedelta import relativedelta

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save reference to the table
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
    print("Server received request for 'Home' page...")
    return (
        f"Welcome to the 'Home' page!<br/><br/>"
        f"Routes Available:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
        )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Convert query results to a dictionary using date as 
    # the key and prcp as the value. Return in JSON format
    print("Server received request for '/api/v1.0/precipitation' page...")

    # Query all precipitations
    session = Session(engine)
    results = session.query(measurement.date, measurement.prcp).order_by(measurement.date).all()

    # close the session to end the communication with the database
    session.close()

    # Append all data into a list
    all_date = []
    for date, prcp in results:
        measurement_dict = {}
        measurement_dict[date] = prcp
        all_date.append(measurement_dict)

    return jsonify(all_date)

@app.route("/api/v1.0/stations")
def stations():
    # Return a JSON list of stations from the dataset.
    print("Server received request for '/api/v1.0/stations' page...")

    # Query
    session = Session(engine)
    results = session.query(station.station, station.name).all()

    # close the session to end the communication with the database
    session.close()

    # Append all data into a list
    lst = []
    for stat, name in results:
        station_dict = {}
        station_dict[stat] = name
        lst.append(station_dict)

    return jsonify(lst)

@app.route("/api/v1.0/tobs")
def tobs():
    # Return a JSON list of temperature observations (TOBS) for the previous year.
    print("Server received request for '/api/v1.0/tobs' page...")
    
    # Query
    session = Session(engine)
    query_date = dt.date(2017, 8, 23) - relativedelta(months = 12)
    results = session.query(measurement.date, measurement.tobs).filter(measurement.station == 'USC00519281')\
    .filter(measurement.date >= query_date).all()

    # close the session to end the communication with the database
    session.close()

    # Create JSON
    lst = []
    for date, tmp in results:
        tobs_dict = {}
        tobs_dict[date] = tmp
        lst.append(tobs_dict)

    return jsonify(lst)

@app.route("/api/v1.0/<start>")
def start_date(start):
    # calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
    print("Server received request for '/api/v1.0/<start>' page...")
    
    # Query
    session = Session(engine)
    results = session.query(measurement.date, func.min(measurement.tobs), func.max(measurement.tobs), \
    func.avg(measurement.tobs)).filter(measurement.date >= start).group_by(measurement.date).all()

    # close the session to end the communication with the database
    session.close()

    # Create JSON
    lst = []
    for date, min, max, avg in results:
        start_dict = {}
        start_dict['Start Date'] = date
        start_dict['Min. Temp.'] = min
        start_dict['Max. Temp.'] = max
        start_dict['Avg. Temp.'] = round(avg, 1)
        lst.append(start_dict)

    print(lst[:5])

    return jsonify(lst)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    # When given the start and the end date, calculate the TMIN, TAVG, 
    # and TMAX for dates between the start and end date inclusive.
    print("Server received request for '/api/v1.0/<start>/<end>' page...")
    
    # Query
    session = Session(engine)
    results = session.query(measurement.date, func.min(measurement.tobs), func.max(measurement.tobs),\
    func.avg(measurement.tobs)).filter(measurement.date >= start, measurement.date <= end).group_by(measurement.date).all()



    # close the session to end the communication with the database
    session.close()

    # Create JSON
    lst = []
    for date, min, max, avg in results:
        s_e_dict = {}
        s_e_dict['Date'] = date
        s_e_dict['Min. Temp.'] = min
        s_e_dict['Max. Temp.'] = max
        s_e_dict['Avg. Temp.'] = round(avg, 1)
        lst.append(s_e_dict)
    return jsonify(lst)
    

# Run application
if __name__ == "__main__":
    app.run(debug=True)
