import logging, requests
from discord import Embed
from discord.ext import commands
from discord.ext.commands import bot
from discord_slash import cog_ext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_choice, create_option
from random import randint

logger = logging.getLogger(__name__)


class APICog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Get cat breeds
        response = requests.get(url="https://api.thecatapi.com/v1/breeds")
        if response.status_code != 200:
            logging.error(f"Unable to get cat breeds: {response.text}")
            exit()
        self.cat_breeds = response.json()
        self.cat_breed_ids = []
        for breed in self.cat_breeds:
            self.cat_breed_ids.append(breed["id"])

        # Get dog breeds
        response = requests.get(url="https://dog.ceo/api/breeds/list/all")
        if response.status_code != 200:
            logging.error(f"Unable to get dog breeds: {response.text}")
            exit()
        self.dog_breeds = response.json()["message"]

    @cog_ext.cog_subcommand(
        name="breeds",
        base="cat",
        description="Get a list of cat breeds and their breed IDs.",
    )
    async def _cat_breeds(self, ctx):
        # List cat breeds
        message = "List of breed IDs and their corresponding breeds:\n```"
        for breed in self.cat_breeds:
            message += f'\n{breed["id"].upper()}: {breed["name"]}'
        message += "```"
        await ctx.send(message)

    @cog_ext.cog_subcommand(
        name="gif", base="cat", description="Get a random GIF of a cat."
    )
    async def _cat_gif(self, ctx):
        # Get cat gif
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
                description="The breed ID of cat. A list of available breed IDs can be found using /cat breeds.",
                option_type=3,
                required=False,
            ),
        ],
    )
    async def _cat_image(self, ctx, breed_id: str = None):
        # Get cat image
        if breed_id and not breed_id in self.cat_breed_ids:
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
                description="The breed ID of cat. A list of available breed IDs can be found using /cat breeds.",
                option_type=3,
                required=False,
            ),
        ],
    )
    async def _cat_info(self, ctx, breed_id: str = None):
        # Get cat info
        if breed_id and not breed_id in self.cat_breed_ids:
            await ctx.send(
                "Breed ID could not be found. A list of available breed IDs can be found using `/cat breeds`."
            )
            return
        breed_id = (
            breed_id
            if breed_id
            else self.cat_breed_ids[randint(0, len(self.cat_breed_ids) - 1)]
        )
        breed = next(b for b in self.cat_breeds if b["id"] == breed_id)

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

    @cog_ext.cog_subcommand(
        name="breeds",
        base="dog",
        description="Get a list of dog breeds and their sub-breeds.",
    )
    async def _dog_breeds(self, ctx):
        # Get dog breeds
        message = "List of dog breeds and their sub-breeds:\n```"
        for breed, subbreeds in self.dog_breeds.items():
            subbreeds = [subbreed.capitalize() for subbreed in subbreeds]
            message += f"\n{breed.capitalize()}" + (
                f': {", ".join(subbreeds)}' if subbreeds else ""
            )
        message += "```"
        await ctx.send(message)

    @cog_ext.cog_subcommand(
        name="image",
        base="dog",
        description="Get an image of a dog by its breed and sub-breed. If no breed is given, a random breed will be used.",
        base_description="Images and breeds of dogs.",
        options=[
            create_option(
                name="breed",
                description="The breed of dog. A list of available breeds can be found using /dog breeds.",
                option_type=3,
                required=False,
            ),
            create_option(
                name="subbreed",
                description="The sub-breed of dog. A list of available sub-breeds can be found using /dog breeds.",
                option_type=3,
                required=False,
            ),
        ],
    )
    async def _dog_image(self, ctx, breed: str = None, subbreed: str = None):
        # Get dog image
        response = requests.get(
            url="https://dog.ceo/api/breed"
            + (
                (
                    f"/{breed.lower()}"
                    + (f"/{subbreed.lower()}" if subbreed else "")
                    + "/images/random"
                )
                if breed
                else "s/image/random"
            )
        )
        if response.status_code != 200:
            if response.json()["message"].startswith("Breed not found"):
                await ctx.send(
                    "Breed could not be found. A list of available breed IDs can be found using `/dog breeds`."
                )
                return
            logging.warning(f"Unable to get dog image: {response.text}")
            await ctx.send(
                "An API error has occurred. Check logs for more information."
            )
        await ctx.send(response.json()["message"])

    @cog_ext.cog_subcommand(
        name="single",
        base="joke",
        description="Get a two-part joke by category.",
        options=[
            create_option(
                name="category",
                description='The category of the joke. Select "any" for jokes from any category.',
                option_type=3,
                choices=[
                    create_choice(name="Any", value="any"),
                    create_choice(name="Christmas", value="christmas"),
                    create_choice(name="Dark", value="dark"),
                    create_choice(name="Miscellaneous", value="miscellaneous"),
                    create_choice(name="Programming", value="programming"),
                    create_choice(name="Pun", value="pun"),
                    create_choice(name="Spooky", value="spooky"),
                ],
                required=True,
            )
        ],
    )
    async def _joke_single(self, ctx, category: str):
        # Get single part joke
        response = requests.get(
            url=f"https://sv443.net/jokeapi/v2/joke/{category}",
            params={"type": "single"},
        )
        if response.status_code != 200:
            logging.warning(f"Unable to get joke: {response.text}")
            await ctx.send(
                "An API error has occurred. Check logs for more information."
            )
            return
        await ctx.send(response.json()["joke"])

    @cog_ext.cog_subcommand(
        name="twopart",
        base="joke",
        description="Get a two-part joke by category.",
        base_description="Single or two-part jokes, specified by category.",
        options=[
            create_option(
                name="category",
                description='The category of the joke. Select "any" for jokes from any category.',
                option_type=3,
                choices=[
                    create_choice(name="Any", value="any"),
                    create_choice(name="Christmas", value="christmas"),
                    create_choice(name="Dark", value="dark"),
                    create_choice(name="Miscellaneous", value="miscellaneous"),
                    create_choice(name="Programming", value="programming"),
                    create_choice(name="Pun", value="pun"),
                    create_choice(name="Spooky", value="spooky"),
                ],
                required=True,
            )
        ],
    )
    async def _joke_twopart(self, ctx, category: str):
        # Get two-part joke
        response = requests.get(
            url=f"https://sv443.net/jokeapi/v2/joke/{category}",
            params={"type": "twopart"},
        )
        if response.status_code != 200:
            logging.warning(f"Unable to get joke: {response.text}")
            await ctx.send(
                "An API error has occurred. Check logs for more information."
            )
            return
        await ctx.send(f'{response.json()["setup"]}\n||{response.json()["delivery"]}||')


def setup(bot):
    bot.add_cog(APICog(bot))