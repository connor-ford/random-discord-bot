from logging import error
import requests


class DogAPI():
    def run(params=None, guild_data=None):

        if not params:
            return {'error': 'USAGE'}

        subcommand = params.split()[0]

        message = {}

        # Breeds
        if subcommand == 'breeds':
            # Get list of breeds
            response = requests.get(url='https://dog.ceo/api/breeds/list/all')
            if response.status_code != 200:
                return {
                    'error': 'API',
                    'message': response.text
                }
            breeds = response.json()['message']
            # Compile message
            message['message'] = 'List of dog breeds and their sub-breeds:\n```'
            for breed, subbreeds in breeds.items():
                if subbreeds:  # If breed has sub-breeds, list them with the breed
                    message['message'] += f'\n{breed.capitalize()}: {", ".join(subbreeds)}'
                else:  # Else, only display the breed
                    message['message'] += f'\n{breed.capitalize()}'
            message['message'] += '```'

        # Image
        elif subcommand == 'image':

            # Get breed/sub-breed
            if len(params.split()) < 2:
                return {'error': 'USAGE'}
            breed = params.split()[1]
            subbreed = params.split()[2] if len(params.split()) > 2 else ''

            # Get image
            if breed == 'random':  # Random breed
                response = requests.get(
                    url='https://dog.ceo/api/breeds/image/random'
                )
            else:  # Specified breed
                response = requests.get(
                    url=f'https://dog.ceo/api/breed/{breed}' + (
                        f'/{subbreed}' if subbreed else '') + '/images/random'
                )
            if response.status_code != 200:
                if response.json()['message'].startswith('Breed not found'):
                    return {
                        'error': 'USAGE',
                        'message': response.json()['message']
                    }
                return {
                    'error': 'API',
                    'message': response.text
                }
            message['message'] = response.json()['message']
        else:
            return {'error': 'USAGE'}

        return message
