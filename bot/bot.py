#!/usr/bin/env python3

import json
import logging
import random
import sys
from logging.handlers import TimedRotatingFileHandler
from os import path

import discord

from cache import cache
from config import LOG_CACHE, LOG_KEYWORDS, LOG_LEVEL_FILE, LOG_LEVEL_STDOUT, TOKEN
from methods.api import cat_api, dog_api, joke_api
from methods.keywords import keywords
from methods.minecraft import find_mc_username, grab_mc_skin
from methods.pil import worm_on_a_string
from methods.randoms import flip_coin, random_value, roll_die
from methods.utils import change_prefix, get_usage, list_commands

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

# Parse commands
commands = cache.get("commands")
if not commands:
    with open("commands.json") as f:
        commands = json.load(f)["commands"]
    cache.add("commands", commands, 1440)


# Discord client
client = discord.Client()


@client.event
async def on_ready():
    logger.info(f"{client.user} has connected.")
    # Changes activity to a random line in statuses.txt
    await client.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=random.choice(open("resources/statuses.txt").read().splitlines()),
        )
    )


@client.event
async def on_message(message):
    # If sender was a bot
    if message.author.bot:
        return

    # If sent in a guild, use guild data. Otherwise, use user data.
    if message.guild:
        id = str(f"g_{message.guild.id}")
        data_path = f"data/guilds/{id}.json"
    else:
        id = str(f"u_{message.author.id}")
        data_path = f"data/users/{id}.json"

    data = cache.get(id)
    if not data:
        if path.exists(data_path):
            data = json.load(open(data_path))
        else:
            data = {"general": {"prefix": "rdb-"}, "keywords": {}}
        cache.add(id, data, 60)

    prefix = data["general"]["prefix"].lower()

    if commands:
        for command in commands:
            # If message is the command
            if message.content.lower().startswith(prefix + command["command"]):
                logger.info(
                    f'{id} - {message.author} ran the command "{message.content}" (Message ID {message.id})'
                )

                # Send specified response, if exists
                if "response" in command:
                    await message.channel.send(command["response"])

                # Call specified method, if exists
                if "method" in command:
                    command_method = getattr(sys.modules[__name__], command["method"])
                    if not command_method:
                        logger.error(
                            f'{id} - Method {command["method"]} not found. Called from command {command["command"]}'
                        )
                        return
                    response = command_method(
                        params=message.content[message.content.find(" ") + 1 :]
                        if message.content.find(" ") != -1
                        else "",  # Everything past the first space if it exists, else empty string
                        data=data,
                    )
                    logger.debug(
                        f'{id} - Method {command["method"]} ran. Called from command {command["command"]}'
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
                            logger.info(
                                f'{id} - Usage error while running command "{message.content}" (Message ID {message.id})'
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
                                f'{id} - API Error while running command "{message.content}" (Message ID {message.id})'
                                + (
                                    f': {response["message"]}'
                                    if "message" in response
                                    else "."
                                )
                            )
                            return

                    # If guild data changed, update file
                    if "data" in response:
                        data.update(response["data"])
                        cache.add(id, data, 60)
                        with open(data_path, "w") as f:
                            json.dump(data, f)

                    # If response is larger than 2000 characters, send as file
                    if "message" in response and len(response["message"]) > 2000:
                        with open("resources/temp/message.txt", "w") as f:
                            f.write(response["message"])
                        with open("resources/temp/message.txt", "rb") as f:
                            await message.channel.send(
                                content="The response message is larger than 2000 characters, sending as a text file instead:",
                                file=discord.File(f, "message.txt"),
                            )
                        logger.info(
                            f'{id} - Character limit exceeded while running command "{message.content}" (Message ID {message.id})'
                        )
                        return

                    # Send response
                    await message.channel.send(
                        content=response["message"] if "message" in response else None,
                        embed=response["embed"] if "embed" in response else None,
                        file=response["file"] if "file" in response else None,
                    )
                    logger.info(
                        f'{id} - Response sent to command "{message.content}" (Message ID {message.id})'
                    )

                return
    if data["keywords"]:
        sorted_keywords = sorted(data["keywords"].keys(), key=len, reverse=True)
        for keyword in sorted_keywords:
            # If keyword is found in the message
            if keyword in message.content.lower():
                if LOG_KEYWORDS:
                    logger.info(
                        f'{id} - {message.author} triggered the keyword "{keyword}" (Message ID {message.id})'
                    )
                response = data["keywords"][keyword]
                # Substitute variables with their values
                response = response.replace("$NAME$", message.author.name)
                response = response.replace("$ID$", f"<@{message.author.id}>")
                # Only used if in guild
                if message.guild:
                    response = response.replace("$NICK$", message.author.nick)
                    response = response.replace("$CHANNEL$", message.channel.name)
                    response = response.replace("$GUILD$", message.guild.name)
                await message.channel.send(response)
                if LOG_KEYWORDS:
                    logger.info(
                        f'{id} - Response sent to keyword "{keyword}" (Message ID {message.id})'
                    )
                return


client.run(TOKEN)
