#####################################################################
#                                                                   #
#  Roblox Username Sniper                                    #
#  v1.0                                                             #
#  Utilizes robloxapi by iranathan                                  #
#                                                                   #
#####################################################################

import robloxapi, asyncio
import requests
import pathlib
import colorama
import os, sys
import time
from pathlib import Path
from colorama import *
from itertools import product
import random

client = robloxapi.Client()
current_path = os.path.dirname(os.path.realpath(__file__))
open(current_path +"/"+str("Available")+str("")+".txt","a") #Creates 'Available.txt'
open(current_path +"/"+str("Usernames")+str("")+".txt","a") #Creates 'Usernames.txt'
available = open('Available.txt', 'w')
mypath = Path('Usernames.txt')
numberOfUsernames = 0

# Generate 4-letter combinations with any characters
def generate_4_letter_combinations():
    return [''.join(c) for c in product('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', repeat=4)]

# Generate 5-letter combinations with only letters
def generate_5_letter_combinations():
    return [''.join(c) for c in product('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', repeat=5)]

async def check():
    print(Fore.LIGHTBLACK_EX+"["+Fore.CYAN+"+"+Fore.LIGHTBLACK_EX+"]"+"Roblox Username Sniper")

    usernames = generate_4_letter_combinations() + generate_5_letter_combinations()

    for username in usernames:
        attempt = 0
        max_attempts = 5
        while attempt < max_attempts:
            try:
                user = await client.get_user_by_username(username) #robloxapi either returns a user object or None if the user doesn't exist
                if user == None:
                    available.write(username + "\n") #The username isn't taken so we store it into 'Availables.txt'
                    print(Fore.WHITE+"["+Style.BRIGHT + Fore.GREEN + Back.BLACK+"Not Taken"+Fore.WHITE+"]" +Fore.WHITE +username)
                    global numberOfUsernames
                    numberOfUsernames += 1 #Counter for the total number of usernames

                else:
                    print(Fore.WHITE+"["+Style.BRIGHT + Fore.RED + Back.BLACK+"Taken"+Fore.WHITE+"]" +Fore.WHITE +username)

                break  # Exit the loop if the request is successful

            except robloxapi.exceptions.RobloxAPIError as e:
                if e.response.status_code == 429:  # Rate limited
                    wait_time = 2 ** attempt + random.uniform(0, 1)  # Exponential backoff with jitter
                    print(Fore.YELLOW + f"Rate limited. Retrying in {wait_time:.2f} seconds...")
                    await asyncio.sleep(wait_time)
                    attempt += 1
                else:
                    print(Fore.RED + f"Error: {e}")
                    break

tic = time.perf_counter() #Program timer start
asyncio.run(check())
toc = time.perf_counter() #Program timer stop
available.close()
print(Fore.CYAN+"\nChecker finished " + str(numberOfUsernames) + f" usernames in {toc - tic:0.4f} seconds")
print(Fore.RED +"Closing in 5 seconds")
time.sleep(5)
sys.exit()
