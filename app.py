# Dependencies
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt

# Create engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect Database
Base = automap_base()
Base.prepare(engine, reflect = True)

# Save tables references
measurement = Base.classes.measurement
Station = Base.classes.station

#Create session
session = Session(engine)

#Setup Flask
app = Flask(__name__)

# Create function for measures of central tendency of temperatures
def calc_temp(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
    Returns:
        TMIN, TAVG, and TMAX
    """
    return session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start_date).filter(measurement.date <= end_date).all()

# Set Flask Routes

@app.route("/")
def main():
    # List all routes that are available
    return (
        f"These are the Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    # Convert the query results to a dictionary using date as the key and prcp as the value.
    # Return the JSON representation of your dictionary.
    print("Received API request on precipitation.")

    # Queries
    last_date_query = session.query(func.max(measurement.date)).all()
    max_date_string = last_date_query[0][0]
    max_date = dt.datetime.strptime(max_date_string,"%Y-%m-%d")
    begin_date = max_date - dt.timedelta(365)
    precipitation_data = session.query(measurement.date,measurement.prcp).\
        filter(measurement.date >= begin_date).all()
    
    results_dict = {}

    for result in precipitation_data:
        results_dict[result[0]] = result[1]

    session.close()
    return jsonify(results_dict)

@app.route("/api/v1.0/stations")
def stations():
    # Return a JSON list of stations from the dataset.
    print("Received a API request on Station")

    # Query 
    all_stations = session.query(Station).all()

    # Create a list of dictionaries
    stations_list = []

    for station in all_stations:
        station_dict = {}
        station_dict["id"] = station.id
        station_dict["station"] = station.station
        station_dict["name"] = station.name
        station_dict["latitude"] = station.latitude
        station_dict["longitude"] = station.longitude
        station_dict["elevation"] = station.elevation
        stations_list.append(station_dict)

    session.close()
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Query the dates and temperature observations of the most active station for the last year of data.
    # Return a JSON list of temperature observations (TOBS) for the previous year.
    print("Received API request on tobs.")
    
    # Queries for dates
    final_date_query = session.query(func.max(measurement.date)).all()

    max_date_string = final_date_query[0][0]
    max_date = dt.datetime.strptime(max_date_string,"%Y-%m-%d")

    # Set beginning of search query using dt.timedelta to go 1 year back
    begin_date = max_date - dt.timedelta(365)

    # Query
    all_results = session.query(measurement).\
        filter(measurement.date >= begin_date).all()

    # Create a list of dictionaries for each observation
    tobs_list = []

    for result in all_results:
        tobs_dict = {}
        tobs_dict["date"] = result.date
        tobs_dict["station"] = result.station
        tobs_dict["tobs"] = result.tobs
        tobs_list.append(tobs_dict)
    
    session.close()
    return jsonify(tobs_list)

    # Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a given start or start-end range.
        # When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.

@app.route("/api/v1.0/<start>")  
def start(start):
    print("Received API request on start date.")
    
    # Find the first date
    first_date_query = session.query(func.min(measurement.date)).all()
    first_date = first_date_query[0][0]

    temp = calc_temp(start, last_date)
    return_list = []

    date_dict = {"start_date": start,"end_date": last_date}
    return_list.append(date_dict)
    return_list.append({"TMIN": temp[0][0]})
    return_list.append({"TAVG": temp[0][1]})
    return_list.append({"TMAX": temp[0][2]})
    
    session.close()
    return jsonify(return_list)
    
        # When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):

    print("Received API request on start date and end date.")
    temp = calc_temp(start,end)
    return_list = []

    date_dict = {'start_date': start, 'end_date': end}
    return_list.append(date_dict)
    return_list.append({"TMIN": temp[0][0]})
    return_list.append({"TAVG": temp[0][1]})
    return_list.append({"TMAX": temp[0][2]})

    session.close()
    return jsonify(return_list)
    
if __name__ == "__main__":
    app.run(debug = True)