import os
import textwrap
from io import BytesIO

import langdetect
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from scipy import interpolate

from .constants import messages


class Render:
    def __init__(self):
        self.path = os.getcwd()

    def make_graph(self, data):
        x = [0, 0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7]
        y = [data[0]] + data + [data[len(data) - 1]]

        f = interpolate.PchipInterpolator(x, y)
        x_new = np.arange(0, len(y) - 2, 0.01)
        y_new = f(x_new)

        fig = plt.figure(frameon=False)
        fig.set_size_inches(12, 4)
        ax = plt.subplot(111)
        ax.fill_between(x_new, y_new, min(y) - 1)
        ax.set_axis_off()

        fig.canvas.draw()

        w, h = fig.canvas.get_width_height()
        buf = np.fromstring(fig.canvas.tostring_argb(), dtype=np.uint8)
        buf.shape = (w, h, 4)
        buf = np.roll(buf, 3, axis=2) # Convert ARGB to RGBA

        plot = Image.frombytes("RGBA", (w, h), buf)
        plot = self.png_crop(plot)

        mask = Image.open(f"{self.path}/resources/card/mask.png")
        back = Image.new("RGBA", mask.size, (255, 255, 255, 0))
        plot = plot.resize(mask.size, resample=Image.ANTIALIAS)
        back.paste(mask, plot)
        return back

    def png_crop(self, image):
        """Crops all transparent borders in png image"""
        bbox = image.getbbox()

        return image.crop(bbox)

    def make_hourly(self, data, lang):
        city = data["city"]
        temp = str(round(data["temperature"])) + "°"
        temp_chart = [
            data["temperature"],
            data["+2"],
            data["+4"],
            data["+6"],
            data["+8"],
            data["+10"],
            data["+12"],
        ]
        weather = data["summary"].lower()
        wind = str(round(data["wind"])) + messages["ms"][lang]
        humidity = str(int(data["humidity"] * 100)) + "%"
        feels_like = (
            messages["feels_like"][lang]
            + str(round(data["apparentTemperature"]))
            + "°"
        )
        bw_divs = [79, 186, 293, 400, 507, 614, 721]

        im = Image.new("RGBA", (800, 656), (255, 255, 255, 0))
        bg = ImageEnhance.Brightness(
            Image.open(f"{self.path}/resources/backgrounds/" + data["icon"] + ".png")
        ).enhance(0.6) # Reduce brightness to 0.6 to make text more visible and add blur
        card = Image.open(f"{self.path}/resources/card/card.png")
        ic = Image.open(
            f"{self.path}/resources/icons/" + data["icon"] + ".png"
        ).convert("RGBA")
        wind_ic = Image.open(f"{self.path}/resources/icons/wind_ic.png")
        hum_ic = Image.open(f"{self.path}/resources/icons/hum_ic.png")
        graph = self.make_graph(temp_chart)

        font_h = f"{self.path}/resources/fonts/Montserrat-Black.ttf"
        font_l = f"{self.path}/resources/fonts/Montserrat-Medium.ttf"

        city_font_jp = (
            f"{self.path}/resources/fonts/NotoSansJP-Medium.otf"  # Japanese
        )
        city_font_ko = (
            f"{self.path}/resources/fonts/NotoSansKR-Medium.otf"  # Korean
        )
        city_font_zh = f"{self.path}/resources/fonts/NotoSansSC-Medium.otf"  # Chinese (Simplified)
        city_font_ar = (
            f"{self.path}/resources/fonts/Vazir-Medium.ttf"  # Arabic or languages using letters from its alphabet
        )
        city_font_he = (
            f"{self.path}/resources/fonts/Rubik-Medium.ttf"  # Hebrew
        )

        city_font_misc = f"{self.path}/resources/fonts/NotoSans-Bold.ttf"  # Other languages (Latin, Greek, etc)

        temp_font = ImageFont.truetype(font=font_h, size=112)
        temp_chart_font_now = ImageFont.truetype(font=font_h, size=25)
        temp_chart_font = ImageFont.truetype(font=font_l, size=25)
        feels_like_font = ImageFont.truetype(font=font_l, size=30)
        weather_font = ImageFont.truetype(font=font_h, size=38)
        weather_font_big = ImageFont.truetype(font=font_h, size=58)
        wind_font = ImageFont.truetype(font=font_l, size=32)
        time_font = ImageFont.truetype(font=font_l, size=24)
        time_font_now = ImageFont.truetype(font=font_h, size=24)
        city_font_pos = 32

        # City name language detection
        city_lang = langdetect.detect(city)

        # Choose compatible font for the detected language
        if city_lang == "jp":
            city_font = ImageFont.truetype(font=city_font_jp, size=32)
        elif city_lang == "ko":
            city_font = ImageFont.truetype(font=city_font_ko, size=32)
        elif city_lang in ("zh-cn", "zh-tw",):
            city_font = ImageFont.truetype(font=city_font_zh, size=32)
        elif city_lang in ("ar", "fa", "ur", "pa",):
            city_font = ImageFont.truetype(font=city_font_ar, size=32)
            city_font_pos = 20
        elif city_lang == "el":
            city_font = ImageFont.truetype(font=city_font_misc, size=32)
        elif city_lang == "he":
            city_font = ImageFont.truetype(font=city_font_he, size=32)
        else:
            city_font = ImageFont.truetype(
                font=font_l, size=32
            )  # Fallback to default font if no compatible font was found

        
        blur_mask = Image.open(f"{self.path}/resources/card/blur_mask.png")
        blur_bg = bg.filter(ImageFilter.GaussianBlur(radius=4))
        bg.paste(blur_bg, blur_mask)

        im.paste(bg)
        im.paste(ic, (48, 8), ic)
        draw = ImageDraw.Draw(im)
        text_size = ImageDraw.Draw(im).textsize

        draw.text(
            (im.width - text_size(city, city_font)[0] - 77, city_font_pos),
            city,
            font=city_font,
        )
        draw.text(
            (im.width - text_size(temp, temp_font)[0] - 77, 72),
            text=temp,
            font=temp_font,
        )
        draw.text(
            (im.width - text_size(feels_like, feels_like_font)[0] - 77, 186),
            text=feels_like,
            font=feels_like_font,
            fill=(255, 255, 255, 221),
        )
        draw.text(
            ((im.width - text_size(wind, wind_font)[0] - 77), 276),
            text=wind,
            font=wind_font,
            fill=(255, 255, 255, 221),
        )
        draw.text(
            ((im.width - text_size(humidity, wind_font)[0] - 77), 236),
            text=humidity,
            font=wind_font,
            fill=(255, 255, 255, 221),
        )
        im.paste(
            wind_ic,
            (
                im.width
                - text_size(wind, wind_font)[0]
                - 77
                - 10
                - wind_ic.width,
                282,
            ),
            wind_ic,
        )
        im.paste(
            hum_ic,
            (
                im.width
                - text_size(humidity, wind_font)[0]
                - 77
                - 10
                - hum_ic.width,
                240,
            ),
            hum_ic,
        )

        card_compose = Image.new("RGBA", (800, 380), (255, 255, 255, 0))
        card_compose_final = Image.new("RGBA", (800, 380), (255, 255, 255, 0))

        card_compose.paste(graph, (24, card_compose.height - graph.height - 20), graph)
        card_compose_draw = ImageDraw.Draw(card_compose)

        for x in bw_divs:
            for y in range(0, card_compose.height - 1):
                yl, yc, yr = 0, 0, 0

                if card_compose.getpixel((x, y)) == (255, 255, 255, 0):
                    continue
                else:
                    yc = y

                    for yy in range(0, card_compose.height - 1):
                        if card_compose.getpixel((x - 15, yy)) != (255, 255, 255, 0):
                            yl = yy
                            break
                        else:
                            continue

                    for yy in range(0, card_compose.height - 1):
                        if card_compose.getpixel((x + 15, yy)) != (255, 255, 255, 0):
                            yr = yy
                            break
                        else:
                            continue

                    if bw_divs.index(x) == 0:
                        card_compose_draw.text(
                            (
                                (
                                    x
                                    + 10
                                    - text_size(
                                        str(temp_chart[bw_divs.index(x)]),
                                        temp_chart_font_now,
                                    )[0]
                                    / 2
                                ),
                                min(yl, yc, yr) - 38,
                            ),
                            text=str(round(temp_chart[bw_divs.index(x)]))
                            + "°",
                            font=temp_chart_font_now,
                            fill=(255, 255, 255, 255),
                        )
                    else:
                        card_compose_draw.text(
                            (
                                (
                                    x
                                    + 10
                                    - text_size(
                                        str(temp_chart[bw_divs.index(x)]),
                                        temp_chart_font,
                                    )[0]
                                    / 2
                                ),
                                min(yl, yc, yr) - 38,
                            ),
                            text=str(round(temp_chart[bw_divs.index(x)]))
                            + "°",
                            font=temp_chart_font,
                            fill=(255, 255, 255, 255),
                        )
                    break

        card_compose_final.paste(card, card)
        card_compose_final.paste(card_compose, card_compose)

        im.paste(card_compose_final, (0, im.height - card_compose_final.height), card_compose_final)

        time = data["time"].split(":")
        time_list = list()
        time_list.append(data["time"])
        hours = time[0]
        minutes = time[1]

        if int(hours) + 3 > 23:
            if int(hours) == 22:
                if int(minutes) > 30:
                    hours = "01"
                    time[1] = "00"
                    time_list.append("01:00")
                else:
                    hours = "00"
                    time[1] = "00"
                    time_list.append("00:00")

            elif int(hours) == 23:
                if int(minutes) > 30:
                    hours = "02"
                    time[1] = "00"
                    time_list.append("02:00")
                else:
                    hours = "01"
                    time[1] = "00"
                    time_list.append("01:00")

            else:
                if int(minutes) > 30:
                    hours = "00"
                    time[1] = "00"
                    time_list.append("00:00")
                else:
                    hours = "23"
                    time[1] = "00"
                    time_list.append("23:00")

        else:
            if int(minutes) > 30:
                hours = str(int(hours) + 3)
                time[0] = hours
                time[1] = "00"
                time_list.append(":".join(time))
            else:
                hours = str(int(hours) + 2)
                time[0] = hours
                time[1] = "00"
                time_list.append(":".join(time))

        for i in range(0, 5):
            if int(hours) + 2 > 23:
                if int(hours) % 2 == 0:
                    hours = "00"
                else:
                    hours = "01"
            else:
                hours = str(int(hours) + 2)
            time_plus = [hours, "00"]
            time_list.append(":".join(time_plus))

        for i in range(0, 7):
            if i:
                draw.text(
                    (bw_divs[i] - text_size(time_list[i])[0], 370),
                    text=time_list[i],
                    font=time_font,
                    fill=(255, 255, 255, 255),
                )
            else:
                draw.text(
                    (bw_divs[i] - text_size(time_list[i])[0], 370),
                    text=time_list[i],
                    font=time_font_now,
                    fill=(255, 255, 255, 255),
                )

        lines = textwrap.wrap(weather, width=17)
        if len(weather) < 13:
            draw.text((64, 253), text=lines[0], font=weather_font_big)
        else:
            if len(lines) > 2:
                liness = textwrap.wrap(weather, width=23)
                draw.text(
                    (64, 230),
                    text=liness[0],
                    font=ImageFont.truetype(font=font_h, size=32),
                )
                try:
                    draw.text(
                        (64, text_size(liness[0], weather_font)[1] + 230 + 3),
                        text=liness[1],
                        font=ImageFont.truetype(font=font_h, size=32),
                    )
                except Exception:
                    pass
                try:
                    draw.text(
                        (
                            64,
                            text_size(liness[0], weather_font)[1] * 2
                            + 230
                            + 3,
                        ),
                        text=liness[2],
                        font=ImageFont.truetype(font=font_h, size=32),
                    )
                except Exception:
                    pass
            elif len(lines) > 1:
                draw.text((64, 245), text=lines[0], font=weather_font)
                draw.text(
                    (64, text_size(lines[0], weather_font)[1] + 245 + 5),
                    text=lines[1],
                    font=weather_font,
                )
            else:
                draw.text((64, 253), text=lines[0], font=weather_font)

        bio = BytesIO()
        bio.name = "image.jpg"
        im.convert("RGB").save(bio, "JPEG")
        bio.seek(0)

        return bio
