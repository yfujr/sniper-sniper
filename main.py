import requests
import random
import string
import threading
import time

# Configuration
THREADS = 8
FILE = 'valid.txt'
BIRTHDAY = '1999-04-20'
LOG_TAKEN = True  # Show taken usernames

# Colors
class bcolors:
    OK = '\033[94m'
    FAIL = '\033[91m'
    END = '\033[0m'

# Shared counters & data
lock = threading.Lock()
found = 0
successful_usernames = []

def log_success(username, thread_id):
    global found
    with lock:
        found += 1
        successful_usernames.append(username)
        print(f"{bcolors.OK}[{found}] [+] {username} is available [T{thread_id}]{bcolors.END}")
        with open(FILE, 'a') as f:
            f.write(username + '\n')

def log_taken(username, thread_id):
    if LOG_TAKEN:
        with lock:
            print(f"{bcolors.FAIL}[TAKEN] {username} [T{thread_id}]{bcolors.END}")

def make_username():
    length = 4
    chars = string.ascii_lowercase + string.digits  # 4-letter usernames can have letters + digits
    while True:
        uname = ''.join(random.choices(chars, k=length))
        if '__' in uname or uname.startswith('_') or uname.endswith('_'):
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
        result, status = check_username_with_status(username)

        if status == 429:
            print(f"{bcolors.FAIL}[T{thread_id}] Rate limited. Skipping...{bcolors.END}")
            continue
        if result is None:
            continue

        if result:
            log_success(username, thread_id)
        else:
            log_taken(username, thread_id)

# Start threads
print(f"[*] Starting {THREADS} threads searching only 4-letter usernames... Press Ctrl+C to stop.\n")
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
