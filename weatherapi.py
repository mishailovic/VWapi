import time
from asyncio import get_running_loop
from functools import partial
from typing import Optional

from fastapi import FastAPI
from langid import classify as get_lang
from starlette.responses import StreamingResponse

from lru import LRU

from config import OWM_TOKEN, LRU_SIZE, LRU_EXPIRE
from utils import LANGUAGES, Render, WeatherAPI, constants

app = FastAPI()

weather = WeatherAPI(OWM_TOKEN)

renderer = Render()

cache = LRU(LRU_SIZE)

@app.get("/")
async def weather_(
    city: str,
    lang: Optional[LANGUAGES] = None,
    timestamp: Optional[int] = None,
):
    cache_key = city + str(timestamp or "") + str(lang or "")

    if cache.has_key(cache_key):
        cache_entry = cache[cache_key]

        if not cache_entry["expires"] <= int(time.time()):
            cache_entry["image"].seek(0)
            return StreamingResponse(cache_entry["image"], media_type="image/jpeg")

    loop = get_running_loop()
    exec = loop.run_in_executor
    if not lang:
        lang = (await exec(None, get_lang, city))[0]
        if lang not in constants.messages["ms"].keys():
            lang = "en"
    language = LANGUAGES(lang)
    info = await weather.get_weather(
        city, language=language.name, timestamp=timestamp
    )
    if info:
        image = await exec(
            None, partial(renderer.make_hourly, info, language.name)
        )

        cache[cache_key] = {
            "image": image,
            "expires": int(time.time()) + LRU_EXPIRE
        }

        return StreamingResponse(image, media_type="image/jpeg")
    return {"status": "error", "message": "location not found"}
