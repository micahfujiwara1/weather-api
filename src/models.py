from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from pytz import timezone


db = SQLAlchemy()


class Weather(db.Model):
    """
    Represents weather data stored in the database.

    Attributes:
        weather_id (int): The unique identifier for the weather data.
        weather_station_id (str): The ID of the weather station.
        date (datetime.date): The date of the weather data.
        max_temp (int): The maximum temperature recorded.
        min_temp (int): The minimum temperature recorded.
        precipitation (int): The amount of precipitation recorded.
        created (datetime.datetime): The timestamp when the data was created.
    """
    __tablename__ = 'weather'
    weather_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    weather_station_id = db.Column(db.String(80))
    date = db.Column(db.Date, nullable=False)
    max_temp = db.Column(db.Integer, nullable=True)
    min_temp = db.Column(db.Integer, nullable=True)
    precipitation = db.Column(db.Integer, nullable=True)
    created = db.Column(db.DateTime, default=datetime.now(timezone('UTC')))

    def __init__(self, weather_station_id, date, max_temp, min_temp, precipitation, created=None):
        self.weather_station_id = weather_station_id
        self.date = date
        self.max_temp = max_temp
        self.min_temp = min_temp
        self.precipitation = precipitation
        if created is None:
            created = datetime.now(timezone('UTC'))
        self.created = created

    def __repr__(self):
        return f"Weather(weather_id={self.weather_id}, weather_station_id={self.weather_station_id}, date={self.date}, max_temp={self.max_temp}, min_temp={self.min_temp}, precipitation={self.precipitation}, created={self.created})"

    def serialize(self):
        return {
            'weather_id':self.weather_id,
            'weather_station_id':self.weather_station_id,
            'date':self.date,
            'max_temp':self.max_temp,
            'min_temp':self.min_temp,
            'precipitation':self.precipitation,
            'created':self.created.isoformat()
        }


class YieldData(db.Model):
    """
    Represents yield data stored in the database.

    Attributes:
        yield_id (int): The unique identifier for the yield data.
        year (int): The year for which the yield data is recorded.
        yield_amount (int): The yield amount recorded.
        created (datetime.datetime): The timestamp when the data was created.
    """
    __tablename__ = 'yield_data'
    yield_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    year = db.Column(db.Integer, nullable=False)
    yield_amount = db.Column(db.Integer, nullable=True)
    created = db.Column(db.DateTime, default=datetime.now(timezone('UTC')))

    def __init__(self, year, yield_amount, created=None):
        self.year = year
        self.yield_amount = yield_amount
        if created is None:
            created = datetime.now(timezone('UTC'))
        self.created = created

    def __repr__(self):
        return f"YieldData(yield_id={self.yield_id}, year={self.year}, yield_amount={self.yield_amount}, created={self.created})"
    
    def serialize(self):
        return {
            'id':self.yield_id,
            'year':self.year,
            'yield_amount':self.yield_amount,
            'created':self.created.isoformat()
        }
    


class WeatherAnalysis(db.Model):
    """
    Represents weather analysis data stored in the database.

    Attributes:
        weather_analysis_id (int): The unique identifier for the weather analysis data.
        weather_station_id (str): The ID of the weather station.
        year (int): The year for which the analysis is conducted.
        avg_max_temp_celsius (int): The average maximum temperature in Celsius.
        avg_min_temp_celsius (int): The average minimum temperature in Celsius.
        accumulated_precipitation_cm (int): The accumulated precipitation in centimeters.
        created (datetime.datetime): The timestamp when the data was created.
    """
    __tablename__ = 'weather_analysis'
    weather_analysis_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    weather_station_id = db.Column(db.String(80), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    avg_max_temp_celsius = db.Column(db.Integer, nullable = True)
    avg_min_temp_celsius = db.Column(db.Integer, nullable = True)
    accumulated_precipitation_cm = db.Column(db.Integer, nullable = True)
    created = db.Column(db.DateTime, default=datetime.now(timezone('UTC')), nullable=False)

    def __init__(self, weather_station_id, year, avg_max_temp_celsius=None, avg_min_temp_celsius=None, accumulated_precipitation_cm=None, created=None):
        self.weather_station_id = weather_station_id
        self.year = year
        self.avg_max_temp_celsius = avg_max_temp_celsius
        self.avg_min_temp_celsius = avg_min_temp_celsius
        self.accumulated_precipitation_cm = accumulated_precipitation_cm
        if created is None:
            created = datetime.now(timezone('UTC'))
        self.created = created

    def __repr__(self):
        return f"WeatherAnalysis(weather_id={self.weather_analysis_id}, weather_station_id={self.weather_station_id}, year={self.year}, avg_max_temp={self.avg_max_temp_celsius}, avg_min_temp={self.avg_min_temp_celsius}, accumulated_precipitation={self.accumulated_precipitation_cm}, created={self.created})"

    def serialize(self):
        return {
            'weather_analysis_id':self.weather_analysis_id,
            'weather_station_id':self.weather_station_id,
            'year':self.year,
            'avg_max_temp':self.avg_max_temp_celsius,
            'avg_min_temp':self.avg_min_temp_celsius,
            'accumulated_precipitation':self.accumulated_precipitation_cm,
            'created':self.created.isoformat()
        }
    



