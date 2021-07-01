from datetime import datetime
from typing import Dict, Optional
import requests
from time import time


class WeatherAPI:
    def __init__(self, weather_token: str) -> None:
        self.weather_token = weather_token
        self.weather_url = "https://pro.openweathermap.org/data/2.5/forecast/hourly?"

    def get_geo(self, address: str) -> Optional[Dict[str, str]]:
        request = (
            f"https://nominatim.openstreetmap.org/search.php?q={address}&format=jsonv2&addressdetails=1"
        )
        response = requests.get(request)
        location = response.json()
        if (
            response.status_code == 200
        ):  # Is anything else possible? answer: everything is posiible...
            if location == []:
                return None
            address = location[0]["address"]
            return {"lat": str(location[0]["lat"]), "lng": str(location[0]["lon"]), "name": str(address[list(address.keys())[0]])}
        else:
            return None
    
    def get_weather(self, name: str, language: str, timestamp: str = None):
        if geo := self.get_geo(name):
            lat = geo["lat"]
            lng = geo["lng"]
            name = geo["name"]

            response = requests.get(
                f"{self.weather_url}lat={lat}&lon={lng}&appid={self.weather_token}&lang={language}&units=metric"
            )
            if response.status_code == 200:
                json_data = response.json()
                timezone = int(json_data["city"]["timezone"])
                utcdiff = 3 * 3600  # yes)

                if timestamp != None:
                    realtime = round(round(round(timestamp / 3600) * 3600 + 3600) / 3600) * 3600  # top 10 bruh moments
                else:
                    realtime = json_data["list"][0]["dt"] # one more bruh

                for weather in range(96):
                    if str(json_data["list"][weather]["dt"]) == str(realtime):
                        return {
                            "country": json_data["city"]["country"],
                            "city": name,
                            "time": datetime.utcfromtimestamp(realtime + timezone).strftime("%H:%M"),
                            "summary": json_data["list"][weather]["weather"][0]["description"],
                            "apparentTemperature": json_data["list"][weather]["main"]["feels_like"],
                            "temperature": json_data["list"][weather]["main"]["temp"],
                            "wind": json_data["list"][weather]["wind"]["speed"],
                            "humidity": json_data["list"][weather]["main"]["humidity"] / 100,
                            "icon": json_data["list"][weather]["weather"][0]["icon"],
                            "+2": json_data["list"][weather + 2]["main"]["temp"],
                            "+4": json_data["list"][weather + 4]["main"]["temp"],
                            "+6": json_data["list"][weather + 6]["main"]["temp"],
                            "+8": json_data["list"][weather + 8]["main"]["temp"],
                            "+10": json_data["list"][weather + 10]["main"]["temp"],
                            "+12": json_data["list"][weather + 12]["main"]["temp"],
                        }