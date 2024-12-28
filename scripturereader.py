#!/usr/bin/env python3
import time
import json
import subprocess
import schedule

from gpiozero import Button
from PIL import Image, ImageDraw, ImageFont
from image_utils import ImageText
from datetime import datetime

import st7789

BUTTONS = [Button(5), Button(6), Button(16), Button(24)]
LABELS = ["A", "B", "X", "Y"]

# Create ST7789 LCD display class.

disp = st7789.ST7789(
    height=240,
    rotation=90,
    port=0,
    cs=st7789.BG_SPI_CS_FRONT,  # BG_SPI_CS_BACK or BG_SPI_CS_FRONT
    dc=9,
    backlight=13,  # 18 for back BG slot, 19 for front BG slot.
    spi_speed_hz=80 * 1000 * 1000,
    offset_left=0,
    offset_top=0,
)

with open("/home/zak/scripturereader/data.json") as f:
    d = json.load(f)

now = datetime.now()
year = now.year
day_of_year = now.timetuple().tm_yday
index = now.timetuple().tm_yday - 1

if year % 4 != 0 and day_of_year > 58:
    index += 1

current_verse = d[index]


def handle_button(button):
    global index
    global current_verse
    global d

    label = LABELS[BUTTONS.index(button)]
    print("Button press detected: {}".format(label))

    if label == "A":
        subprocess.run(
            ["aplay", "/home/zak/scripturereader/audio/{}.wav".format(index)]
        )

    elif label == "B":
        now = datetime.now()
        year = now.year
        day_of_year = now.timetuple().tm_yday
        index = now.timetuple().tm_yday - 1

        if year % 4 != 0 and day_of_year > 58:
            index += 1

    elif label == "X":
        index = (index - 1) % 366

    elif label == "Y":
        index = (index + 1) % 366

    current_verse = d[index]
    render_verse()


for button in BUTTONS:
    button.when_released = handle_button

# Initialize display.
disp.begin()

font = "/home/zak/scripturereader/newsreader.ttf"
font_size = 24


def render_verse():
    global font
    global font_size
    global current_verse
    img = ImageText((240, 240), background=(0, 0, 0, 0))
    w, h = img.write_multi_line_text_box(
        (5, 5),
        current_verse,
        box_width=230,
        font_filename=font,
        font_size=font_size,
        color=(255, 255, 255),
        place="left",
        line_spacing=1.5,
    )

    while h > 215:
        font_size -= 1
        img = ImageText((240, 240), background=(0, 0, 0, 0))
        w, h = img.write_multi_line_text_box(
            (5, 5),
            current_verse,
            box_width=230,
            font_filename=font,
            font_size=font_size,
            color=(255, 255, 255),
            place="left",
            line_spacing=1.5,
        )

    disp.display(img.image)
    font_size = 24


def roll_date():
    global index
    global current_verse
    global d

    now = datetime.now()
    year = now.year
    day_of_year = now.timetuple().tm_yday
    index = now.timetuple().tm_yday - 1

    if year % 4 != 0 and day_of_year > 58:
        index += 1

    current_verse = d[index]
    render_verse()


render_verse()

schedule.every().day.at("00:00").do(roll_date)

while True:
    schedule.run_pending()

    time.sleep(1)
