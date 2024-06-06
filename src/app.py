from flask import Flask, jsonify, request
from models import db, Weather, WeatherAnalysis
from ingest_data import ingest_data_main
from flasgger import Swagger
from datetime import datetime



def create_app():
    """
    Create and configure the Flask application.

    Returns:
        Flask: The configured Flask application instance.
    """
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()


    Swagger(app, template_file='swagger.yaml')


    @app.route('/')
    def hello():
        return "hello"

    @app.route('/api/weather', methods=['GET'])
    def weather():
        """
        Retrieve weather data.

        This endpoint retrieves weather data based on optional query parameters.

        Returns:
            dict: A JSON object containing weather data.
        """
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        station_id = request.args.get('station_id',type=str)
        date_str = request.args.get('date', type=str)

        query = Weather.query

        if station_id:
            query = query.filter_by(weather_station_id=station_id)
        if date_str:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            query = query.filter_by(date=date)

        weather_query = query.paginate(page=page, per_page=per_page, error_out=False)
        serialized_result = [result.serialize() for result in weather_query.items]

        return jsonify({
            'weather': serialized_result,
            'page': weather_query.page,
            'per_page': weather_query.per_page,
            'total': weather_query.total,
            'pages': weather_query.pages
        })


    @app.route('/api/weather/stats', methods=['GET'])
    def weather_stats():
        """
        Retrieve weather statistics.

        This endpoint retrieves weather statistics based on optional query parameters.

        Returns:
            dict: A JSON object containing weather statistics.
        """
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        station_id = request.args.get('station_id', type=str)
        year = request.args.get('year', type=int)

        query = WeatherAnalysis.query

        if station_id:
            query = query.filter_by(weather_station_id=station_id)
        if year:
            query = query.filter_by(year=year)

        weather_analysis_query = query.paginate(page=page, per_page=per_page, error_out=False)
        serialized_result = [result.serialize() for result in weather_analysis_query.items]

        return jsonify({
            'weather_analysis': serialized_result,
            'page': weather_analysis_query.page,
            'per_page': weather_analysis_query.per_page,
            'total': weather_analysis_query.total,
            'pages': weather_analysis_query.pages
        })


    return app


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        ingest_data_main()

    app.run(debug=False)

