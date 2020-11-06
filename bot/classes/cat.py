import json
import random

import requests
from discord import Embed


class CatAPI():
    def run(params=None):

        if not params:
            return {'error': 'USAGE'}

        subcommand = params.split()[0]

        message = {}

        # Breeds
        if subcommand == 'breeds':
            response = requests.get(url='https://api.thecatapi.com/v1/breeds')
            if response.status_code != 200:
                return {
                    'error': 'API',
                    'message': response.text
                }

            breeds = response.json()

            message['message'] = "List of breeds and their IDs:\n```"

            # Line up breed codes with offset
            # Note: not used due to 2000 character limit in Discord messages.

            # max_length = 0
            # for breed in breeds:
            #     if len(breed["name"]) > max_length: max_length = len(breed["name"])
            # for breed in breeds:
            #     message += f'\n{breed["name"]}   {repeat(" ",max_length-len(breed["name"]))}{breed["id"]}'

            for breed in breeds:
                message['message'] += f'\n{breed["name"]}: {breed["id"]}'

            message['message'] += '```'

        # Info
        elif subcommand == 'info':
            # Get breed id
            if len(params.split()) < 2:
                return {'error': 'USAGE'}
            breed_id = params.split()[1]
            if not (breed_id == 'random' or len(breed_id) == 4):
                return {'error': 'USAGE'}

            # Get list of breeds
            response = requests.get(url='https://api.thecatapi.com/v1/breeds')
            if response.status_code != 200:
                return {
                    'error': 'API',
                    'message': response.text
                }

            breeds = response.json()

            # If random, pick random breed, else use breed ID
            breed = {}
            if breed_id == 'random':
                breed = random.sample(breeds, 1)[0]
            else:
                for breed_potential in breeds:
                    if breed_potential['id'] == breed_id:
                        breed = breed_potential
                        continue
                if breed == {}:
                    return {
                        'error': 'USAGE',
                        'message': 'The code provided did not match any valid code.'
                    }

            # Get info
            name = breed['name']
            description = breed['description']
            fields = {
                'ID': breed['id'].upper(),
                'AKA': breed['alt_names'] if breed['alt_names'] else 'None',
                'Life Span': f'{breed["life_span"]} years',
                'Weight': f'{breed["weight"]["imperial"]} lbs ({breed["weight"]["metric"]} kgs)',
                'Temperament': breed['temperament'],
                'Origin': f'{breed["origin"]} ({breed["country_code"]})'
            }
            wiki = breed['wikipedia_url']

            print(json.dumps(fields))

            # Get picture of breed
            response = requests.get(
                url='https://api.thecatapi.com/v1/images/search',
                params={'breed_ids': breed_id} if breed_id != 'random' else {}
            )
            if response.status_code != 200:
                return {
                    'error': 'API',
                    'message': response.text
                }

            image_url = response.json()[0]['url']
            print(image_url)

            # Wrap up info/picture in embed
            embed = Embed(
                title=name,
                colour=000000,
                description=description
            )
            for field_name, field_value in fields.items():
                embed.add_field(
                    name=field_name,
                    value=field_value
                )
            embed.set_image(url=image_url)
            embed.set_footer(text=wiki)

            message['embed'] = embed

        # Image
        elif subcommand == 'image':

            # Get breed id
            if len(params.split()) < 2:
                return {'error': 'USAGE'}
            breed_id = params.split()[1]
            if not (breed_id == 'random' or len(breed_id) == 4):
                return {'error': 'USAGE'}

            # Get image
            response = requests.get(
                url='https://api.thecatapi.com/v1/images/search',
                params=dict({'mime_types': 'jpg,png'}, **
                            ({'breed_ids': breed_id} if breed_id != 'random' else {}))
            )
            if response.status_code != 200:
                return {
                    'error': 'API',
                    'message': response.text
                }
            message['message'] = response.json()[0]['url']
        # Gif
        elif subcommand == 'gif':
            # Get gif
            response = requests.get(
                url='https://api.thecatapi.com/v1/images/search',
                params={'mime_types': 'gif'}
            )
            if response.status_code != 200:
                return {
                    'error': 'API',
                    'message': response.text
                }
            message['message'] = response.json()[0]['url']
        else:
            return {'error': 'USAGE'}

        return message
