import random

import requests
from cache import cache
from discord import Embed


def _list_cat_breeds():

    breeds = cache.get("cat_breeds")
    if not breeds:
        response = requests.get(url="https://api.thecatapi.com/v1/breeds")
        if response.status_code != 200:
            return {"error": "API", "message": response.text}

        breeds = response.json()
        cache.add("cat_breeds", breeds, 1440)

    message = {}
    message["message"] = "List of breeds and their IDs:\n```"

    for breed in breeds:
        message["message"] += f'\n{breed["id"].upper()}: {breed["name"]}'

    message["message"] += "```"
    return message


def _get_cat_info(params=None):
    # Get breed id
    breed_id = params.split()[1].lower() if params else "random"
    if not (breed_id == "random" or len(breed_id) == 4):
        return {"error": "USAGE"}

    # Get list of breeds
    breeds = cache.get("cat_breeds")
    if not breeds:
        response = requests.get(url="https://api.thecatapi.com/v1/breeds")
        if response.status_code != 200:
            return {"error": "API", "message": response.text}

        breeds = response.json()
        cache.add("cat_breeds", breeds, 1440)

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
                "message": "The code provided did not match any valid breed.",
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

    return {"embed": embed}


def _get_cat_image(params=None):
    # Get breed id
    breed_id = params.split()[1].lower() if len(params.split()) >= 2 else "random"
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
    return {"message": response.json()[0]["url"]}


def _get_cat_gif():
    # Get gif
    response = requests.get(
        url="https://api.thecatapi.com/v1/images/search",
        params={"mime_types": "gif"},
    )
    if response.status_code != 200:
        return {"error": "API", "message": response.text}
    return {"message": response.json()[0]["url"]}


def cat_api(params=None, data=None):
    if not params:
        return {"error": "USAGE"}

    subcommand = params.split()[0].lower()

    message = {}

    # Breeds
    if subcommand == "breeds":
        return _list_cat_breeds()

    # Info
    elif subcommand == "info":
        return _get_cat_info(params)

    # Image
    elif subcommand == "image":
        return _get_cat_image(params)

    # Gif
    elif subcommand == "gif":
        return _get_cat_gif()

    else:
        return {"error": "USAGE"}


def _list_dog_breeds():
    # Get list of breeds
    breeds = cache.get("dog_breeds")
    if not breeds:
        response = requests.get(url="https://dog.ceo/api/breeds/list/all")
        if response.status_code != 200:
            return {"error": "API", "message": response.text}
        breeds = response.json()["message"]
        cache.add("dog_breeds", breeds, 1440)
    # Compile message
    message = {}
    message["message"] = "List of dog breeds and their sub-breeds:\n```"
    for breed, subbreeds in breeds.items():
        if subbreeds:  # If breed has sub-breeds, list them with the breed
            message["message"] += f'\n{breed.capitalize()}: {", ".join(subbreeds)}'
        else:  # Else, only display the breed
            message["message"] += f"\n{breed.capitalize()}"
    message["message"] += "```"
    return message


def _get_dog_image(params=None):
    # Get breed/sub-breed
    breed = params.split()[1].lower() if len(params.split()) >= 2 else "random"
    subbreed = params.split()[2].lower() if len(params.split()) >= 3 else ""

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
    return {"message": response.json()["message"]}


def dog_api(params=None, data=None):
    if not params:
        return {"error": "USAGE"}

    subcommand = params.split()[0].lower()

    message = {}

    # Breeds
    if subcommand == "breeds":
        return _list_dog_breeds()

    # Image
    elif subcommand == "image":
        return _get_dog_image(params)
    else:
        return {"error": "USAGE"}


def joke_api(params=None, data=None):
    subcommand = params.split()[0].lower() if params else "single"

    message = {}

    # Subcommand validation
    if subcommand != "single" and subcommand != "twopart":
        return {"error": "USAGE"}

    genres = params.split()[1].lower() if len(params.split()) > 1 else "any"

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
