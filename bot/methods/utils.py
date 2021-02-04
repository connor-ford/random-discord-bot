import json

from cache import cache


def change_prefix(params=None, guild_data=None):
    if not params:
        return {"error": "USAGE"}
    prefix = params.split()[0]
    message = {}
    message["message"] = f"Prefix updated to {prefix}"
    guild_data["general"]["prefix"] = prefix
    message["guild_data"] = guild_data
    return message


def get_usage(params=None, guild_data=None):
    if not params:
        return {"error": "USAGE"}

    usage_command = params.split()[0].lower()

    commands = cache.get("commands")
    if not commands:
        with open("commands.json") as f:
            commands = json.load(f)["commands"]
        cache.add("commands", commands, 1440)

    found_command = {}
    for command in commands:
        if usage_command == command["command"]:
            found_command = command

    if not found_command:
        return {
            "error": "USAGE",
            "message": f'Command not recognized. Please use {guild_data["general"]["prefix"]}list to see a full list of commands.',
        }

    message = {}
    usages = (
        found_command["usage"]
        if type(found_command["usage"]) is list
        else [found_command["usage"]]
    )
    message["message"] = f"Usage:"
    for usage in usages:
        message[
            "message"
        ] += f'\n`{guild_data["general"]["prefix"]}{found_command["command"]} {usage}`'
    return message


def list_commands(params=None, guild_data=None):
    commands = cache.get("commands")
    if not commands:
        with open("commands.json") as f:
            commands = json.load(f)["commands"]
        cache.add("commands", commands, 1440)

    message = {}
    message["message"] = "List of commands and their descriptions:\n```"

    for command in commands:
        message[
            "message"
        ] += f'\n{guild_data["general"]["prefix"]}{command["command"]} - ' + (
            f'{command["description"]}' if "description" in command else ""
        )
    message["message"] += "\n```"

    return message
