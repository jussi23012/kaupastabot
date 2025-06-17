# allowedUsers.py
# A list of users who can access the app
import os

userspath = os.path.join("auth","allowedUsers.txt")

with open(userspath) as f:
    allowedUsers = set(int(line.strip()) for line in f if line.strip())
    