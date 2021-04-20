import logging, requests
from discord import Embed
from discord.ext import commands
from discord.ext.commands import bot
from discord_slash import cog_ext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option
from random import randint

logger = logging.getLogger(__name__)


class APICog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        response = requests.get(url="https://api.thecatapi.com/v1/breeds")
        if response.status_code != 200:
            logging.warning(f"Unable to get cat breeds: {response.text}")
            return
        self.breeds = response.json()
        self.breed_ids = []
        for breed in self.breeds:
            self.breed_ids.append(breed["id"])

    @cog_ext.cog_subcommand(
        name="breeds",
        base="cat",
        description="Get a list of cat breeds and their associated breed IDs.",
    )
    async def _cat_breeds(self, ctx):
        message = "List of breed IDs and their corresponding breeds:\n```"
        for breed in self.breeds:
            message += f'\n{breed["id"].upper()}: {breed["name"]}'
        message += "```"
        await ctx.send(message)

    @cog_ext.cog_subcommand(
        name="gif", base="cat", description="Get a random GIF of a cat."
    )
    async def _cat_gif(self, ctx):
        response = requests.get(
            url="https://api.thecatapi.com/v1/images/search",
            params={"mime_types": "gif"},
        )
        if response.status_code != 200:
            logging.warning(f"Unable to get cat gif: {response.text}")
            await ctx.send(
                "An API error has occurred. Check logs for more information."
            )
        await ctx.send(response.json()[0]["url"])

    @cog_ext.cog_subcommand(
        name="image",
        base="cat",
        description="Get an image of a cat by its breed ID. If no breed ID is given, a random breed ID will be used.",
        base_description="Images, gifs, info, and breeds of cats.",
        options=[
            create_option(
                name="breed_id",
                description="The breed ID of cat. A list of available breed IDs can be found using `/cat breeds`.",
                option_type=3,
                required=False,
            ),
        ],
    )
    async def _cat_image(self, ctx, breed_id: str = None):
        if breed_id and not breed_id in self.breed_ids:
            await ctx.send(
                "Breed ID could not be found. A list of available breed IDs can be found using `/cat breeds`."
            )
            return
        response = requests.get(
            url="https://api.thecatapi.com/v1/images/search",
            params=dict(
                {"mime_types": "jpg,png"},
                **({"breed_ids": breed_id} if breed_id else {}),
            ),
        )
        if response.status_code != 200:
            logging.warning(f"Unable to get cat image: {response.text}")
            await ctx.send(
                "An API error has occurred. Check logs for more information."
            )
        await ctx.send(response.json()[0]["url"])

    @cog_ext.cog_subcommand(
        name="info",
        base="cat",
        description="Get information on a cat by its breed ID. If no breed ID is given, a random breed ID will be used.",
        options=[
            create_option(
                name="breed_id",
                description="The breed ID of cat. A list of available breed IDs can be found using `/cat breeds`.",
                option_type=3,
                required=False,
            ),
        ],
    )
    async def _cat_info(self, ctx, breed_id: str = None):
        if breed_id and not breed_id in self.breed_ids:
            await ctx.send(
                "Breed ID could not be found. A list of available breed IDs can be found using `/cat breeds`."
            )
            return
        breed_id = (
            breed_id
            if breed_id
            else self.breed_ids[randint(0, len(self.breed_ids) - 1)]
        )
        breed = next(b for b in self.breeds if b["id"] == breed_id)

        # Get info
        name = breed["name"]
        description = breed["description"]
        fields = {
            "ID": breed["id"].upper(),
            "AKA": breed["alt_names"]
            if "alt_names" in breed and breed["alt_names"]
            else "None",
            "Life Span": f'{breed["life_span"]} years',
            "Weight": f'{breed["weight"]["imperial"]} lbs ({breed["weight"]["metric"]} kgs)',
            "Temperament": breed["temperament"],
            "Origin": f'{breed["origin"]} ({breed["country_code"]})',
        }
        wiki = breed.get("wikipedia_url", "No Wikipedia URL Found.")

        # Get picture of breed
        response = requests.get(
            url="https://api.thecatapi.com/v1/images/search",
            params={"breed_ids": breed_id} if breed_id != "random" else {},
        )
        if response.status_code != 200:
            logging.warning(f"Unable to get cat image: {response.text}")
            await ctx.send(
                "An API error has occurred. Check logs for more information."
            )
            return
        image_url = response.json()[0]["url"]

        # Wrap up info/picture in embed
        embed = Embed(title=name, colour=000000, description=description)
        for field_name, field_value in fields.items():
            embed.add_field(name=field_name, value=field_value)
        embed.set_image(url=image_url)
        embed.set_footer(text=wiki)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(APICog(bot))