import json
from config import PREFIX


class List():
    def run(params=None):
        with open('rules.json') as f:
            commands = json.load(f)["commands"]

        message = {}
        message['message'] = 'List of commands and their descriptions:\n```'

        for command in commands:
            message['message'] += f'\n{PREFIX}{command["command"]}: ' + \
                (f'{command["description"]}' if 'description' in command else '')
        message['message'] += '\n```'

        return message
