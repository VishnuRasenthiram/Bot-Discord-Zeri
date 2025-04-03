import os
from dotenv import load_dotenv
import requests
import json
import random
load_dotenv()
apikey = os.getenv('TENOR_API')  # click to set to your apikey
lmt = 10
ckey = os.getenv('cKey')  # set the client_key for the integration and use the same value for all API calls

# our test search

def getRandomGIf(search_term):
# get the top 8 GIFs for the search term
    r = requests.get(
        "https://tenor.googleapis.com/v2/search?q=%s&key=%s&client_key=%s&limit=%s" % (search_term, apikey, ckey,  lmt))

    if r.status_code == 200:
        # load the GIFs using the urls for the smaller GIF sizes
        gif = json.loads(r.content)
        
        return gif['results'][random.randint(0,9)]['media_formats']['gif']['url']
    else:
        gif = None
        return gif