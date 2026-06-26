DEFAULT_CONFIG = {
    # Fertilizing thresholds
    "fert_optimal_rain_min": 2.0,
    "fert_optimal_rain_max": 8.0,
    "fert_runoff_rain": 15.0,
    "fert_runoff_penalty": 80.0,
    "fert_volatilization_rain": 0.0,
    "fert_volatilization_moisture": 0.20,
    "fert_volatilization_penalty": 60.0,
    "fert_saturated_moisture": 0.45,
    "fert_saturated_penalty": 70.0,
    "fert_heat_temp": 35.0,
    "fert_heat_penalty": 30.0,
    
    # Harvesting thresholds
    "harv_mud_rain": 15.0,
    "harv_mud_penalty": 90.0,
    "harv_wet_rain_min": 5.0,
    "harv_wet_rain_max": 15.0,
    "harv_wet_penalty": 50.0,
    "harv_wind_speed": 25.0,
    "harv_wind_penalty": 50.0,
    
    # Spraying thresholds
    "spray_drift_wind_med": 15.0,
    "spray_drift_penalty_med": 60.0,
    "spray_drift_wind_high": 25.0,
    "spray_drift_penalty_high": 100.0,
    "spray_wash_rain": 2.0,
    "spray_wash_penalty": 80.0,
    "spray_humidity_min": 60.0,
    "spray_humidity_max": 85.0,
    "spray_humidity_penalty": 30.0
}

def calculate_feasibility(weather_data, config):
    """
    Calculates feasibility scores (0-100) for fertilizing, harvesting, and spraying.
    weather_data keys: temp_max, rain, soil_moisture, wind_speed, humidity
    """
    scores = {
        "fertilizer": 100.0,
        "harvesting": 100.0,
        "spraying": 100.0
    }
    
    temp = weather_data.get("temp_max", 28.0)
    rain = weather_data.get("rain", 0.0)
    moisture = weather_data.get("soil_moisture", 0.30)
    wind = weather_data.get("wind_speed", 10.0)
    humidity = weather_data.get("humidity", 75.0)

    # 1. FERTILIZER APPLICATION
    if rain > config["fert_runoff_rain"]:
        scores["fertilizer"] -= config["fert_runoff_penalty"]
    elif config["fert_optimal_rain_min"] <= rain <= config["fert_optimal_rain_max"] and 0.25 <= moisture <= 0.40:
        # Optimal bonus
        scores["fertilizer"] += 10.0
        
    if rain == config["fert_volatilization_rain"] and moisture < config["fert_volatilization_moisture"]:
        scores["fertilizer"] -= config["fert_volatilization_penalty"]
    elif moisture > config["fert_saturated_moisture"]:
        scores["fertilizer"] -= config["fert_saturated_penalty"]
        
    if temp > config["fert_heat_temp"]:
        scores["fertilizer"] -= config["fert_heat_penalty"]
        
    # 2. HARVESTING
    if rain > config["harv_mud_rain"]:
        scores["harvesting"] -= config["harv_mud_penalty"]
    elif config["harv_wet_rain_min"] <= rain <= config["harv_wet_rain_max"]:
        scores["harvesting"] -= config["harv_wet_penalty"]
        
    if wind > config["harv_wind_speed"]:
        scores["harvesting"] -= config["harv_wind_penalty"]
        
    # 3. SPRAYING
    if wind > config["spray_drift_wind_high"]:
        scores["spraying"] -= config["spray_drift_penalty_high"]
    elif wind > config["spray_drift_wind_med"]:
        scores["spraying"] -= config["spray_drift_penalty_med"]
        
    if rain > config["spray_wash_rain"]:
        scores["spraying"] -= config["spray_wash_penalty"]
        
    if not (config["spray_humidity_min"] <= humidity <= config["spray_humidity_max"]):
        scores["spraying"] -= config["spray_humidity_penalty"]
        
    # Clamp scores between 0 and 100
    for key in scores:
        scores[key] = max(0.0, min(100.0, scores[key]))
        
    return scores
