from datetime import datetime
from typing import Dict, Optional

from utils.http import fetch


class WeatherAPI:
    def __init__(self, weather_token: str) -> None:
        self.weather_token = weather_token
        self.weather_url = (
            "https://pro.openweathermap.org/data/2.5/forecast/hourly?"
        )

    async def get_geo(self, address: str, language: str) -> Optional[Dict[str, str]]:
        url = (
            "https://api.openweathermap.org/geo/1.0/direct?"
            + f"q={address}&appid={self.weather_token}"
        )
        location = await fetch(url)
        if not location:
            return
        return {
            "lat": str(location[0]["lat"]),
            "lng": str(location[0]["lon"]),
            "name": str(location[0]["local_names"].get(language, "en") if location[0].get("local_names") else location[0]["name"]),
        }

    async def get_weather(
        self, name: str, language: str, timestamp: str = None
    ):
        geo = await self.get_geo(name, language)
        if not geo:
            return
        lat = geo["lat"]
        lng = geo["lng"]
        name = geo["name"]
        json_data = await fetch(
            f"{self.weather_url}lat={lat}&lon={lng}&appid="
            + f"{self.weather_token}&lang={language}&units=metric"
        )
        if not json_data:
            return
        timezone = int(json_data["city"]["timezone"])
        if timestamp:
            realtime = (
                round(round(round(timestamp / 3600) * 3600 + 3600) / 3600)
                * 3600
            )  # top 10 bruh moments
        else:
            realtime = json_data["list"][0]["dt"]  # one more bruh

        for weather in range(96):
            if str(json_data["list"][weather]["dt"]) == str(realtime):
                return {
                    "country": json_data["city"]["country"],
                    "city": name,
                    "time": datetime.utcfromtimestamp(
                        realtime + timezone
                    ).strftime("%H:%M"),
                    "summary": json_data["list"][weather]["weather"][0][
                        "description"
                    ],
                    "apparentTemperature": json_data["list"][weather]["main"][
                        "feels_like"
                    ],
                    "temperature": json_data["list"][weather]["main"]["temp"],
                    "wind": json_data["list"][weather]["wind"]["speed"],
                    "humidity": json_data["list"][weather]["main"]["humidity"]
                    / 100,
                    "icon": json_data["list"][weather]["weather"][0]["icon"],
                    "+2": json_data["list"][weather + 2]["main"]["temp"],
                    "+4": json_data["list"][weather + 4]["main"]["temp"],
                    "+6": json_data["list"][weather + 6]["main"]["temp"],
                    "+8": json_data["list"][weather + 8]["main"]["temp"],
                    "+10": json_data["list"][weather + 10]["main"]["temp"],
                    "+12": json_data["list"][weather + 12]["main"]["temp"],
                }
