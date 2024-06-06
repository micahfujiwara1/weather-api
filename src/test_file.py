import unittest
from app import create_app

class TestWeatherAPI(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_weather_endpoint(self):
        response = self.client.get('/api/weather')
        self.assertEqual(response.status_code, 200)
        
    def test_weather_stats_endpoint(self):
        response = self.client.get('/api/weather/stats')
        self.assertEqual(response.status_code, 200)
    
    def test_weather_endpoint_with_filter_station(self):
        station_id = 'USC00110072'
        response = self.client.get(f'/api/weather?station_id={station_id}')
        self.assertEqual(response.status_code, 200)

    def test_weather_endpoint_with_filter_date(self):
        date = '2005-04-19'
        response = self.client.get(f'/api/weather?date={date}')
        self.assertEqual(response.status_code, 200)

    def test_weather_endpoint_with_filter_station_date(self):
        station_id = 'USC00114823'
        date = '2001-04-11'
        response = self.client.get(f'/api/weather?station_id={station_id}&date={date}')
        self.assertEqual(response.status_code, 200)

    def test_weather_stats_endpoint_with_filter_station(self):
        station_id = 'USC0014198'
        response = self.client.get(f'/api/weather/stats?station_id={station_id}')
        self.assertEqual(response.status_code, 200)

    def test_weather_stats_endpoint_with_filter_date(self):
        year = 1997
        response = self.client.get(f'/api/weather/stats?year={year}')
        self.assertEqual(response.status_code, 200)

    def test_weather_stats_endpoint_with_filter_station_date(self):
        station_id = 'USC00111436'
        year = 1990
        response = self.client.get(f'/api/weather/stats?station_id={station_id}&year={year}')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
