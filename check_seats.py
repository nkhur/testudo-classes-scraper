import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

# Load environment from local .env if present
load_dotenv()

# Get secrets from environment variables (local/.env or CI)
PUSHOVER_TOKEN = os.getenv('PUSHOVER_TOKEN')
PUSHOVER_USER = os.getenv('PUSHOVER_USER')

URL = 'https://app.testudo.umd.edu/soc/202601/CMSC/CMSC414'

STATE_FILE = 'seats_state.txt'

def send_notification(message):
    if not PUSHOVER_TOKEN or not PUSHOVER_USER:
        print("Pushover credentials missing - skipping notification", PUSHOVER_TOKEN, PUSHOVER_USER)
        return
    
    try:
        resp = requests.post('https://api.pushover.net/1/messages.json', data={
            'token': PUSHOVER_TOKEN,
            'user': PUSHOVER_USER,
            'message': message,
            'title': 'CMSC414 Seats Alert'
        })
        if resp.status_code != 200:
            print(f"Notification failed: {resp.text}")
        else:
            print("Notification sent successfully:", message, resp.status_code)
    except Exception as e:
        print(f"Notification error: {e}")

def get_previous_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            content = f.read().strip()
            if content:
                return set(content.split(','))
    return set()

def save_state(open_sections):
    with open(STATE_FILE, 'w') as f:
        f.write(','.join(sorted(open_sections)))

# Fetch page
headers = {'User-Agent': 'Mozilla/5.0 (compatible; CMSC414-SeatChecker/1.0)'}
response = requests.get(URL, headers=headers, timeout=15)

if response.status_code != 200:
    print(f"Error fetching page: HTTP {response.status_code}")
    exit(1)

soup = BeautifulSoup(response.text, 'html.parser')

# Find all section containers
sections = soup.find_all('div', class_='section')

open_sections = set()

for section in sections:
    # Get section ID
    section_input = section.find('input', {'name': 'sectionId'})
    if not section_input:
        continue
    section_id = section_input.get('value')
    if not section_id:
        continue

    # Find open seats count
    open_seats_span = section.find('span', class_='open-seats-count')
    if open_seats_span:
        try:
            open_count = int(open_seats_span.get_text(strip=True))
            if open_count > 0:
                open_sections.add(section_id)
        except ValueError:
            print(f"Could not parse open seats for section {section_id}")
            continue

# Debug output
previous_open = get_previous_state()
print(f"Previous open sections: {sorted(previous_open)}")
print(f"Current open sections:  {sorted(open_sections)}")

# Detect newly opened sections
newly_opened = open_sections - previous_open

if newly_opened:
    sections_str = ', '.join(sorted(newly_opened))
    msg = f'New section(s) opened in CMSC414: {sections_str} seat(s) available! Check Testudo now: {URL}'
    send_notification(msg)
    print(f"Notification sent for new sections: {sections_str}")
else:
    print("No newly opened sections")

# Update state (even if no change)
save_state(open_sections)