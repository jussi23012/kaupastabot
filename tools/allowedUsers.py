# allowedUsers.py
# A list of users who can access the app

with open("auth\\allowedUsers.txt") as f:
    allowedUsers = set(int(line.strip()) for line in f if line.strip())
    