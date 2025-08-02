import requests
import random
import string
import threading
import time
import os

# Configuration
THREADS = 350
VALID_FILE = 'valid.txt'
CHECKED_FILE = 'checked.txt'
BIRTHDAY = '1999-04-20'
LOG_TAKEN = True  # Show taken usernames

# Colors
class bcolors:
    OK = '\033[94m'
    FAIL = '\033[91m'
    END = '\033[0m'

# Shared data
lock = threading.Lock()
found = 0
successful_usernames = []
checked_usernames = set()

# Load previously checked usernames from file into the set
if os.path.exists(CHECKED_FILE):
    with open(CHECKED_FILE, 'r') as f:
        for line in f:
            checked_usernames.add(line.strip())

def log_success(username, thread_id):
    global found
    with lock:
        found += 1
        successful_usernames.append(username)
        print(f"{bcolors.OK}[{found}] [+] {username} is available [T{thread_id}]{bcolors.END}")
        with open(VALID_FILE, 'a') as f:
            f.write(username + '\n')

def log_taken(username, thread_id):
    if LOG_TAKEN:
        with lock:
            print(f"{bcolors.FAIL}[TAKEN] {username} [T{thread_id}]{bcolors.END}")

def record_checked(username):
    # Save checked username to file and set (thread-safe)
    with lock:
        if username not in checked_usernames:
            checked_usernames.add(username)
            with open(CHECKED_FILE, 'a') as f:
                f.write(username + '\n')

def make_username():
    length = 4
    pos0_chars = string.ascii_lowercase + string.digits
    pos1_chars = string.ascii_lowercase + string.digits + '_'
    pos2_chars = string.ascii_lowercase + string.digits + '_'
    pos3_chars = string.ascii_lowercase + string.digits

    while True:
        uname = (
            random.choice(pos0_chars) +
            random.choice(pos1_chars) +
            random.choice(pos2_chars) +
            random.choice(pos3_chars)
        )
        # Reject if double underscore anywhere
        if '__' in uname:
            continue
        # Reject if username starts or ends with underscore
        if uname[0] == '_' or uname[-1] == '_':
            continue
        return uname

def check_username_with_status(username):
    url = f"https://auth.roblox.com/v1/usernames/validate?request.username={username}&request.birthday={BIRTHDAY}"
    try:
        r = requests.get(url)
        if r.status_code == 429:
            return None, 429
        r.raise_for_status()
        return r.json().get('code') == 0, r.status_code
    except requests.RequestException:
        return None, None

def worker(thread_id):
    while True:
        username = make_username()

        with lock:
            if username in checked_usernames:
                continue  # Skip duplicate

        result, status = check_username_with_status(username)

        if status == 429:
            print(f"{bcolors.FAIL}[T{thread_id}] Rate limited. Skipping...{bcolors.END}")
            time.sleep(5)
            continue

        if result is None:
            time.sleep(0.1)
            continue

        record_checked(username)

        if result:
            log_success(username, thread_id)
        else:
            log_taken(username, thread_id)

# Start threads
print(f"[*] Starting {THREADS} threads searching only 4-letter usernames with duplicate avoidance... Press Ctrl+C to stop.\n")
for i in range(THREADS):
    threading.Thread(target=worker, args=(i+1,), daemon=True).start()

# Main thread: Wait and show summary on exit
try:
    while True:
        time.sleep(10)
except KeyboardInterrupt:
    print("\n[!] Stopped by user.")
    print(f"\n✅ Found {found} valid 4-letter usernames:\n")
    for u in successful_usernames:
        print(f" - {u}")


