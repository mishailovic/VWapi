from starlette.responses import StreamingResponse
import config
from utils import WeatherAPI, Render
from fastapi import FastAPI

import utils

app = FastAPI()


@app.get(
    "/{language}/{city}",
    responses={
        200: {
            "content": {
                "application/json": {  # Should we make 4xx?
                    "example": {"status": "error", "message": "location not found"},
                },
                "image/png": {},
            },
        },
    },
)
def read_root(language: utils.LANGUAGES, city: str):
    weather = WeatherAPI(config.OWM_TOKEN)
    info = weather.get_weather(city, language=language.name)
    if info == None:
        return {"status": "error", "message": "location not found"}
    else:
        image = Render().make_hourly(info, language.name)
        return StreamingResponse(image, media_type="image/jpeg")
