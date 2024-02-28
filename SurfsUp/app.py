# Import the dependencies.
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import pandas as pd

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
    results = session.query(Measurement.date, Measurement.prcp).filter((Measurement.date) >= dt.date(2016, 8, 23)).all()

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
    station_count = session.query(Measurement.station, func.count(Measurement.date)).group_by(Measurement.station).all()
    station_count.sort(key = lambda a: a[1], reverse = True)
    high_station = station_count[0][0]

    """Return last 12 months of temperature data"""
    results = session.query(*sel).filter(Measurement.station == high_station).filter((Measurement.date) >= dt.date(2016, 8, 23)).all()

    session.close()

    # Create a dictionary from the row data and append to a list
    high_data = []
    for date, tobs, station in results:
        high_data_dict = {}
        high_data_dict["date"] = date
        high_data_dict["tobs"] = tobs
        high_data.append(high_data_dict)

    return (jsonify(high_data))

#Retrieve JSON list of min, avg, and max temp for a specified start
@app.route("/api/v1.0/<start>")
def data_start(start):
    """Return a JSON list of the minimum temperature, the average temperature,\
         and the maximum temperature for a specified start or start-end range.s"""

    #Convert start date to date-time object
    canonicalized = start.split('-')
    canonicalized = list(map(int, canonicalized))
    try:
        first_date = dt.date(canonicalized[0], canonicalized[1], canonicalized[2])

        # Create a session
        session = Session(engine)
    
        # Query based on start date
        sel = [Measurement.date, Measurement.tobs]
        results = session.query(*sel).filter((Measurement.date) >= first_date).all()

        session.close()

        #Create dataframe for min, avg, and max temps
        temp_df = pd.DataFrame(results, columns = ["Date", "Temperature"])
        temp_min = temp_df.groupby("Date").min()
        temp_avg = temp_df.groupby("Date").mean()
        temp_max = temp_df.groupby("Date").max()
        temp_frame = pd.DataFrame(temp_df["Date"].unique(), columns = ["Date"])
        temp_frame = pd.merge(temp_frame, temp_min, how = "inner", on = "Date").rename(columns = {"Temperature": "TMIN"})
        temp_frame = pd.merge(temp_frame, temp_avg, how = "inner", on = "Date").rename(columns = {"Temperature": "TAVG"})
        temp_frame = pd.merge(temp_frame, temp_max, how = "inner", on = "Date").rename(columns = {"Temperature": "TMAX"})
    
        #Create list that can jsonify
        show_data = []
        for index, row in temp_frame.iterrows():
            data_dict = {}
            data_dict["date"] = row["Date"]
            data_dict["TMIN"] = row["TMIN"]
            data_dict["TAVG"] = row["TAVG"]
            data_dict["TMAX"] = row["TMAX"]
            show_data.append(data_dict)

        return jsonify(show_data)
    except IndexError:
        return jsonify({"error": f"Starting date of {start} not found.  Please type in a start date in the format of yyyy-mm-dd."}), 404

#Retrieve JSON list of min, avg, and max temp for a specified start and end
@app.route("/api/v1.0/<start>/<end>")
def data_bounded(start, end):
    """Return a JSON list of the minimum temperature, the average temperature,\
         and the maximum temperature for a specified start or start-end range.s"""

    #Convert start date to date-time object
    canonicalized = start.split('-')
    canonicalized = list(map(int, canonicalized))
    end_canon = end.split('-')
    end_canon = list(map(int, end_canon))

    try:
        first_date = dt.date(canonicalized[0], canonicalized[1], canonicalized[2])
        end_date = dt.date(end_canon[0], end_canon[1], end_canon[2])

        # Create a session
        session = Session(engine)
    
        # Query based on start date
        sel = [Measurement.date, Measurement.tobs]
        results = session.query(*sel).filter((Measurement.date) >= first_date).filter((Measurement.date) <= end_date).all()

        session.close()

        #Create dataframe for min, avg, and max temps
        temp_df = pd.DataFrame(results, columns = ["Date", "Temperature"])
        temp_min = temp_df.groupby("Date").min()
        temp_avg = temp_df.groupby("Date").mean()
        temp_max = temp_df.groupby("Date").max()
        temp_frame = pd.DataFrame(temp_df["Date"].unique(), columns = ["Date"])
        temp_frame = pd.merge(temp_frame, temp_min, how = "inner", on = "Date").rename(columns = {"Temperature": "TMIN"})
        temp_frame = pd.merge(temp_frame, temp_avg, how = "inner", on = "Date").rename(columns = {"Temperature": "TAVG"})
        temp_frame = pd.merge(temp_frame, temp_max, how = "inner", on = "Date").rename(columns = {"Temperature": "TMAX"})
    
        #Create list that can jsonify
        show_data = []
        for index, row in temp_frame.iterrows():
            data_dict = {}
            data_dict["date"] = row["Date"]
            data_dict["TMIN"] = row["TMIN"]
            data_dict["TAVG"] = row["TAVG"]
            data_dict["TMAX"] = row["TMAX"]
            show_data.append(data_dict)

        return jsonify(show_data)
    except IndexError:
        return jsonify({"error": f"Starting date of {start} or ending date of {end} not found.  Please type in a start and end date in the format of yyyy-mm-dd."}), 404



if __name__ == '__main__':
    app.run(debug=True)