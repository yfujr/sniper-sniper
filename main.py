import requests
import random
import string
import threading
import time
import os

# Configuration
THREADS = 350  # Adjust as needed
FILE_AVAILABLE = 'valid.txt'
FILE_CHECKED = 'checked.txt'
BIRTHDAY = '1999-04-20'
LOG_TAKEN = True  # Show taken usernames too

# Colors for terminal output
class bcolors:
    OK = '\033[94m'
    FAIL = '\033[91m'
    END = '\033[0m'

# Thread-safe sets and locks
lock = threading.Lock()
found = 0
checked_usernames = set()

# Load previously checked usernames to avoid repeats across runs
if os.path.exists(FILE_CHECKED):
    with open(FILE_CHECKED, 'r') as f:
        checked_usernames = set(line.strip() for line in f if line.strip())

def save_checked(username):
    with lock:
        with open(FILE_CHECKED, 'a') as f:
            f.write(username + '\n')
        checked_usernames.add(username)

def log_success(username):
    global found
    with lock:
        found += 1
        print(f"{bcolors.OK}[{found}] [+] {username} is available{bcolors.END}")
        with open(FILE_AVAILABLE, 'a') as f:
            f.write(username + '\n')

def log_taken(username):
    if LOG_TAKEN:
        with lock:
            print(f"{bcolors.FAIL}[-] {username} is taken{bcolors.END}")

def make_username():
    while True:
        length = random.choice([4, 5])

        if length == 4:
            # Positions: 0 1 2 3
            pos0_chars = string.ascii_lowercase + string.digits
            pos1_chars = string.ascii_lowercase + string.digits + '_'
            pos2_chars = string.ascii_lowercase + string.digits + '_'
            pos3_chars = string.ascii_lowercase + string.digits

            uname = (
                random.choice(pos0_chars) +
                random.choice(pos1_chars) +
                random.choice(pos2_chars) +
                random.choice(pos3_chars)
            )

        else:  # length == 5
            # Positions: 0 1 2 3 4
            pos0_chars = string.ascii_lowercase
            pos1_chars = string.ascii_lowercase + '_'
            pos2_chars = string.ascii_lowercase + '_'
            pos3_chars = string.ascii_lowercase + '_'
            pos4_chars = string.ascii_lowercase

            uname = (
                random.choice(pos0_chars) +
                random.choice(pos1_chars) +
                random.choice(pos2_chars) +
                random.choice(pos3_chars) +
                random.choice(pos4_chars)
            )

        # Reject if double underscore anywhere
        if '__' in uname:
            continue
        # Reject if username already checked
        if uname in checked_usernames:
            continue

        return uname

def check_username_with_status(username):
    url = f"https://auth.roblox.com/v1/usernames/validate?request.username={username}&request.birthday={BIRTHDAY}"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 429:
            return None, 429
        r.raise_for_status()
        return r.json().get('code') == 0, r.status_code
    except requests.RequestException:
        return None, None

def worker():
    global found
    while True:
        username = make_username()
        result, status = check_username_with_status(username)

        if status == 429:
            print(f"{bcolors.FAIL}[!] Rate limited. Pausing thread for 60s...{bcolors.END}")
            time.sleep(60)
            continue

        if result is None:
            # Probably network error or other issue, short sleep to avoid spamming
            time.sleep(1)
            continue

        save_checked(username)

        if result:
            log_success(username)
        else:
            log_taken(username)

# Start threads
print(f"[*] Starting {THREADS} threads... Press Ctrl+C to stop.\n")
for i in range(THREADS):
    threading.Thread(target=worker, daemon=True).start()

# Keep main thread alive
try:
    while True:
        time.sleep(10)
except KeyboardInterrupt:
    print("\n[!] Stopped by user.")
