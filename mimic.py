from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import random
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Twitter credentials from environment variables
TWITTER_USERNAME = os.getenv('TWITTER_USERNAME')
TWITTER_PASSWORD = os.getenv('TWITTER_PASSWORD')

if not TWITTER_USERNAME or not TWITTER_PASSWORD:
    raise ValueError("Please set TWITTER_USERNAME and TWITTER_PASSWORD environment variables")

# Get username from user input
username = input("Enter the Twitter username to monitor (without @): ")
print(f"Logging into X to monitor @{username}'s activity...")

# List of common user agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36"
]

# Configure Chrome options with stealth settings
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

# Add random user agent
chrome_options.add_argument(f'user-agent={random.choice(USER_AGENTS)}')

# Add additional stealth settings
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-gpu')

# Configure Selenium (using Chrome)
driver = webdriver.Chrome(options=chrome_options)

last_activity = None

def random_delay(min_seconds=2, max_seconds=5):
    """Add random delay between actions"""
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)

def human_type(element, text):
    """Type text in a human-like manner"""
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.1, 0.3))

def handle_security_prompt(driver):
    """Handle various security prompts that might appear"""
    try:
        # Check for password change prompt
        password_change = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Change password')]"))
        )
        if password_change:
            print("Detected password change prompt. Skipping...")
            return True
    except:
        pass

    try:
        # Check for verification prompt
        verify_button = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Verify')]"))
        )
        if verify_button:
            print("Detected verification prompt. Skipping...")
            return True
    except:
        pass

    return False

def login_to_twitter(driver):
    print("\n=== Starting Twitter Login ===")
    try:
        # Navigate to Twitter login page
        driver.get("https://twitter.com/login")
        random_delay(3, 5)
        
        # Enter username
        print("Entering username...")
        username_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[autocomplete="username"]'))
        )
        human_type(username_input, TWITTER_USERNAME)
        random_delay(1, 2)
        
        # Click next button
        next_button = driver.find_element(By.XPATH, "//span[text()='Next']")
        next_button.click()
        random_delay(2, 3)
        
        # Enter password
        print("Entering password...")
        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="password"]'))
        )
        human_type(password_input, TWITTER_PASSWORD)
        random_delay(1, 2)
        
        # Click login button
        login_button = driver.find_element(By.XPATH, "//span[text()='Log in']")
        login_button.click()
        random_delay(5, 7)
        
        # Check for security prompts
        if handle_security_prompt(driver):
            print("Security prompt detected. Please handle it manually.")
            return False
        
        print("Login successful!")
        print("=== Completed Twitter Login ===\n")
        return True
        
    except Exception as e:
        print(f"Login failed: {e}")
        return False

# Login before starting the monitoring
if not login_to_twitter(driver):
    print("Failed to login to Twitter. Exiting...")
    driver.quit()
    exit(1)

def get_latest_activity(driver, username):
    driver.get(f"https://x.com/{username}")
    time.sleep(3)
    
    # Wait for tweets to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="tweet"]'))
    )
    
    # Get the first tweet (most recent)
    latest_tweet = driver.find_element(By.CSS_SELECTOR, '[data-testid="tweet"]')
    
    # Extract tweet text and engagement data
    try:
        tweet_text = latest_tweet.find_element(By.CSS_SELECTOR, '[data-testid="tweetText"]').text
        reply_count = latest_tweet.find_element(By.CSS_SELECTOR, '[data-testid="reply"]').text or "0"
        retweet_count = latest_tweet.find_element(By.CSS_SELECTOR, '[data-testid="retweet"]').text or "0"
        like_count = latest_tweet.find_element(By.CSS_SELECTOR, '[data-testid="like"]').text or "0"
        
        activityInfo = {
            "tweet_text": tweet_text,
            "replies": int(reply_count) if reply_count.isdigit() else 0,
            "retweets": int(retweet_count) if retweet_count.isdigit() else 0,
            "likes": int(like_count) if like_count.isdigit() else 0,
            "tweet_url": latest_tweet.find_element(By.CSS_SELECTOR, 'a[href*="/status/"]').get_attribute("href")
        }
        json_string = json.dumps(activityInfo, indent=4)
        print(json_string)
        return activityInfo
    except:
        return None


def check_for_new_activity(driver):
    global last_activity
    current_activity = get_latest_activity(driver, username)
    
    if not last_activity:
        last_activity = current_activity
        return None
    
    # Check if engagement counts increased or if it's a new tweet
    new_actions = {}
    
    # Check for new tweet
    if current_activity["tweet_text"] != last_activity["tweet_text"]:
        new_actions["new_tweet"] = True
    
    if current_activity["replies"] > last_activity["replies"]:
        new_actions["reply"] = True
    
    if current_activity["retweets"] > last_activity["retweets"]:
        new_actions["retweet"] = True
    
    if current_activity["likes"] > last_activity["likes"]:
        new_actions["like"] = True
    
    last_activity = current_activity
    return new_actions if new_actions else None

def create_new_tweet(driver, tweet_text):
    print("\n=== Starting create_new_tweet function ===")
    print(f"Attempting to create tweet with text: {tweet_text}")
    try:
        # First navigate to home timeline to ensure we're not on a tweet's page
        print("Navigating to home timeline...")
        driver.get("https://x.com/home")
        random_delay(2, 3)

        # Click compose tweet button
        print("Looking for compose tweet button...")
        compose_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="SideNav_NewTweet_Button"]'))
        )
        print("Found compose button, clicking...")
        compose_button.click()
        random_delay(1, 2)
        
        # Type tweet text
        print("Looking for tweet text box...")
        tweet_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="tweetTextarea_0"]'))
        )
        print("Found tweet box, clearing any existing text...")
        tweet_box.clear()  # Clear any existing text
        print("Found tweet box, typing text...")
        human_type(tweet_box, tweet_text)
        random_delay(1, 2)
        
        # Post tweet
        print("Looking for post button...")
        post_button = driver.find_element(By.CSS_SELECTOR, '[data-testid="tweetButton"]')
        print("Found post button, clicking...")
        post_button.click()
        print("Tweet posted successfully")
        random_delay(3, 5)
        print("=== Completed create_new_tweet function ===\n")
        return True
        
    except Exception as e:
        print(f"Failed to create tweet: {e}")
        print(f"Error type: {type(e).__name__}")
        print("=== Failed create_new_tweet function ===\n")
        return False

def mirror_new_tweet(driver, tweet_text):
    print("\n=== Starting mirror_new_tweet function ===")
    # Wait a realistic delay (30-120 seconds) before posting
    wait_time = random.randint(30, 120)
    print(f"Waiting {wait_time} seconds before posting...")
    time.sleep(wait_time)
    
    # Create a similar but unique tweet
    similar_tweets = [
        f"Interesting take on this: {tweet_text[:100]}...",
        f"Agree with this perspective: {tweet_text[:100]}...",
        f"Great point about {tweet_text[:100]}...",
        f"Thanks for sharing this insight: {tweet_text[:100]}...",
        f"Important perspective: {tweet_text[:100]}..."
    ]
    
    new_tweet_text = random.choice(similar_tweets)
    print(f"Selected tweet text: {new_tweet_text}")
    
    create_new_tweet(driver, new_tweet_text)
    print("=== Completed mirror_new_tweet function ===\n")

def mirror_reply(driver, tweet_url):
    print("\n=== Starting mirror_reply function ===")
    print(f"Target tweet URL: {tweet_url}")
    
    # Wait a realistic delay (10-30 seconds)
    wait_time = random.randint(10, 30)
    print(f"Waiting {wait_time} seconds before replying...")
    time.sleep(wait_time)
    
    # Reply with a generic human-like comment
    possible_replies = [
        "Interesting perspective!",
        "I agree with this.",
        "Great take! 👏",
        "Thanks for sharing!",
    ]
    reply_text = random.choice(possible_replies)
    print(f"Selected reply text: {reply_text}")
    
    reply_to_tweet(driver, tweet_url, reply_text)
    print("=== Completed mirror_reply function ===\n")

def mirror_retweet(driver, tweet_url):
    # Wait 5-60 seconds before retweeting
    time.sleep(random.randint(5, 60))
    
    # Sometimes add a comment (30% chance)
    add_comment = random.random() < 0.3
    retweet(driver, tweet_url, add_comment)

def mirror_like(driver, tweet_url):
    # Wait 3-20 seconds before liking
    time.sleep(random.randint(3, 20))
    like_tweet(driver, tweet_url)

def monitor_and_mirror(driver, username, poll_interval=45):
    while True:
        try:
            print("Checking for new activity...")
            new_actions = check_for_new_activity(driver)
        
            if new_actions:
                print(f"Detected new activity: {new_actions}")
                
                if "new_tweet" in new_actions:
                    mirror_new_tweet(driver, last_activity["tweet_text"])
                
                if "reply" in new_actions:
                    mirror_reply(driver, last_activity["tweet_url"])
                
                if "retweet" in new_actions:
                    mirror_retweet(driver, last_activity["tweet_url"])
                
                if "like" in new_actions:
                    mirror_like(driver, last_activity["tweet_url"])
            
            # Randomize polling interval (30-90 sec)
            time.sleep(poll_interval + random.randint(-15, 15))
        
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)  # Wait a minute if something fails

def reply_to_tweet(driver, tweet_url, comment="Interesting take!"):
    print("\n--- Starting reply_to_tweet function ---")
    print(f"Navigating to tweet URL: {tweet_url}")
    driver.get(tweet_url)
    time.sleep(3)
    
    print("Attempting to click reply button...")
    # Click reply button
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="reply"]'))).click()
    print("Reply button clicked successfully")
    time.sleep(1)
    
    print("Typing reply text...")
    # Type reply
    reply_box = driver.find_element(By.CSS_SELECTOR, '[role="textbox"]')
    reply_box.send_keys(comment)
    print(f"Reply text entered: {comment}")
    time.sleep(1)
    
    print("Attempting to post reply...")
    # Post reply
    driver.find_element(By.CSS_SELECTOR, '[data-testid="tweetButton"]').click()
    print("Reply posted successfully")
    time.sleep(2)
    print("--- Completed reply_to_tweet function ---\n")

def retweet(driver, tweet_url, add_comment=False):
    driver.get(tweet_url)
    time.sleep(3)
    
    # Click retweet button
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="retweet"]'))).click()
    time.sleep(1)
    
    # Sometimes add a comment (like a human)
    if add_comment and random.random() > 0.7:  # 30% chance
        comment_box = driver.find_element(By.CSS_SELECTOR, '[role="textbox"]')
        comment_box.send_keys("Great point! " + random.choice(["👏", "🔥", "Thanks for sharing."]))
        time.sleep(1)
    
    # Confirm retweet
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="retweetConfirm"]'))).click()
    time.sleep(2)

def like_tweet(driver, tweet_url):
    driver.get(tweet_url)
    time.sleep(3)
    
    # Click like button
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="like"]'))).click()
    time.sleep(2)


monitor_and_mirror(driver, username=username, poll_interval=45)