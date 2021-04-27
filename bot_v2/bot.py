import discord, logging, sys, os

from config import *
from discord.ext import commands
from discord_slash import SlashCommand
from logging.handlers import TimedRotatingFileHandler

### LOGGING ###

# Init logging
formatter = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# File
if LOG_LEVEL_FILE:
    fileHandler = TimedRotatingFileHandler(
        "logs/random_discord_bot.log", when="midnight", interval=1
    )
    fileHandler.setFormatter(formatter)
    fileHandler.setLevel(LOG_LEVEL_FILE)
    logger.addHandler(fileHandler)

# Stdout
if LOG_LEVEL_STDOUT:
    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setFormatter(formatter)
    consoleHandler.setLevel(LOG_LEVEL_STDOUT)
    logger.addHandler(consoleHandler)

logger.info(f"FILE Log Level set to {LOG_LEVEL_FILE}.")
logger.info(f"STDOUT Log Level set to {LOG_LEVEL_STDOUT}.")

### SETUP ###

bot = commands.Bot(
    command_prefix="#",
    description='An "everything but the kitchen sink" Discord bot, for all of your random needs.',
)
slash = SlashCommand(bot, sync_commands=True)
guild_ids = []


@bot.event
async def on_ready():
    logger.info(f"{bot.user} has connected.")
    # Get list of guild IDs from bot
    global guild_ids
    for guild in bot.guilds:
        guild_ids.append(guild.id)
    # Set presence to display number of connected guilds
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{len(guild_ids)} servers.",
        )
    )


@bot.event
async def on_slash_command(ctx):
    # Log the command called
    logger.info(
        'Slash command "'
        + ctx.name
        + (f" {ctx.subcommand_name}" if ctx.subcommand_name else "")
        + f'" called '
        + (
            f'in guild "{ctx.guild.name}" (ID: {ctx.guild_id}) in channel "{bot.get_channel(ctx.channel_id)}" (ID: {ctx.channel_id}) by'
            if ctx.guild_id
            else f"in DM of"
        )
        + f' user "{ctx.author}" (ID: {ctx.author_id}) (Interaction ID: {ctx.interaction_id})'
    )


cognames = ["api", "minecraft", "pil", "randoms", "utils", "keywords"]
for cogname in cognames:
    bot.load_extension(f"cogs.{cogname}")

bot.run(TOKEN)