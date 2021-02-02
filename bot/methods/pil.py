import colorsys
import random

import numpy as np
from discord import File
from PIL import Image

rgb_to_hsv = np.vectorize(colorsys.rgb_to_hsv)
hsv_to_rgb = np.vectorize(colorsys.hsv_to_rgb)


def _shift_hue(arr, hout):
    r, g, b, a = np.rollaxis(arr, axis=-1)
    h, s, v = rgb_to_hsv(r, g, b)
    h = hout
    r, g, b = hsv_to_rgb(h, s, v)
    arr = np.dstack((r, g, b, a))
    return arr


def _colorize(image, hue):
    """
    Colorize PIL image `original` with the given
    `hue` (hue within 0-360); returns another PIL image.
    """
    img = image.convert("RGBA")
    arr = np.array(img)
    new_img = Image.fromarray(_shift_hue(arr, hue / 360.0).astype("uint8"), "RGBA")

    return new_img


def worm_on_a_string(params=None):
    hue = params.split()[0].lower() if params else "random"
    if not (hue.isdigit() or hue == "random"):
        return {
            "error": "USAGE",
            "message": 'Please provide a valid hue value between 0 and 360, or the "random" keyword to specify a random hue value.',
        }

    if hue == "random":
        hue = random.randrange(0, 360)
    else:
        hue = int(hue)

    if not (0 <= int(hue) <= 360):
        return {
            "error": "USAGE",
            "message": "Please provide a valid hue value between 0 and 360.",
        }

    with Image.open("resources/worm-on-a-string-base.png", "r") as image:
        new_image = _colorize(image, hue)
        new_image.save("resources/temp/worm-on-a-string.png")

    message = {
        "message": f"Worm on a string, shifted by a hue value of {str(hue)}.",
        "file": File(fp="resources/temp/worm-on-a-string.png"),
    }
    return message
