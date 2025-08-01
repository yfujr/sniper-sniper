import requests
import random
import string
import threading
import time

# Config
THREADS = 2  # Number of threads (start with 10)
FILE = 'valid.txt'
BIRTHDAY = '1999-04-20'
LOG_TAKEN = False  # Set to True to show taken names

# Terminal colors
class bcolors:
    OK = '\033[94m'
    FAIL = '\033[91m'
    END = '\033[0m'

# Thread-safe print and file write
lock = threading.Lock()
found = 0

def log_success(username):
    global found
    with lock:
        found += 1
        print(f"{bcolors.OK}[{found}] [+] {username} is available{bcolors.END}")
        with open(FILE, 'a') as f:
            f.write(username + '\n')

def log_taken(username):
    if LOG_TAKEN:
        with lock:
            print(f"{bcolors.FAIL}[-] {username} is taken{bcolors.END}")

def make_username():
    length = random.choice([4, 5])
    chars = string.ascii_lowercase + string.digits if length == 4 else string.ascii_lowercase
    while True:
        uname = ''.join(random.choices(chars, k=length))
        if '__' in uname or uname.startswith('_') or uname.endswith('_'):
            continue
        return uname

def check_username(username):
    url = f"https://auth.roblox.com/v1/usernames/validate?request.username={username}&request.birthday={BIRTHDAY}"
    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        return r.json().get('code') == 0
    except Exception as e:
        return None

def worker():
    while True:
        username = make_username()
        result = check_username(username)
        if result is None:
            time.sleep(1)  # network error fallback
            continue
        if result:
            log_success(username)
        else:
            log_taken(username)

# Start threads
print(f"[*] Starting {THREADS} threads... Press Ctrl+C to stop.\n")
for _ in range(THREADS):
    threading.Thread(target=worker, daemon=True).start()

# Keep main thread alive
try:
    while True:
        time.sleep(10)
except KeyboardInterrupt:
    print("\n[!] Stopped by user.")
