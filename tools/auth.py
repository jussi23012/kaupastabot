# auth.py
# Here we get the API key from a local folder

import os

apipath = os.path.join("auth","kaupastabot_api.txt")

with open(apipath) as f:
    API_key = f.read().strip()
