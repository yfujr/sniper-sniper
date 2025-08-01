#####################################################################
#                                                                   #
#  Dew3's Roblox Username Generator & Checker                       # 
#  v0.3                                                             #
#  Modified with random username generation (4-5 chars)              #
#  Utilizes robloxapi by iranathan                                  #
#                                                                   #
#####################################################################

import robloxapi, asyncio
import requests
import pathlib
import colorama
import os, sys
import time
import random
import string
from pathlib import Path
from colorama import *

client = robloxapi.Client()
current_path = os.path.dirname(os.path.realpath(__file__))
open(current_path + "/Available.txt", "a")  # Creates 'Available.txt'
numberOfUsernames = 0
savedNames = 0

def generate_username():
    # Decide between 4 or 5 letters
    length = random.choice([4, 5])
    
    if length == 4:
        # 4 characters - can be any characters
        characters = string.ascii_letters + string.digits + "_"
        username = ''.join(random.choice(characters) for _ in range(4))
    else:
        # 5 characters - letters only
        username = ''.join(random.choice(string.ascii_letters) for _ in range(5))
    
    return username

async def check():
    print(Fore.LIGHTBLACK_EX + "[" + Fore.CYAN + "+" + Fore.LIGHTBLACK_EX + "]" + "Dew3's Roblox Username Generator & Checker")
    print(Fore.WHITE + "[" + Fore.CYAN + "*" + Fore.WHITE + "]" + "Generating and checking random usernames...\n")
    
    global savedNames
    with open('Available.txt', 'w') as available:
        while True:
            username = generate_username()
            if len(username) >= 3 and len(username) <= 20:  # Ensure username meets Roblox requirements
                global numberOfUsernames
                numberOfUsernames += 1
                
                user = await client.get_user_by_username(username)
                if user is None:
                    available.write(username + "\n")
                    savedNames += 1
                    print(Fore.WHITE + "[" + Style.BRIGHT + Fore.GREEN + Back.BLACK + "Available" + Fore.WHITE + "]" + Fore.WHITE + username)
                else:
                    print(Fore.WHITE + "[" + Style.BRIGHT + Fore.RED + Back.BLACK + "Taken" + Fore.WHITE + "]" + Fore.WHITE + username)
                
                # Display stats every 50 checks
                if numberOfUsernames % 50 == 0:
                    print(Fore.CYAN + f"\nChecked {numberOfUsernames} usernames | Found {savedNames} available")
                
                # Small delay to prevent rate limiting
                await asyncio.sleep(0.5)

async def main():
    try:
        tic = time.perf_counter()
        await check()
    except KeyboardInterrupt:
        toc = time.perf_counter()
        print(Fore.CYAN + "\n\nChecker finished " + str(numberOfUsernames) + f" usernames in {toc - tic:0.4f} seconds")
        print("Saved " + str(savedNames) + " usernames to Available.txt!")
        print(Fore.RED + "Closing in 5 seconds")
        time.sleep(5)
        sys.exit()

if __name__ == "__main__":
    asyncio.run(main())
