#!/usr/bin/env python3

import json
import logging
import sys
from logging.handlers import TimedRotatingFileHandler
from os import path

import discord

from config import TOKEN
from methods.api import cat_api, dog_api, joke_api
from methods.minecraft import find_mc_username, grab_mc_skin
from methods.pil import worm_on_a_string
from methods.utils import (
    change_prefix,
    flip_coin,
    get_usage,
    list_commands,
    random_value,
    roll_die,
)

# Init logging
formatter = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s")
handler = TimedRotatingFileHandler(
    "logs/random_discord_bot.log", when="midnight", interval=1
)
handler.setFormatter(formatter)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# Parse rules.json
commands = []
keywords = []

with open("rules.json") as f:
    rules = json.load(f)
    commands = rules["commands"]
    keywords = rules["keywords"]


# Discord client
client = discord.Client()


@client.event
async def on_ready():
    logger.info("%s has connected." % (client.user))
    # Changes activity to 'Watching television'
    await client.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name="television")
    )


@client.event
async def on_message(message):
    # If sender was a bot
    if message.author.bot:
        return

    guild_id = str(message.guild.id)

    if path.exists(f"data/guilds/{guild_id}.json"):
        with open(f"data/guilds/{guild_id}.json") as f:
            guild_data = json.load(f)
    else:
        guild_data = {"general": {"prefix": "rdb-"}}

    prefix = guild_data["general"]["prefix"]

    if commands:
        for command in commands:
            # If message is the command
            if message.content.lower().startswith(prefix + command["command"]):
                logger.info(
                    f'{message.author} ran the command "{message.content}" (Message ID {message.id})'
                )

                # Send specified response, if exists
                if "response" in command:
                    await message.channel.send(command["response"])

                # Call specified method, if exists
                if "method" in command:
                    command_method = getattr(sys.modules[__name__], command["method"])
                    if not command_method:
                        logger.error(
                            f'Method {command["method"]} not found. Called from command {command["command"]}'
                        )
                        return
                    response = command_method(
                        params=message.content.lower()[message.content.find(" ") + 1 :]
                        if message.content.find(" ") != -1
                        else "",  # Everything past the first space if it exists, else empty string
                        guild_data=guild_data,
                    )
                    logger.info(
                        f'Method {command["method"]} ran. Called from command {command["command"]}'
                    )

                    # Returned error
                    if "error" in response:
                        # Usage error
                        if response["error"] == "USAGE":
                            if "message" in response:
                                await message.channel.send(response["message"])
                            usages = (
                                command["usage"]
                                if type(command["usage"]) is list
                                else [command["usage"]]
                            )
                            response = f"Usage:"
                            for usage in usages:
                                response += f'\n`{prefix}{command["command"]} {usage}`'
                            await message.channel.send(response)
                            logger.warning(
                                f'Usage error while running command "{message.content}" (Message ID {message.id})'
                                + (
                                    f': {response["message"]}'
                                    if "message" in response
                                    else "."
                                )
                            )
                            return
                        # API error
                        if response["error"] == "API":
                            await message.channel.send(
                                "An error has occurred with the API while performing this command. Check logs for more info."
                            )
                            logger.error(
                                f'API Error while running command "{message.content}" (Message ID {message.id})'
                                + (
                                    f': {response["message"]}'
                                    if "message" in response
                                    else "."
                                )
                            )
                            return

                    # If guild data changed, update file
                    if "guild_data" in response:
                        guild_data.update(response["guild_data"])
                        with open(f"data/guilds/{guild_id}.json", "w") as f:
                            json.dump(guild_data, f)

                    # If response is larger than 2000 characters, error out
                    if len(response["message"]) > 2000:
                        await message.channel.send(
                            "The response message is larger than 2000 characters."
                        )
                        logger.error(
                            f'Character limit exceeded while running command "{message.content}" (Message ID {message.id}'
                        )
                        return

                    # Send response
                    await message.channel.send(
                        content=response["message"] if "message" in response else None,
                        embed=response["embed"] if "embed" in response else None,
                        file=response["file"] if "file" in response else None,
                    )
                    logger.info(
                        f'Response sent to command "{message.content}" (Message ID {message.id})'
                    )

                return
    if keywords:
        for keyword in keywords:
            if keyword["keyword"] in message.content.lower():
                logger.info(
                    f'{message.author} triggered the keyword "{keyword["keyword"]}" (Message ID {message.id})'
                )
                await message.channel.send(keyword["response"])
                logger.info(
                    f'Response sent to keyword "{keyword["keyword"]}" (Message ID {message.id})'
                )
                return


client.run(TOKEN)
