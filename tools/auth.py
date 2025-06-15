# auth.py
# Here we get the API key from a local folder

with open("auth\\kaupastabot_api.txt") as f:
    API_key = f.read().strip()
