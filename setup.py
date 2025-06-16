import os
import time

# ===================Colour Magic===================
red = "\033[91m"
green = "\033[92m"
yellow = "\033[93m"
reset = "\033[0m"

print(f"\nWelcome to the {green}Kaupastabot{reset} setup.\n")
time.sleep(1)

# ====================Directory====================
directory = "auth" # default name: auth
bDirectory = False
try:
    os.mkdir(directory)
    print(f"{green}Directory '{directory}' created successfully.{reset}")
    bDirectory = True
except FileExistsError:
    print(f"{yellow}Directory '{directory}' already exists. {reset}")
except PermissionError:
    print(f"{red}Permission denied: Unable to create '{directory}'.{reset}")
except Exception as e:
    print(f"{red}An error occurred: {e}{reset}")

time.sleep(1)

# ====================API key====================
filename = "kaupastabot_api.txt"
path = os.path.join(directory,filename)
bApi = False
try:
    f = open(path, "x").close()
    userinput = input(f"Add API key to the {filename}? (Enter Y to continue, anything else to skip)\n").lower().strip()
    if (userinput == 'y'):
        input_api = input("Enter API key from BotFather: ")
        with open(path, "a") as f:
            f.write(input_api)
        print(f"{green}API key '{input_api}' saved to {path}!{reset}")
        bApi = True
        print("\n")

    else:
        print(f"{yellow}Skipped{reset}")

except FileExistsError:
    print(f"{yellow}File '{filename}' already exists. {reset}")
except PermissionError:
    print(f"{red}Permission denied: Unable to create '{filename}'.{reset}")
except Exception as e:
    print(f"{red}An error occurred: {e}{reset}")

time.sleep(1)

# ====================Allowed Users====================
filename = "allowedUsers.txt"
path = os.path.join(directory,filename)
bAllowed = False
try:
    f = open(path, "x").close()
    userinput = input(f"Add Telegram user ID to the {filename}? (Enter Y to continue, anything else to skip)\n").lower().strip()
    if (userinput == 'y'):
        input_id = input("Enter Telegram user ID (Press Enter to skip): ")
        with open(path, "a") as f:
            f.write(input_id+"\n")
        print(f"{green}User ID '{input_id}' saved to {path}{reset}")
        bAllowed = True
        print("\n")

    else:
        print(f"{yellow}Skipped{reset}")

except FileExistsError:
    print(f"{yellow}File '{filename}' already exists. {reset}")
except PermissionError:
    print(f"{red}Permission denied: Unable to create '{filename}'.{reset}")
except Exception as e:
    print(f"{red}An error occurred: {e}{reset}")

# ====================Report====================
print("\nSetup complete.")
time.sleep(0.25)
color = green if bDirectory else red
print(f"{directory} directory created: {color}{bDirectory}{reset}")
time.sleep(0.25)
color = green if bApi else red
print(f"kaupastabot_api.txt created: {color}{bApi}{reset}")
time.sleep(0.25)
color = green if bAllowed else red
print(f"allowedUsers.txt created: {color}{bAllowed}{reset}")
time.sleep(0.25)
print("Exiting...\n")