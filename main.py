import requests
import random
import string
import threading
import time

# Configuration
THREADS = 8
FILE = 'valid.txt'
BIRTHDAY = '1999-04-20'
LOG_TAKEN = True  # <- Now enabled

# Rate limiting
MAX_REQUESTS_PER_MIN = 500
SAFE_REQUESTS_PER_MIN = int(MAX_REQUESTS_PER_MIN * 0.9)
REQUESTS_PER_THREAD_PER_MIN = SAFE_REQUESTS_PER_MIN // THREADS
SLEEP_AFTER_429 = 60  # seconds

# Colors
class bcolors:
    OK = '\033[94m'
    FAIL = '\033[91m'
    END = '\033[0m'

# Shared counters
lock = threading.Lock()
found = 0

def log_success(username):
    global found
    with lock:
        found += 1
        print(f"{bcolors.OK}[{found}] [+] {username} is available{bcolors.END}")
        with open(FILE, 'a') as f:
            f.write(username + '\n')

def log_taken(username, thread_name):
    if LOG_TAKEN:
        with lock:
            print(f"{bcolors.FAIL}[{thread_name}] [TAKEN] {username}{bcolors.END}")

def make_username():
    length = random.choice([4, 5])
    chars = string.ascii_lowercase + string.digits if length == 4 else string.ascii_lowercase
    while True:
        uname = ''.join(random.choices(chars, k=length))
        if '__' in uname or uname.startswith('_') or uname.endswith('_'):
            continue
        return uname

def check_username_with_status(username):
    url = f"https://auth.roblox.com/v1/usernames/validate?request.username={username}&request.birthday={BIRTHDAY}"
    try:
        r = requests.get(url)  # No timeout for hotspot method
        if r.status_code == 429:
            return None, 429
        r.raise_for_status()
        return r.json().get('code') == 0, r.status_code
    except requests.RequestException:
        return None, None

def worker():
    count = 0
    window_start = time.time()
    thread_name = threading.current_thread().name

    while True:
        elapsed = time.time() - window_start
        if count >= REQUESTS_PER_THREAD_PER_MIN:
            if elapsed < 60:
                time.sleep(60 - elapsed)
            window_start = time.time()
            count = 0

        username = make_username()
        result, status = check_username_with_status(username)
        count += 1

        if status == 429:
            print(f"{bcolors.FAIL}[{thread_name}] [!] Rate limited. Sleeping {SLEEP_AFTER_429}s...{bcolors.END}")
            time.sleep(SLEEP_AFTER_429)
            continue

        if result is None:
            continue

        if result:
            log_success(username)
        else:
            log_taken(username, thread_name)

# Start threads
print(f"[*] Starting {THREADS} threads with live logging... Press Ctrl+C to stop.\n")
for i in range(THREADS):
    threading.Thread(target=worker, daemon=True, name=f"T{i+1}").start()

# Keep main thread alive
try:
    while True:
        time.sleep(10)
except KeyboardInterrupt:
    print("\n[!] Stopped by user.")
