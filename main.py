import requests
import random
import string
import threading
import time
from queue import Queue

# Configuration
THREADS = 18                  # More stable thread count
TIMEOUT = 3                   # Longer timeout
OUTPUT_FILE = "premium_names.txt"
REQUEST_DELAY = 0.12          # 120ms between requests (safe but fast)

# Thread-safe setup
queue = Queue()
found = []
lock = threading.Lock()
running = True

def generate_name():
    """Generates either 4-char (alphanum) or 5-char (letters only)"""
    if random.choice([True, False]):
        # 4-character with numbers
        chars = string.ascii_lowercase + string.digits
        return ''.join(random.choice(chars) for _ in range(4))
    else:
        # 5-letter only
        return ''.join(random.choice(string.ascii_lowercase) for _ in range(5))

def check_name(name):
    url = f"https://auth.roblox.com/v1/usernames/validate?request.username={name}&request.birthday=2000-01-01"
    try:
        response = requests.get(url, timeout=TIMEOUT)
        
        # Handle rate limits
        if response.status_code == 429:
            time.sleep(3)
            return False
            
        if response.json().get("code") == 0:
            with lock:
                found.append(name)
                with open(OUTPUT_FILE, 'a') as f:
                    f.write(f"{name}\n")
            print(f"\033[92m[AVAILABLE] {name}\033[0m")
            return True
        print(f"\033[91m[taken] {name}\033[0m", end='\r', flush=True)
    except Exception as e:
        time.sleep(1)
    return False

def worker():
    while running:
        name = queue.get()
        check_name(name)
        queue.task_done()
        time.sleep(REQUEST_DELAY)  # Consistent delay between checks

def producer():
    while running:
        if queue.qsize() < 100:  # Keep queue filled
            queue.put(generate_name())
        else:
            time.sleep(0.01)

def main():
    global running
    print("\033[1m🔥 24/7 Name Sniper | 4-char & 5-letter\033[0m")
    
    # Start producer thread
    threading.Thread(target=producer, daemon=True).start()
    
    # Start worker threads
    for _ in range(THREADS):
        threading.Thread(target=worker, daemon=True).start()
    
    try:
        while True:
            time.sleep(1)
            if found:
                print(f"\n\033[1m💎 Found: {len(found)} | Last: {found[-1]}\033[0m")
    except KeyboardInterrupt:
        running = False
        print(f"\n\033[1m✅ Saved {len(found)} names to {OUTPUT_FILE}\033[0m")

if __name__ == "__main__":
    main()
