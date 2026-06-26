import unittest
from agronomy import calculate_feasibility, DEFAULT_CONFIG

class TestAgronomyEngine(unittest.TestCase):
    def test_fertilizer_runoff(self):
        # Heavy rain should trigger heavy runoff penalty
        weather = {
            "temp_max": 28.0,
            "rain": 16.0,
            "soil_moisture": 0.30,
            "wind_speed": 10.0,
            "humidity": 75.0
        }
        scores = calculate_feasibility(weather, DEFAULT_CONFIG)
        self.assertLessEqual(scores["fertilizer"], 20.0)

    def test_harvesting_heavy_rain(self):
        # Impassable roads due to heavy rain
        weather = {
            "temp_max": 28.0,
            "rain": 20.0,
            "soil_moisture": 0.30,
            "wind_speed": 10.0,
            "humidity": 75.0
        }
        scores = calculate_feasibility(weather, DEFAULT_CONFIG)
        self.assertEqual(scores["harvesting"], 10.0)

    def test_spraying_drift_wind(self):
        # High wind speed should fully penalize spraying
        weather = {
            "temp_max": 28.0,
            "rain": 0.0,
            "soil_moisture": 0.30,
            "wind_speed": 26.0,
            "humidity": 75.0
        }
        scores = calculate_feasibility(weather, DEFAULT_CONFIG)
        self.assertEqual(scores["spraying"], 0.0)

if __name__ == "__main__":
    unittest.main()
