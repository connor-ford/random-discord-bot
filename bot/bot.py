#!/usr/bin/env python3

import logging
import discord
import json

from config import TOKEN, PREFIX

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
                await message.channel.send(command['response'])
                return
    if keywords:
        for keyword in keywords:
            if keyword['keyword'] in message.content:
                await message.channel.send(keyword['response'])
                return


client.run(TOKEN)