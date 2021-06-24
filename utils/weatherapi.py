from datetime import datetime
from typing import Dict, Optional
import requests


class WeatherAPI:
    def __init__(self, weather_token: str) -> Optional[Dict[str, str]]:
        self.weather_token = weather_token
        self.weather_url = "https://pro.openweathermap.org/data/2.5/forecast/hourly?"

    def get_geo(self, address: str):
        request = (
            f"https://nominatim.openstreetmap.org/search.php?q={address}&format=jsonv2"
        )
        response = requests.get(request)
        location = response.json()
        if response.status_code == 200:  # Is anything else possible?
            if location == []:
                return None

            return {
                "lat": str(location[0]["lat"]),
                "lng": str(location[0]["lon"]),
                "place_name": location[0]["display_name"],
            }
        else:
            return None

    def get_weather(self, name: str, language: str):
        if geo := self.get_geo(name):
            lat = geo["lat"]
            lng = geo["lng"]

            response = requests.get(
                f"{self.weather_url}lat={lat}&lon={lng}&appid={self.weather_token}&lang={language}&units=metric"
            )
            if response.status_code == 200:
                json_data = response.json()
                dt = int(json_data["list"][2]["dt"])

                return {
                    "country": json_data["city"]["country"],
                    "city": json_data["city"]["name"],
                    "time": datetime.utcfromtimestamp(dt).strftime("%H:%M"),
                    "summary": json_data["list"][2]["weather"][0]["description"],
                    "apparentTemperature": json_data["list"][2]["main"]["feels_like"],
                    "temperature": json_data["list"][2]["main"]["temp"],
                    "wind": json_data["list"][2]["wind"]["speed"],
                    "humidity": json_data["list"][2]["main"]["humidity"] / 100,
                    "icon": json_data["list"][2]["weather"][0]["icon"],
                    "+2": json_data["list"][4]["main"]["temp"],
                    "+4": json_data["list"][6]["main"]["temp"],
                    "+6": json_data["list"][8]["main"]["temp"],
                    "+8": json_data["list"][10]["main"]["temp"],
                    "+10": json_data["list"][12]["main"]["temp"],
                    "+12": json_data["list"][14]["main"]["temp"],
                }
