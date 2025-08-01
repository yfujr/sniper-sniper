import requests
import random
import string
import threading
import time
from queue import Queue

# Configuration
THREADS = 18
TIMEOUT = 3
REQUEST_DELAY = 0.2   # Safer delay between requests
OUTPUT_FILE = "premium_names.txt"

# Shared resources
queue = Queue()
found_names = []
running = True
lock = threading.Lock()

def generate_name():
    """Generates a name: either 4-char alphanum or 5-letter"""
    if random.choice([True, False]):
        chars = string.ascii_lowercase + string.digits
        return ''.join(random.choices(chars, k=4))
    else:
        return ''.join(random.choices(string.ascii_lowercase, k=5))

def check_name(name):
    url = "https://auth.roblox.com/v1/usernames/validate"
    payload = {
        "username": name,
        "birthday": "2000-01-01"
    }

    try:
        response = requests.post(url, json=payload, timeout=TIMEOUT)

        if response.status_code == 429:
            print(f"\033[93m[Rate Limited] Sleeping...\033[0m")
            time.sleep(5)
            return False

        data = response.json()

        if data.get("code") == 0:
            with lock:
                found_names.append(name)
                with open(OUTPUT_FILE, 'a') as f:
                    f.write(f"{name}\n")
            print(f"\033[92m[AVAILABLE] {name}\033[0m")
            return True
        else:
            print(f"\033[91m[taken] {name}\033[0m", end='\r', flush=True)

    except Exception as e:
        print(f"\033[93m[Error] {name}: {e}\033[0m")
        time.sleep(1)

    return False

def producer():
    while running:
        if queue.qsize() < 100:
            queue.put(generate_name())
        else:
            time.sleep(0.05)

def worker():
    while running:
        name = queue.get()
        check_name(name)
        queue.task_done()
        time.sleep(REQUEST_DELAY)

def main():
    global running
    print("\033[1m🔥 Premium Name Finder | Roblox Username Checker\033[0m")

    threading.Thread(target=producer, daemon=True).start()

    for _ in range(THREADS):
        threading.Thread(target=worker, daemon=True).start()

    try:
        while True:
            time.sleep(1)
            if found_names:
                print(f"\n\033[1m💎 Found: {len(found_names)} | Last: {found_names[-1]}\033[0m")
    except KeyboardInterrupt:
        running = False
        print(f"\n\033[1m✅ Saved {len(found_names)} names to {OUTPUT_FILE}\033[0m")

if __name__ == "__main__":
    main()
