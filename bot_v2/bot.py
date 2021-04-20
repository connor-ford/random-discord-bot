import discord, logging, sys

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
logger.info(f"Cache logging {'ENABLED' if LOG_CACHE else 'DISABLED'}.")
logger.info(f"Keyword logging {'ENABLED' if LOG_KEYWORDS else 'DISABLED'}.")

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


### COMMANDS ###

# Ping
@slash.slash(
    name="ping",
    description="Get the latency of the bot in milliseconds.",
    guild_ids=guild_ids,
)
async def _ping(ctx):
    await ctx.send(f"Pong! ({(int) (bot.latency*1000)}ms)")


bot.load_extension("cogs.pil")
bot.load_extension("cogs.api")

bot.run(TOKEN)