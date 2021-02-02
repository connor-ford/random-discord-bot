import random


def flip_coin(params=None):
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


def random_value(params=None):
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


def roll_die(params=None):
    dice = params.split()[0].lower() if params else "1d6"
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
