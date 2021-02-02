from datetime import datetime
from uuid import UUID

import requests
from discord import Embed


def find_mc_username(params=None):
    if not params or len(params.split()) > 1:
        return {"error": "USAGE", "message": "Please supply a valid username or UUID."}

    mc_uuid = None
    mc_username = ""

    # Check if UUID
    try:
        mc_uuid = str(UUID(params.split()[0].lower(), version=4))
    except ValueError:
        mc_username = params.split()[0].lower()

    # If not UUID, get UUID
    if mc_username:
        response = requests.get(
            url=f"https://api.mojang.com/users/profiles/minecraft/{mc_username}"
        )
        if response.status_code == 204:  # No content = no information
            return {"message": "The supplied username could not be found."}
        if response.status_code != 200:
            return {"error": "API", "message": response.text}

        mc_uuid = str(UUID(response.json()["id"], version=4))

    # Get previous names
    response = requests.get(url=f"https://api.mojang.com/user/profiles/{mc_uuid}/names")
    if response.status_code == 204:  # No content = no information
        return {"message": "The supplied UUID could not be found."}
    if response.status_code != 200:
        return {"error": "API", "message": response.text}

    mc_prev_names = response.json()
    # Proper capitalization of name due to prior lower() of params
    mc_username = mc_prev_names[-1]["name"]

    message = {}
    embed = Embed(title=mc_username, colour=000000, description=mc_uuid)

    # Image of player skin's head
    mc_image_url = f"https://crafatar.com/avatars/{mc_uuid}"
    embed.set_image(url=mc_image_url)

    # Format previous name timestamps
    mc_prev_names_str = ""
    for prev_name in mc_prev_names:
        mc_prev_names_str += (
            f'{prev_name["name"]}: '
            + (
                datetime.utcfromtimestamp(prev_name["changedToAt"] / 1000).strftime(
                    "%e %B, %Y %I:%M %p"
                )
                if "changedToAt" in prev_name
                else "NA"
            )
            + "\n"
        )
    embed.add_field(name="Previous Names", value=mc_prev_names_str)

    message["embed"] = embed
    return message


def grab_mc_skin(params=None):
    if not params or len(params.split()) > 1:
        return {"error": "USAGE", "message": "Please supply a valid username or UUID."}

    mc_uuid = None
    mc_username = ""

    # Check if UUID
    try:
        mc_uuid = str(UUID(params.split()[0].lower(), version=4))
    except ValueError:
        mc_username = params.split()[0].lower()

    # If not UUID, get UUID
    if mc_username:
        response = requests.get(
            url=f"https://api.mojang.com/users/profiles/minecraft/{mc_username}"
        )
        # No content = no information
        if response.status_code == 204 or (
            "error" in response.json()
            and "is invalid" in response.json()["errorMessage"]
        ):
            return {"message": "The supplied username could not be found."}
        if response.status_code != 200:
            return {"error": "API", "message": response.text}

        mc_uuid = str(UUID(response.json()["id"], version=4))

    # URL to skin
    message = {"message": f"https://crafatar.com/skins/{mc_uuid}"}
    return message
