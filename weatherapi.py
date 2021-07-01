from starlette.responses import StreamingResponse
import config
from utils import WeatherAPI, Render
from fastapi import FastAPI
from typing import Optional

import utils

app = FastAPI()

weather = WeatherAPI(config.OWM_TOKEN)


@app.get("/{language}/{city}")
async def with_timestamp(
    language: utils.LANGUAGES, city: str, timestamp: Optional[int] = None, fuck_cache: Optional[str] = None # this value needed to bypass telegram url cache
):
    if timestamp != None:
        info = weather.get_weather(city, language=language.name, timestamp=timestamp)
        if info == None:
            return {
                "status": "error", 
                "message": "location not found"
            }
        else:
            image = Render().make_hourly(info, language.name)
            return StreamingResponse(image, media_type="image/jpeg")
    else:
        info = weather.get_weather(city, language=language.name)
        if info == None:
            return {
                "status": "error",
                "message": "location not found"
            }
        else:
            image = Render().make_hourly(info, language.name)
            return StreamingResponse(image, media_type="image/jpeg")
