from asyncio import get_running_loop
from functools import partial
from typing import Optional

from fastapi import FastAPI
from langid import classify as get_lang
from starlette.responses import StreamingResponse

from config import OWM_TOKEN
from utils import LANGUAGES, Render, WeatherAPI, constants

app = FastAPI()

weather = WeatherAPI(OWM_TOKEN)

renderer = Render()


@app.get("/")
async def weather_(
    city: str,
    lang: Optional[LANGUAGES] = None,
    timestamp: Optional[int] = None,
):
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
        return StreamingResponse(image, media_type="image/jpeg")
    return {"status": "error", "message": "location not found"}
