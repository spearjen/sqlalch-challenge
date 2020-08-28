# import 
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc
import datetime as dt
from datetime import date

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

# Create an app
app = Flask(__name__)

# Define what to do when a user hits the index route
@app.route("/")
def home():
    return (
        f"<b>Available Routes</b></br>"
        "</br>"
        f"Preciptitation data for all dates in dataset: /api/v1.0/precipitation</br>"
        "</br>"
        f"Station names: /api/v1.0/stations</br>"
        "</br>"
        f"Temperature data for last year of available data: /api/v1.0/tobs</br>"
        "</br>"
        f"Temperature summary for a single date: /api/v1.0/yyyy-mm-dd</br>"
        f"To get single date information, enter a date after the last slash to see temperature min, max, avg on that date. For example, /api/v1.0/2017-04-20, gives data for March 20, 2017.</br>"
        "</br>"
        f"Temperature summary for a date range: /api/v1.0/yyyy-mm-dd/yyyy-mm-dd</br>"
        f"To get a date range, enter a start date after the last provided slash, then add a slash and provide an end date to see temperature min, max, avg for the date range. For example, \
        /api/v1.0/2017-04-20/2017-04-30, returns data for the date range March 20-30, 2017.</br>"
        "</br>"
        f"Be sure to format dates as yyyy-mm-dd!"
    )

# Define what to do when a user hits the /api/v1.0/precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).all()
    data = {row[0]:row[1] for row in results}
    session.close()
    return jsonify(data)

# # Define what to do when a user hits the /api/v1.0/stations route Return a JSON list of stations from the dataset
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station).all()
    data = [row[0] for row in results]
    session.close()
    return jsonify(data)

# # Define what to do when a user hits the /tobs route
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    end_date, = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    begin_date=dt.datetime.strptime(end_date, '%Y-%m-%d')-dt.timedelta(days=365)
    end_date = dt.datetime.strptime(end_date, '%Y-%m-%d')
    most_active_yr = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station)\
    .filter(Measurement.date>=begin_date).filter(Measurement.date<=end_date)\
    .order_by(func.count(Measurement.station).desc()).all()[0][0]

    results = session.query(Measurement.tobs).filter\
    (Measurement.station == most_active_yr).filter(Measurement.date>=begin_date).filter\
    (Measurement.date<=end_date).all()
    data = [row[0] for row in results]
    session.close()
    return jsonify(data)

@app.route("/api/v1.0/<start>")
def start_date(start):
    session = Session(engine)
    max4_start_date, = session.query(func.max(Measurement.tobs).filter(Measurement.date==start)).all()
    min4_start_date, = session.query(func.min(Measurement.tobs).filter(Measurement.date==start)).all()
    avg4_start_date, = session.query(func.avg(Measurement.tobs).filter(Measurement.date==start)).all()

    session.close()

    return(
        f"You chose {start}.</br>"
        f"</br>"
        f"Minimum temperature for date:  {min4_start_date[0]}</br>"
        f"Maximum temperature for date:  {max4_start_date[0]}</br>"
        f"Average temperature for date:  {avg4_start_date[0]}")

@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    session = Session(engine)
    session.query(Measurement.date, Measurement.tobs).filter(Measurement.date>=start).filter(Measurement.date<=end).all()
    min4_start_end, = session.query(func.min(Measurement.tobs)).all()
    max4_start_end, = session.query(func.max(Measurement.tobs)).all()
    avg4_start_end, = session.query(func.avg(Measurement.tobs)).all()
    session.close()

    return(
        f"You chose {start} to {end}.</br>"
        f"</br>"
        f"Minimum temperature for date range:  {min4_start_end[0]}</br>"
        f"Maximum temperature for date range:  {max4_start_end[0]}</br>"
        f"Average temperature for date range:  {avg4_start_end[0]}")

if __name__ == '__main__':
    app.run(debug=True)
