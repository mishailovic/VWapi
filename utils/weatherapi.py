from datetime import datetime
import requests


class WeatherAPI:
    def __init__(self, weather_token, geo_token):
        self.weather_token = weather_token
        self.geo_token = geo_token
        self.weather_url = "https://pro.openweathermap.org/data/2.5/forecast/hourly?"
        self.geo_url = "https://geocoder.ls.hereapi.com/6.2/geocode.json"

    def get_geo(self, address):
        try:
            request = self.geo_url + f"?apiKey={self.geo_token}&searchtext={address}"
            response = requests.get(request)

            if response.status_code == 200:
                if raw_data := response.json()["Response"]["View"]:
                    location = raw_data[0]["Result"][0]["Location"]

                    return {
                        "lat": location["DisplayPosition"]["Latitude"],
                        "lng": location["DisplayPosition"]["Longitude"],
                    }
        except KeyError:
            pass

    def get_weather(self, name, language):
        if geo := self.get_geo(name):
            lat = str(geo["lat"])
            lng = str(geo["lng"])

            response = requests.get(
                f"{self.weather_url}lat={lat}&lon={lng}&appid={self.weather_token}&lang={language}&units=metric"
            )
            if response.status_code == 200:
                json_data = response.json()
                dt = int(json_data["list"][0]["dt"])

                return {
                    "country": json_data["city"]["country"],
                    "city": json_data["city"]["name"],
                    "time": datetime.utcfromtimestamp(dt).strftime("%H:%M"),
                    "summary": json_data["list"][0]["weather"][0]["description"],
                    "apparentTemperature": json_data["list"][0]["main"]["feels_like"],
                    "temperature": json_data["list"][0]["main"]["temp"],
                    "wind": json_data["list"][0]["wind"]["speed"],
                    "humidity": json_data["list"][0]["main"]["humidity"] / 100,
                    "icon": json_data["list"][0]["weather"][0]["icon"],
                    "+2": json_data["list"][2]["main"]["temp"],
                    "+4": json_data["list"][4]["main"]["temp"],
                    "+6": json_data["list"][6]["main"]["temp"],
                    "+8": json_data["list"][8]["main"]["temp"],
                    "+10": json_data["list"][10]["main"]["temp"],
                    "+12": json_data["list"][12]["main"]["temp"],
                }
