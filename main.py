import requests
import random
import string
import threading
import time
from queue import Queue

# Configuration
THREADS = 28                  # Optimal thread count
TIMEOUT = 2                   # Request timeout
OUTPUT_FILE = "premium_names.txt"

# Thread-safe setup
queue = Queue(maxsize=1000)
found = []
lock = threading.Lock()
running = True

def generate_name():
    """50% chance for 4-char (alphanumeric), 50% for 5-char (letters only)"""
    if random.random() > 0.5:
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
        if response.status_code == 429:
            time.sleep(1.5)  # Rate limit handling
            return False
        if response.json().get("code") == 0:
            with lock:
                found.append(name)
                with open(OUTPUT_FILE, 'a') as f:
                    f.write(f"{name}\n")
            print(f"\033[92m[AVAILABLE] {name}\033[0m")
            return True
        print(f"\033[91m[taken] {name}\033[0m", end='\r', flush=True)
    except:
        pass
    return False

def worker():
    while running:
        try:
            name = queue.get(timeout=1)
            check_name(name)
            queue.task_done()
            time.sleep(0.07)  # 70ms delay between checks
        except:
            continue

def main():
    global running
    print("\033[1m🔥 Scanning 4-char (alphanumeric) and 5-letter usernames\033[0m")
    
    # Start threads
    threads = []
    for _ in range(THREADS):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        threads.append(t)
    
    try:
        # Main producer loop
        while True:
            if queue.qsize() < THREADS * 10:
                queue.put(generate_name())
            else:
                time.sleep(0.01)
            
            # Stats every 2 minutes
            if time.time() % 120 < 0.1 and found:
                print(f"\n\033[1m💎 Found: {len(found)} | Last: {found[-1]}\033[0m\n")
                
    except KeyboardInterrupt:
        running = False
        print("\n🛑 Stopping gracefully...")
        for t in threads:
            t.join(timeout=1)
        print(f"\033[1m✅ Saved {len(found)} names to {OUTPUT_FILE}\033[0m")

if __name__ == "__main__":
    main()
