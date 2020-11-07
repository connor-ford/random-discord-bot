import json

class List():
    def run(params=None, guild_data=None):
        with open('rules.json') as f:
            commands = json.load(f)["commands"]

        message = {}
        message['message'] = 'List of commands and their descriptions:\n```'

        for command in commands:
            message['message'] += f'\n{guild_data["prefix"]}{command["command"]} - ' + \
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
        guild_data['prefix'] = prefix
        message['guild_data'] = guild_data
        return message