import json


class List():
    def run(params=None, guild_data=None):
        with open('rules.json') as f:
            commands = json.load(f)["commands"]

        message = {}
        message['message'] = 'List of commands and their descriptions:\n```'

        for command in commands:
            message['message'] += f'\n{guild_data["general"]["prefix"]}{command["command"]} - ' + \
                (f'{command["description"]}' if 'description' in command else '')
        message['message'] += '\n```'

        return message


class Prefix():
    def run(params=None, guild_data=None):
        if not params:
            return {'error': 'USAGE'}
        if len(params.split()[0]) > 1:
            return {'error': 'USAGE', 'message': 'Your prefix can only be one character, such as ! or ;'}
        prefix = params.split()[0]
        message = {}
        message['message'] = f'Prefix updated to {prefix}'
        guild_data['general']['prefix'] = prefix
        message['guild_data'] = guild_data
        return message


class Usage():
    def run(params=None, guild_data=None):
        if not params:
            return {'error': 'USAGE'}

        usage_command = params.split()[0]

        with open('rules.json') as f:
            rules = json.load(f)
            commands = rules['commands']

        found_command = {}
        for command in commands:
            if usage_command == command['command']:
                found_command = command
        
        if not found_command:
            return {'error': 'USAGE', 'message': f'Command not recognized. Please use {guild_data["general"]["prefix"]}list to see a full list of commands.'}

        message = {}
        usages = found_command['usage'] if type(found_command['usage']) is list else [
            found_command['usage']]
        message['message'] = f'Usage:'
        for usage in usages:
            message['message'] += f'\n`{guild_data["general"]["prefix"]}{found_command["command"]} {usage}`'
        return message