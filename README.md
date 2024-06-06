# Code Challenge Template
# Weather Data API

This project is a Flask-based web application that provides an API for accessing weather data and statistics. The application ingests weather and yield data from text files, processes the data, and stores it in a SQLite database. The API allows users to query weather data and weather statistics based on various filters.


# Table of Contents

Weather Data API
Table of Contents
Project Structure
Setup
Prerequisites
Installation
Usage
Running the Application
API Endpoints
Testing


# Project Structure

├── app.py
├── ingest_data.py
├── models.py
├── swagger.yaml
├── test_file.py
├── requirements.txt
├── wx_data/
│   └── ...
└── yld_data/
    └── US_corn_grain_yield.txt

app.py: Main application file containing the Flask application and API endpoints.
ingest_data.py: Script for ingesting weather and yield data, performing data analysis, and storing results in the database.
models.py: SQLAlchemy models for the database.
swagger.yaml: Swagger specification file for API documentation.
test_file.py: Unit tests for the API endpoints.
requirements.txt: List of required Python packages.
wx_data/: Directory containing weather data files.
yld_data/: Directory containing yield data file.


# Setup

Prerequisites
Python 3.12+
pip (Python package installer)


# Installation

1. Clone the repository:
git clone https://github.com/micahfujiwara1/weather-data.git
cd Code-Challenge-Template/src


2. Install the required packages:
pip install -r requirements.txt


# Running the Application

1.Ensure the SQLite database file (database.db) does not exist. If it exists, delete it to start fresh.
2.Run the application:
python app.py

The application will ingest data, perform analysis, and start the Flask server at http://localhost:5000.


# API Endpoints

URL: /api/weather
Method: GET
Query Parameters:
page (integer): Page number for pagination (default: 1)
per_page (integer): Number of items per page (default: 10)
station_id (string): Weather station ID for filtering
date (string): Date for filtering (YYYY-MM-DD)
Response: JSON object containing weather data
Retrieve Weather Statistics

URL: /api/weather/stats
Method: GET
Query Parameters:
page (integer): Page number for pagination (default: 1)
per_page (integer): Number of items per page (default: 10)
station_id (string): Weather station ID for filtering
year (integer): Year for filtering
Response: JSON object containing weather statistics
The detailed API documentation can be found at http://localhost:5000/apidocs (Swagger UI).


# Testing

To run the unit tests:
python -m unittest test_file.py