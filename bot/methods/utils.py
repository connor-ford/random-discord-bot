import json
import random


def change_prefix(params=None, guild_data=None):
    if not params:
        return {"error": "USAGE"}
    prefix = params.split()[0]
    message = {}
    message["message"] = f"Prefix updated to {prefix}"
    guild_data["general"]["prefix"] = prefix
    message["guild_data"] = guild_data
    return message


def flip_coin(params=None, guild_data=None):
    try:
        amount = int(params) if params else 1
    except ValueError:
        return {"error": "USAGE"}

    message = {}
    message["message"] = f"Flipped {amount} coin{'s' if amount > 1 else ''}:\n```"
    for _ in range(amount):
        message["message"] += f"{'H' if random.randint(0, 1) == 1 else 'T'} "
    message["message"] += "```"

    return message


def get_usage(params=None, guild_data=None):
    if not params:
        return {"error": "USAGE"}

    usage_command = params.split()[0]

    with open("rules.json") as f:
        rules = json.load(f)
        commands = rules["commands"]

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
    with open("rules.json") as f:
        commands = json.load(f)["commands"]

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


def random_value(params=None, guild_data=None):
    nums = params.split()[0] if params else "1-10"
    if len(nums.split("-")) != 2:
        return {"error": "USAGE"}
    try:
        num_min, num_max = list(map(int, nums.split("-")))
        amount = int(params.split()[1]) if len(params.split()) >= 2 else 1
        amount = min(amount, 1000)
    except ValueError:
        return {"error": "USAGE"}

    message = {}
    message[
        "message"
    ] = f"{amount} number{'s' if amount > 1 else ''}{' (max)' if amount == 1000 else ''} from {num_min} to {num_max}:\n```"
    for _ in range(amount):
        message["message"] += f"{random.randint(num_min, num_max)} "
    message["message"] += "```"

    return message


def roll_die(params=None, guild_data=None):
    dice = params.split()[0] if params else "1d6"
    try:
        amount, faces = list(map(int, dice.split("d")))
    except ValueError:
        return {"error": "USAGE"}

    message = {}
    message["message"] = f"{amount} {faces}-sided di{'c' if amount > 1 else ''}e:\n```"
    for _ in range(amount):
        message["message"] += f"{random.randint(1, faces)} "
    message["message"] += "```"

    return message
