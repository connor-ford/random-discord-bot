import colorsys, discord, numpy as np
from discord.ext import commands
from discord_slash import cog_ext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option
from PIL import Image
from random import randint


class PILCog(commands.Cog):
    def __init__(self, bot):
        self.rgb_to_hsv = np.vectorize(colorsys.rgb_to_hsv)
        self.hsv_to_rgb = np.vectorize(colorsys.hsv_to_rgb)

    def _shift_hue(self, arr, hout):
        r, g, b, a = np.rollaxis(arr, axis=-1)
        h, s, v = self.rgb_to_hsv(r, g, b)
        h = hout
        r, g, b = self.hsv_to_rgb(h, s, v)
        arr = np.dstack((r, g, b, a))
        return arr

    def _colorize(self, image, hue):
        """
        Colorize PIL image `original` with the given
        `hue` (hue within 0-360); returns another PIL image.
        """
        img = image.convert("RGBA")
        arr = np.array(img)
        new_img = Image.fromarray(
            self._shift_hue(arr, hue / 360.0).astype("uint8"), "RGBA"
        )

        return new_img

    @cog_ext.cog_slash(
        name="worm",
        description="Get a color-shifted image of a worm on a string.",
        options=[
            create_option(
                name="hue",
                description="Color value to shift the image by (defaults to a random value).",
                option_type=SlashCommandOptionType.INTEGER,
                required=False,
            )
        ],
    )
    async def _worm(self, ctx, hue: int = randint(0, 359)):
        with Image.open("resources/worm-on-a-string-base.png", "r") as image:
            new_image = self._colorize(image, hue)
            new_image.save("resources/worm-on-a-string.png")
        await ctx.send(
            f"Worm on a string, shifted by a color value of {hue}:",
            file=discord.File("resources/worm-on-a-string.png"),
        )


def setup(bot):
    bot.add_cog(PILCog(bot))