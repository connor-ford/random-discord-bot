#!/usr/bin/env python3

import json
import logging
import sys

import discord
from discord import guild

from classes.cat import CatAPI
from classes.dog import DogAPI
from classes.utils import List, Prefix
from config import TOKEN

# Init logging
logging.basicConfig(
    filename='logs/log.txt',
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s'
)

# Parse rules.json
commands = []
keywords = []

with open('rules.json') as f:
    rules = json.load(f)
    commands = rules['commands']
    keywords = rules['keywords']

with open('data/server_data.json') as f:
    server_data = json.load(f)


# Discord client
client = discord.Client()


@client.event
async def on_ready():
    logging.info('%s has connected.' % (client.user))
    # Changes activity to 'Watching television'
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='television'))


@client.event
async def on_message(message):
    # If sender was a bot
    if message.author.bot:
        return

    if str(message.guild.id) not in server_data:
        server_data[str(message.guild.id)] = {'prefix': '!'}

    prefix = server_data[str(message.guild.id)]['prefix']

    if commands:
        for command in commands:
            # If message is the command
            if message.content.lower().startswith(prefix + command['command']):
                logging.info(
                    f'{message.author} ran the command "{message.content}" (Message ID {message.id})')

                # Send specified response, if exists
                if 'response' in command:
                    await message.channel.send(command['response'])

                # Call specified class, if exists
                if 'class' in command:
                    command_class = getattr(
                        sys.modules[__name__], command['class'])
                    if not command_class:
                        logging.error(
                            f'Class {command["class"]} not found. Called from command {command["command"]}')
                        return
                    response = command_class.run(
                        params=message.content.lower()[message.content.find(" ") + 1:] if message.content.find(
                            " ") != -1 else "",  # Everything past the first space if it exists, else empty string
                        guild_data=server_data[str(message.guild.id)]
                    )
                    logging.info(
                        f'Class {command["class"]} ran. Called from command {command["command"]}')

                    # Returned error
                    if 'error' in response:
                        # Usage error
                        if response['error'] == 'USAGE':
                            if 'message' in response:
                                await message.channel.send(response['message'])
                            usages = command['usage'] if type(command['usage']) is list else [
                                command['usage']]
                            response = f'Usage:'
                            for usage in usages:
                                response = response + \
                                    f'\n`{prefix}{command["command"]} {usage}`'
                            await message.channel.send(response)
                            logging.warning(
                                f'Usage error while running command "{message.content}" (Message ID {message.id})' + (f': {response["message"]}' if 'message' in response else '.'))
                            return
                        # API error
                        if response['error'] == 'API':
                            await message.channel.send('An error has occurred with the API while performing this command. Check logs for more info.')
                            logging.error(
                                f'API Error while running command "{message.content}" (Message ID {message.id})' + (f': {response["message"]}' if 'message' in response else '.'))
                            return

                    # If guild data changed, update file
                    if 'guild_data' in response:
                        server_data[str(message.guild.id)].update(response['guild_data'])
                        print(server_data)
                        with open('data/server_data.json', 'w') as f:
                            json.dump(server_data, f)

                    # Send response
                    await message.channel.send(
                        content=response['message'] if 'message' in response else None,
                        embed=response['embed'] if 'embed' in response else None
                    )
                    logging.info(
                        f'Response sent to command "{message.content}" (Message ID {message.id})')

                return
    if keywords:
        for keyword in keywords:
            if keyword['keyword'] in message.content.lower():
                logging.info(
                    f'{message.author} triggered the keyword "{keyword["keyword"]}" (Message ID {message.id})')
                await message.channel.send(keyword['response'])
                logging.info(
                    f'Response sent to keyword "{keyword["keyword"]}" (Message ID {message.id})')
                return


client.run(TOKEN)
