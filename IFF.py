import instaloader
import json
import os
import logging
from datetime import datetime
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# Load configuration from config.json
config_file = "config.json"
if not os.path.exists(config_file):
    raise FileNotFoundError(f"{config_file} not found. Please create the file with appropriate credentials and version information.")

with open(config_file, "r") as file:
    config = json.load(file)

username = config.get("username")
password = config.get("password")
target_username = config.get("target_username")
version = config.get("version", "1.0.0")

if not all([username, password, target_username]):
    raise ValueError("Credentials and target username must be provided in the config.json file.")

# Initialize Instaloader
L = instaloader.Instaloader()

try:
    # Login
    print(f"Logging in as {username}...")
    L.login(username, password)

    # Get profile
    print(f"Fetching profile of {target_username}...")
    profile = instaloader.Profile.from_username(L.context, target_username)

    # Get followers and followings
    print("Fetching followers and followings...")
    current_followers = [follower.username for follower in profile.get_followers()]
    current_followings = [following.username for following in profile.get_followees()]

    # Load previous followers and followings from file
    data_file = "followers_followings.json"
    if os.path.exists(data_file):
        with open(data_file, "r") as file:
            data = json.load(file)
            previous_followers = data.get("followers", [])
            previous_followings = data.get("followings", [])
    else:
        previous_followers = []
        previous_followings = []

    # Compare followers
    new_followers = set(current_followers) - set(previous_followers)
    lost_followers = set(previous_followers) - set(current_followers)

    # Compare followings
    new_followings = set(current_followings) - set(previous_followings)
    lost_followings = set(previous_followings) - set(current_followings)

    # Save current followers and followings to file
    print("Saving current followers and followings...")
    with open(data_file, "w") as file:
        json.dump({"followers": current_followers, "followings": current_followings}, file, indent=4)

    # Set up logging
    logging.basicConfig(filename='changes.log', level=logging.INFO, format='%(asctime)s - %(message)s')
    logger = logging.getLogger()

    # Function to print colored messages
    def print_colored(message, color=Fore.WHITE):
        print(color + message)

    # Log changes
    if new_followers or lost_followers or new_followings or lost_followings:
        logger.info("Changes detected:")
        print_colored("Changes detected:", Fore.CYAN)
        if new_followers:
            logger.info(f"New followers: {new_followers}")
            print_colored(f"New followers: {new_followers}", Fore.GREEN)
        if lost_followers:
            logger.info(f"Lost followers: {lost_followers}")
            print_colored(f"Lost followers: {lost_followers}", Fore.RED)
        if new_followings:
            logger.info(f"New followings: {new_followings}")
            print_colored(f"New followings: {new_followings}", Fore.GREEN)
        if lost_followings:
            logger.info(f"Lost followings: {lost_followings}")
            print_colored(f"Lost followings: {lost_followings}", Fore.RED)
    else:
        logger.info("No changes detected.")
        print_colored("No changes detected.", Fore.YELLOW)

    # Print summary to console
    print("\nSummary:")
    print_colored(f"New followers: {len(new_followers)}", Fore.GREEN)
    print_colored(f"Lost followers: {len(lost_followers)}", Fore.RED)
    print_colored(f"New followings: {len(new_followings)}", Fore.GREEN)
    print_colored(f"Lost followings: {len(lost_followings)}", Fore.RED)

except instaloader.exceptions.InstaloaderException as e:
    print(f"Error: {e}")
    logging.error(f"Error: {e}")

except Exception as e:
    print(f"Unexpected error occurred: {e}")
    logging.exception("Unexpected error occurred")

finally:
    # Always close Instaloader session
    L.close()
    print("Session closed.")
