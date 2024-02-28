# sqlalchemy-challenge
This challenge is set up to analyze sample weather data from stations in Hawaii from a sqlite file, and to make data accessible through a Flask API.

## Climate Data
To complete the data analysis, run the climate_starter.ipynb file.  You will be able to see graphs of precipitation and temperatue data across weather stations from 2010 to 2017.

## Flask API
To access the API, run the app.py file in your terminal, and then open local url listed in your terminal when you open the file.

The initial page using the local url will give a list of available routes.  The precipitation link provides data from the last year of the observation data.  The stations link provides a list of weather stations within the data.  The tobs link provies temperature information for the last year of data for the most active station. 

To access maximum, minimum, and average temperature data from a desired start time, use the following route: /api/v1.0/<start>, where the <start> date is no earlier than 2010-01-01, in the format of yyyy-mm-dd.  To access this data for more restricted range, use the following route: /api/v1.0/<start>/<end>, where the <end> date is of the same format as the start date, and ends no later than 2017-08-23.