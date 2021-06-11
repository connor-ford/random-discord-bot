import random
from discord.ext import commands
from discord_slash import cog_ext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option


class RandomsCog(commands.Cog):
    # Flip a specified amount of coins
    @cog_ext.cog_subcommand(
        name="coins",
        base="random",
        description="Flip a specified amount of coins.",
        options=[
            create_option(
                name="amount",
                description="The amount of coins to flip (default is 1, must be greater than 0 and less than 1000).",
                option_type=SlashCommandOptionType.INTEGER,
                required=False,
            )
        ],
    )
    async def _coinflip(self, ctx, amount: int = 1):
        if amount < 1:
            await ctx.send("Amount of coins must be greater than 0.")
            return
        if amount > 1000:
            await ctx.send("Amount of coins must be less than 1000.")
            return
        await ctx.send(
            f"Flipped {amount} coins: `"
            + " ".join(
                [
                    f'{"T" if random.randint(0, 1) == 1 else "F"} '
                    for _ in range(0, amount)
                ]
            )
            + "`"
        )

    # Roll a specified amount of dice with a specified amount of faces
    @cog_ext.cog_subcommand(
        name="dice",
        base="random",
        description="Roll a specified amount of dice with a specified amount of faces.",
        options=[
            create_option(
                name="amount",
                description="The amount of dice to roll (default is 1, must be greater than 0 and less than 1000).",
                option_type=SlashCommandOptionType.INTEGER,
                required=False,
            ),
            create_option(
                name="sides",
                description="The amount of faces each dice should have (default is 6, must be greater than 1 and less than 100).",
                option_type=SlashCommandOptionType.INTEGER,
                required=False,
            ),
        ],
    )
    async def _rolldice(self, ctx, amount: int = 1, sides: int = 6):
        if amount < 1:
            await ctx.send("Amount of dice must be greater than 0.")
            return
        if amount > 1000:
            await ctx.send("Amount of dice must be less than 1000.")
            return
        if sides < 2:
            await ctx.send("Amount of faces must be greater than 1.")
            return
        if sides > 100:
            await ctx.send("Amount of faces must be less than 100.")
            return
        await ctx.send(
            f"Rolled {amount} {sides}-sided dice: `"
            + " ".join([str(random.randint(1, sides)) for _ in range(0, amount)])
            + "`"
        )

    # Get a specified amount of numbers between a specified range
    @cog_ext.cog_subcommand(
        name="range",
        base="random",
        description="Get a specified amount of random numbers in a specified range.",
        options=[
            create_option(
                name="amount",
                description="The amount of numbers to generate (default is 1, must be greater than 0 and less than 1000).",
                option_type=SlashCommandOptionType.INTEGER,
                required=False,
            ),
            create_option(
                name="min",
                description="The lower range bound (default is 1).",
                option_type=SlashCommandOptionType.INTEGER,
                required=False,
            ),
            create_option(
                name="max",
                description="The higher range bound (default is 10).",
                option_type=SlashCommandOptionType.INTEGER,
                required=False,
            ),
        ],
    )
    async def _randomrange(self, ctx, amount: int = 1, min: int = 1, max: int = 10):
        if amount < 1:
            await ctx.send("Amount of numbers must be greater than 0.")
            return
        if amount > 1000:
            await ctx.send("Amount of coins must be less than 1000.")
            return
        await ctx.send(
            f"{amount} number{'s' if amount > 1 else ''} between {min} and {max}: `"
            + " ".join([str(random.randint(min, max)) for _ in range(0, amount)])
            + "`"
        )


def setup(bot):
    bot.add_cog(RandomsCog(bot))
