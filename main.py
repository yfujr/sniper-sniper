import requests
import random
import string
import time

# Configuration
NAMES = 10  # How many valid usernames to find
FILE = 'valid.txt'
BIRTHDAY = '1999-04-20'

# Terminal Colors
class bcolors:
    OK = '\033[94m'
    FAIL = '\033[91m'
    END = '\033[0m'

# Functions
def success(username, count):
    print(f"{bcolors.OK}[{count}/{NAMES}] [+] {username} is available{bcolors.END}")
    with open(FILE, 'a') as f:
        f.write(username + '\n')

def taken(username):
    print(f"{bcolors.FAIL}[-] {username} is taken{bcolors.END}")

def make_username():
    length = random.choice([4, 5])
    if length == 4:
        chars = string.ascii_lowercase + string.digits
    else:
        chars = string.ascii_lowercase
    return ''.join(random.choices(chars, k=length))

def check_username(username):
    url = f"https://auth.roblox.com/v1/usernames/validate?request.username={username}&request.birthday={BIRTHDAY}"
    r = requests.get(url, timeout=5)
    r.raise_for_status()
    return r.json().get('code') == 0

# Main Loop
found = 0
while found < NAMES:
    try:
        user = make_username()
        if check_username(user):
            found += 1
            success(user, found)
        else:
            taken(user)
    except requests.exceptions.RequestException as e:
        print(f"[!] Network error: {e}")
        time.sleep(1)
    except KeyboardInterrupt:
        print("Interrupted by user.")
        break
    except Exception as e:
        print(f"[!] Error: {e}")
        time.sleep(1)
