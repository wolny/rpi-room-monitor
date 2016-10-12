import argparse
import json
import webbrowser
import flickrapi

parser = argparse.ArgumentParser(description='Authenticate with flickr')
parser.add_argument("-c", help="JSON config file")
args = parser.parse_args()

with open(args.c) as config_file:
    config = json.load(config_file)

api_key = config['flickr_api_key']
api_secret = config['flickr_api_secret']

flickr = flickrapi.FlickrAPI(api_key, api_secret, format='parsed-json')

print('Step 1: authenticate')

# Only do this if we don't have a valid token already
if not flickr.token_valid(perms='write'):

    # Get a request token
    flickr.get_request_token(oauth_callback='oob')

    # Open a browser at the authentication URL. Do this however
    # you want, as long as the user visits that URL.
    authorize_url = flickr.auth_url(perms='write')
    webbrowser.open_new_tab(authorize_url)

    # Get the verifier code from the user. Do this however you
    # want, as long as the user gives the application the code.
    verifier = str(input('Verifier code: '))

    # Trade the request token for an access token
    flickr.get_access_token(verifier)

print('Step 2: get my photosets')

sets = flickr.photosets.getList()
print(sets)
