import requests
import random
import string
import threading
import time
from queue import Queue

# Configuration
THREADS = 22                  # Optimal thread count
TIMEOUT = 2.5                 # Request timeout
OUTPUT_FILE = "premium_names.txt"
MIN_DELAY = 0.055             # 55ms between requests (max speed without bans)

# Thread-safe setup
queue = Queue(maxsize=1000)
found = []
lock = threading.Lock()
running = True
last_request_time = time.time()

def generate_name():
    """Alternates perfectly between 4-char (alphanum) and 5-char (letters)"""
    if random.choice([True, False]):  # True=4-char, False=5-char
        chars = string.ascii_lowercase + string.digits
        return ''.join(random.choice(chars) for _ in range(4))
    else:
        return ''.join(random.choice(string.ascii_lowercase) for _ in range(5))

def check_name(name):
    global last_request_time
    url = f"https://auth.roblox.com/v1/usernames/validate?request.username={name}&request.birthday=2000-01-01"
    
    # Rate limit control
    elapsed = time.time() - last_request_time
    if elapsed < MIN_DELAY:
        time.sleep(MIN_DELAY - elapsed)
    last_request_time = time.time()
    
    try:
        response = requests.get(url, timeout=TIMEOUT)
        
        # Handle rate limits
        if response.status_code == 429:
            time.sleep(2.5)
            return False
            
        if response.json().get("code") == 0:
            with lock:
                found.append(name)
                with open(OUTPUT_FILE, 'a') as f:
                    f.write(f"{name}\n")
            print(f"\033[92m[✔] {name}\033[0m")
            return True
        print(f"\033[91m[✖] {name}\033[0m", end='\r', flush=True)
    except:
        pass
    return False

def worker():
    while running:
        try:
            name = queue.get(timeout=1)
            check_name(name)
            queue.task_done()
        except:
            continue

def main():
    global running
    print("\033[1m🔥 24/7 Name Sniper | 4-char & 5-letter | No Stops\033[0m")
    
    # Start threads
    threads = []
    for _ in range(THREADS):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        threads.append(t)
    
    try:
        while True:
            if queue.qsize() < THREADS * 3:
                queue.put(generate_name())
            else:
                time.sleep(0.001)  # Tiny sleep to prevent CPU overload
            
            # Stats every minute
            if time.time() % 60 < 0.1 and found:
                print(f"\n\033[1m💎 Found: {len(found)} | Last: {found[-1]}\033[0m")
                
    except KeyboardInterrupt:
        running = False
        print(f"\n\033[1m✅ Saved {len(found)} names to {OUTPUT_FILE}\033[0m")

if __name__ == "__main__":
    main()
