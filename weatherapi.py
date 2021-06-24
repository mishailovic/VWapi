from os import error
from typing import Optional
import io
from starlette.responses import StreamingResponse
import time
import sys
import config
from utils import WeatherAPI, Render
from loguru import logger
from fastapi import FastAPI

app = FastAPI()

from fastapi.responses import FileResponse


@app.get("/{language}/{city}")
def read_root(language: str, city: str):
    weather = WeatherAPI(config.owm_token)
    info = weather.get_weather(city, language=language)
    if info == None:
        return {"status": "error", "message": "location not found"}
    else:    
        image = Render().make_hourly(info, language)
        return StreamingResponse(image, media_type="image/jpeg")
