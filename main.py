import requests
import string
import itertools
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

# === CONFIGURATION ===
MAX_USERNAMES = 50  # Limit to avoid hitting Roblox API too fast
DELAY_BETWEEN_REQUESTS = 1.5  # seconds
CHECK_4_LETTER = True
CHECK_5_LETTER = True
MAX_WORKERS = 10  # Number of concurrent requests

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_usernames():
    usernames = set()

    if CHECK_4_LETTER:
        charset = string.ascii_lowercase + string.digits
        for combo in itertools.product(charset, repeat=4):
            usernames.add("".join(combo))
            if len(usernames) >= MAX_USERNAMES:
                break

    if CHECK_5_LETTER and len(usernames) < MAX_USERNAMES:
        charset = string.ascii_lowercase
        for combo in itertools.product(charset, repeat=5):
            usernames.add("".join(combo))
            if len(usernames) >= MAX_USERNAMES:
                break

    return list(usernames)

def check_username(username):
    url = f"https://api.roblox.com/users/get-by-username?username={username}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get("Id") is None
    except requests.RequestException as e:
        logging.error(f"Error checking username {username}: {e}")
        return False

def main():
    usernames = generate_usernames()
    logging.info(f"Checking {len(usernames)} usernames...")

    available = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_username = {executor.submit(check_username, username): username for username in usernames}

        for future in as_completed(future_to_username):
            username = future_to_username[future]
            try:
                is_available = future.result()
                status = "Available" if is_available else "Taken"
                logging.info(f"[{status}] {username}")

                if is_available:
                    available.append(username)

            except Exception as exc:
                logging.error(f"Generated an exception: {exc}")

            time.sleep(DELAY_BETWEEN_REQUESTS)

    with open("Available.txt", "w") as f:
        for name in available:
            f.write(name + "\n")

    logging.info(f"\nDone. {len(available)} usernames available.")

if __name__ == "__main__":
    main()
