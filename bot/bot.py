#!/usr/bin/env python3

import json
import logging
import sys

import discord

from config import PREFIX, TOKEN

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
    rules = json.load(f)['rules']
    for rule in rules:
        if rule['trigger'] == 'command':
            commands.append(rule)
        elif rule['trigger'] == 'keyword':
            keywords.append(rule)
            

# Discord client
client = discord.Client()

@client.event
async def on_ready():
    logging.info('%s has connected.' %(client.user))
    await client.change_presence(activity = discord.Activity(type = discord.ActivityType.watching, name = 'television'))

@client.event
async def on_message(message):
    if message.author.bot:
        return
        
    if commands:
        for command in commands:
            if message.content.startswith(PREFIX + command['command']):
                if 'response' in command:
                    await message.channel.send(command['response'])

                if 'class' in command:
                    command_class = getattr(sys.modules[__name__], command['class'])
                    if not command_class:
                        logging.error('Class %s not found. Called from command %s' %(command_class, command['name']))
                        return
                    response = command_class.run(
                        params=message.content[message.content.find(" ") + 1:] if message.content.find(" ") != -1 else "" # Everything past the first space if it exists, else empty string
                    )

                    # Returned error
                    if 'error' in response:
                        if response['error'] == 'usage':
                            await message.channel.send(f'Usage: `{PREFIX}{command["command"]} {command["usage"]}`')
                            return
                        if response['error'] == 'api':
                            await message.channel.send('An error has occurred with the API while performing this command. Check logs for more info.')
                            logging.error(f'API Error while running command {command["name"]}' + (f': {response["message"]}' if 'message' in response and response['message'] else f'.'))
                            return

                    # Send response
                    await message.channel.send(response['message'])

                return
    if keywords:
        for keyword in keywords:
            if keyword['keyword'] in message.content:
                await message.channel.send(keyword['response'])
                return


client.run(TOKEN)
