import random

import requests
from discord import Embed


def cat_api(params=None, guild_data=None):
    if not params:
        return {"error": "USAGE"}

    subcommand = params.split()[0]

    message = {}

    # Breeds
    if subcommand == "breeds":
        response = requests.get(url="https://api.thecatapi.com/v1/breeds")
        if response.status_code != 200:
            return {"error": "API", "message": response.text}

        breeds = response.json()

        message["message"] = "List of breeds and their IDs:\n```"

        for breed in breeds:
            message["message"] += f'\n{breed["name"]}: {breed["id"].upper()}'

        message["message"] += "```"

    # Info
    elif subcommand == "info":
        # Get breed id
        if len(params.split()) < 2:
            return {"error": "USAGE"}
        breed_id = params.split()[1]
        if not (breed_id == "random" or len(breed_id) == 4):
            return {"error": "USAGE"}

        # Get list of breeds
        response = requests.get(url="https://api.thecatapi.com/v1/breeds")
        if response.status_code != 200:
            return {"error": "API", "message": response.text}

        breeds = response.json()

        # If random, pick random breed, else use breed ID
        breed = {}
        if breed_id == "random":
            breed = random.sample(breeds, 1)[0]
        else:
            for breed_potential in breeds:
                if breed_potential["id"] == breed_id:
                    breed = breed_potential
                    continue
            if breed == {}:
                return {
                    "error": "USAGE",
                    "message": "The code provided did not match any valid code.",
                }

        # Get info
        name = breed["name"]
        description = breed["description"]
        fields = {
            "ID": breed["id"].upper(),
            "AKA": breed["alt_names"]
            if "alt_names" in breed and breed["alt_names"]
            else "None",
            "Life Span": f'{breed["life_span"]} years',
            "Weight": f'{breed["weight"]["imperial"]} lbs ({breed["weight"]["metric"]} kgs)',
            "Temperament": breed["temperament"],
            "Origin": f'{breed["origin"]} ({breed["country_code"]})',
        }
        wiki = breed.get("wikipedia_url", "No Wikipedia URL Found.")

        # Get picture of breed
        response = requests.get(
            url="https://api.thecatapi.com/v1/images/search",
            params={"breed_ids": breed_id} if breed_id != "random" else {},
        )
        if response.status_code != 200:
            return {"error": "API", "message": response.text}

        image_url = response.json()[0]["url"]

        # Wrap up info/picture in embed
        embed = Embed(title=name, colour=000000, description=description)
        for field_name, field_value in fields.items():
            embed.add_field(name=field_name, value=field_value)
        embed.set_image(url=image_url)
        embed.set_footer(text=wiki)

        message["embed"] = embed

    # Image
    elif subcommand == "image":

        # Get breed id
        if len(params.split()) < 2:
            return {"error": "USAGE"}
        breed_id = params.split()[1]
        if not (breed_id == "random" or len(breed_id) == 4):
            return {"error": "USAGE"}

        # Get image
        response = requests.get(
            url="https://api.thecatapi.com/v1/images/search",
            params=dict(
                {"mime_types": "jpg,png"},
                **({"breed_ids": breed_id} if breed_id != "random" else {}),
            ),
        )
        if response.status_code != 200:
            return {"error": "API", "message": response.text}
        message["message"] = response.json()[0]["url"]
    # Gif
    elif subcommand == "gif":
        # Get gif
        response = requests.get(
            url="https://api.thecatapi.com/v1/images/search",
            params={"mime_types": "gif"},
        )
        if response.status_code != 200:
            return {"error": "API", "message": response.text}
        message["message"] = response.json()[0]["url"]
    else:
        return {"error": "USAGE"}

    return message


def dog_api(params=None, guild_data=None):
    if not params:
        return {"error": "USAGE"}

    subcommand = params.split()[0]

    message = {}

    # Breeds
    if subcommand == "breeds":
        # Get list of breeds
        response = requests.get(url="https://dog.ceo/api/breeds/list/all")
        if response.status_code != 200:
            return {"error": "API", "message": response.text}
        breeds = response.json()["message"]
        # Compile message
        message["message"] = "List of dog breeds and their sub-breeds:\n```"
        for breed, subbreeds in breeds.items():
            if subbreeds:  # If breed has sub-breeds, list them with the breed
                message["message"] += f'\n{breed.capitalize()}: {", ".join(subbreeds)}'
            else:  # Else, only display the breed
                message["message"] += f"\n{breed.capitalize()}"
        message["message"] += "```"

    # Image
    elif subcommand == "image":

        # Get breed/sub-breed
        if len(params.split()) < 2:
            return {"error": "USAGE"}
        breed = params.split()[1]
        subbreed = params.split()[2] if len(params.split()) > 2 else ""

        # Get image
        if breed == "random":  # Random breed
            response = requests.get(url="https://dog.ceo/api/breeds/image/random")
        else:  # Specified breed
            response = requests.get(
                url=f"https://dog.ceo/api/breed/{breed}"
                + (f"/{subbreed}" if subbreed else "")
                + "/images/random"
            )
        if response.status_code != 200:
            if response.json()["message"].startswith("Breed not found"):
                return {"error": "USAGE", "message": response.json()["message"]}
            return {"error": "API", "message": response.text}
        message["message"] = response.json()["message"]
    else:
        return {"error": "USAGE"}

    return message


def joke_api(params=None, guild_data=None):
    if not params:
        return {"error": "USAGE"}

    subcommand = params.split()[0]

    message = {}

    # Subcommand validation
    if subcommand != "single" and subcommand != "twopart":
        return {"error": "USAGE"}

    # Get genres, defaulting to "any" if not specified
    if len(params.split()) > 1:
        genres = params.split()[1]
    else:
        genres = "any"

    # Send request
    response = requests.get(
        url=f"https://sv443.net/jokeapi/v2/joke/{genres}", params={"type": subcommand}
    )
    if response.status_code == 106:
        return {"error": "USAGE", "message": response.json()["additionalInfo"]}
    if response.status_code != 200:
        return {"error": "API", "message": response.text}

    # Compile Message
    if subcommand == "twopart":
        message[
            "message"
        ] = f'{response.json()["setup"]}\n||{response.json()["delivery"]}||'
    else:
        message["message"] = f'{response.json()["joke"]}'

    return message
