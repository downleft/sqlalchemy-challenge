# Import the dependencies.
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Declare a Base using `automap_base()`
Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(autoload_with=engine)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station

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
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
        )

#Return 12 months of precipitation data
@app.route("/api/v1.0/precipitation")
def precipitation():

    # Create a session
    session = Session(engine)

    """Return last 12 months of precipitation data"""
    results = session.query(Measurement.date, Measurement.prcp).filter(func.strftime(Measurement.date) >= dt.date(2016, 8, 23)).all()

    session.close()

    # Create a dictionary from the row data and append to a list
    year_data = []
    for date, prcp in results:
        year_data_dict = {}
        year_data_dict["date"] = date
        year_data_dict["prcp"] = prcp
        year_data.append(year_data_dict)

    return jsonify(year_data)

#Return JSON list of stations
@app.route("/api/v1.0/stations")
def stations():

    # Create a session
    session = Session(engine)

    """Return a list of all stations"""
    # Query all stations
    results = session.query(Station.station).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

#Retrieve 12 months of tops data for most-active station
@app.route("/api/v1.0/tobs")
def tobs():

    # Create a session
    session = Session(engine)

    #Identify most-active station
    sel = [Measurement.date, Measurement.tobs, Measurement.station]
    #station_count = session.query([Measurement.station, func.count(Measurement.date)]).group_by(Measurement.station).all()
    #station_count.sort(key = lambda a: a[1], reverse = True)

    """Return last 12 months of temperature data"""
    results = session.query(*sel).filter(func.strftime(Measurement.station) == "USC00519281").filter(func.strftime(Measurement.date) >= dt.date(2016, 8, 23)).all()

    session.close()

    # Create a dictionary from the row data and append to a list
    high_data = []
    for date, tobs, station in results:
        high_data_dict = {}
        high_data_dict["date"] = date
        high_data_dict["tobs"] = tobs
        high_data.append(high_data_dict)

    return (
        #print(f"Return last 12 months of temperature data<br/>"), 
        jsonify(high_data))

#Retrieve JSON list of min, avg, and max temp for a specified start

#Retrieve JSON list of min, avg, and max temp for a specified start and end




if __name__ == '__main__':
    app.run(debug=True)