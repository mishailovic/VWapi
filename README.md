<h1 align="center">VWapi</h1>

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=mishailovic_VWapi&metric=alert_status)](https://sonarcloud.io/dashboard?id=mishailovic_VWapi)
[![GitHub issues](https://img.shields.io/github/issues/mishailovic/VWapi)](https://github.com/mishailovic/VWapi/issues)
[![GitHub forks](https://img.shields.io/github/forks/mishailovic/VWapi)](https://github.com/mishailovic/VWapi/network)
[![GitHub stars](https://img.shields.io/github/stars/mishailovic/VWapi)](https://github.com/mishailovic/VWapi/stargazers)
[![GitHub license](https://img.shields.io/github/license/mishailovic/VWapi)](https://github.com/mishailovic/VWapi/blob/master/LICENSE)


<p align="center">Visual Weather api. Returns beautiful pictures with the current weather.
</p>

![image](https://vwapi.herokuapp.com?city=Москва)
![image](https://vwapi.herokuapp.com?city=Frankfurt)
![image](https://vwapi.herokuapp.com?city=Kyoto)

# Installation:

```bash
sudo apt update -y && sudo apt upgrade -y
sudo apt install -y git python3 python3-pip 
git clone https://github.com/mishailovic/VWapi
cd VWapi
pip3 install -r requirements.txt
python3 -m uvicorn weatherapi:app
```

# Usage:

```python
import requests
import time
from PIL import Image
import io
language = "en" # can be "en" or "ru"
place = "Moscow" # can be any city, place, street, or site, geocoder automatically selects location. 
timestamp = round(time.time()) # optional timestamp, can be any unix timestamp from now, to now + three days 
r = requests.get(f"https://weather.hotaru.ga?lang={language}&city={place}&timestamp={timestamp}")
image = Image.open(io.BytesIO(r.content))
image.show()
```

# Notes about performance
## StreamingResponse
Usually StreamingResponse is slower than Response, but it depends on the environment where VWapi is gonna be deployed, run some tests before and after using StreamingResponse and see which one has better performance.

If you want to use StreamingResponse set `USE_STREAMING_RESPONSE` environment variable to `true`.

# Credits:
render.py based on https://github.com/adrian-kalinin/TeleWeatherRobot/blob/master/bot/utils/render.py 
Huge thanks to its developer @adrian-kalinin  

Thx to @notmyst33d for https://github.com/notmyst33d/Dripcons
