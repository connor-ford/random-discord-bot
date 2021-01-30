def _list_keywords(guild_data=None):
    message = {}
    message[
        "message"
    ] = f"Listing {len(guild_data['keywords'])} keywords and their responses:\n```"
    for keyword, response in guild_data["keywords"].items():
        message["message"] += f"{keyword}: {repr(response)}\n"
    message["message"] += "```"
    return message


def _add_keyword(params=None, guild_data=None):
    if not params or len(params) < 2:
        return {"error": "USAGE"}
    keyword, response = params.split(" ", 1)
    keyword = keyword.lower()

    message = {}
    message[
        "message"
    ] = f'{"Updated" if keyword in guild_data["keywords"] else "Added"} "{keyword}" keyword with response "{response}".'

    guild_data["keywords"][keyword] = response
    message["guild_data"] = guild_data
    return message


def _remove_keyword(params=None, guild_data=None):
    if not params:
        return {"error": "USAGE"}
    keyword = params.lower()
    message = {}
    if keyword in guild_data["keywords"]:
        guild_data["keywords"].pop(keyword)
        message["guild_data"] = guild_data
        message["message"] = f'Keyword "{keyword}" removed.'
    else:
        message["message"] = f'Keyword "{keyword}" not found.'
    return message


def keywords(params=None, guild_data=None):
    if not params:
        return {"error": "USAGE"}
    subcommand = params.split()[0].lower()

    if subcommand == "list":
        return _list_keywords(guild_data)
    elif subcommand == "add":
        return _add_keyword(params.split(" ", 1)[1], guild_data)
    elif subcommand == "remove":
        return _remove_keyword(params.split(" ", 1)[1], guild_data)
    else:
        return {"error": "USAGE"}
