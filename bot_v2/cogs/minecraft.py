import logging, requests
from datetime import datetime
from discord import Embed
from discord.ext import commands
from discord_slash import cog_ext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_choice, create_option
from uuid import UUID

logger = logging.getLogger(__name__)


class MinecraftCog(commands.Cog):
    def __init__(self, bot):
        pass

    @cog_ext.cog_subcommand(
        name="skin",
        base="minecraft",
        description="Gets the skin of the supplied user.",
        options=[
            create_option(
                name="id_type",
                description="The type of user ID supplied.",
                option_type=SlashCommandOptionType.INTEGER,
                choices=[
                    create_choice(name="Username", value=0),
                    create_choice(name="UUID", value=1),
                ],
                required=True,
            ),
            create_option(
                name="id",
                description="The ID of the user.",
                option_type=SlashCommandOptionType.STRING,
                required=True,
            ),
        ],
    )
    async def _minecraft_skin(self, ctx, id_type: int, id: str):
        if id_type == 1:  # UUID
            try:
                uuid = str(UUID(id, version=4))
            except ValueError:
                await ctx.send("The provided UUID is not valid.")
        else:  # Name
            response = requests.get(
                url=f"https://api.mojang.com/users/profiles/minecraft/{id}"
            )
            if response.status_code == 204:
                await ctx.send("The supplied username could not be found.")
                return
            if response.status_code != 200:
                logging.warning(f"Unable to get minecraft UUID: {response.text}")
                await ctx.send(
                    "An API error has occurred. Check logs for more information."
                )
                return
            uuid = str(UUID(response.json()["id"], version=4))
        await ctx.send(f"https://crafatar.com/skins/{uuid}")

    @cog_ext.cog_subcommand(
        name="info",
        base="minecraft",
        description="Gets information on the supplied user.",
        options=[
            create_option(
                name="id_type",
                description="The type of user ID supplied.",
                option_type=SlashCommandOptionType.INTEGER,
                choices=[
                    create_choice(name="Username", value=0),
                    create_choice(name="UUID", value=1),
                ],
                required=True,
            ),
            create_option(
                name="id",
                description="The ID of the user.",
                option_type=SlashCommandOptionType.STRING,
                required=True,
            ),
        ],
    )
    async def _minecraft_info(self, ctx, id_type: int, id: str):
        if id_type == 1:  # UUID
            try:
                uuid = str(UUID(id, version=4))
            except ValueError:
                await ctx.send("The provided UUID is not valid.")
        else:  # Name
            response = requests.get(
                url=f"https://api.mojang.com/users/profiles/minecraft/{id}"
            )
            if response.status_code == 204:
                await ctx.send("The supplied username could not be found.")
                return
            if response.status_code != 200:
                logging.warning(f"Unable to get minecraft UUID: {response.text}")
                await ctx.send(
                    "An API error has occurred. Check logs for more information."
                )
                return
            uuid = str(UUID(response.json()["id"], version=4))
        response = requests.get(
            url=f"https://api.mojang.com/user/profiles/{uuid}/names"
        )
        if response.status_code == 204:  # No content = no information
            await ctx.send("The supplied user could not be found.")
            return
        if response.status_code != 200:
            logging.warning(f"Unable to get minecraft UUID: {response.text}")
            await ctx.send(
                "An API error has occurred. Check logs for more information."
            )
            return

        prev_names = response.json()
        username = prev_names[-1]["name"]
        embed = Embed(title=username, colour=000000, description=uuid)
        embed.set_image(url=f"https://crafatar.com/avatars/{uuid}")
        embed.add_field(
            name="Previous Names",
            value="\n".join(
                [
                    (
                        f'{prev_name["name"]}: `'
                        + (
                            datetime.utcfromtimestamp(
                                prev_name["changedToAt"] / 1000
                            ).strftime("%d %B, %Y %I:%M %p")
                            if "changedToAt" in prev_name
                            else "`NA`"
                        )
                        + "`"
                    )
                    for prev_name in prev_names
                ]
            ),
        )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(MinecraftCog(bot))