import requests
from bs4 import BeautifulSoup
import json
import time

# Base URL for Fandom
BASE_URL = "https://aceattorney.fandom.com"

# Category Page with character links (excluding the first page with "*")
CHARACTER_LIST_URL = "https://aceattorney.fandom.com/wiki/Category:Characters?from=Jurors"

# Headers to mimic a browser request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Function to clean extracted text
def clean_text(text):
    if text:
        text = text.strip()
        text = text.split("\n", 1)
        return text[1]
    return None

# Function to extract character data from the page
def extract_character_data(soup):
    character_info = {}

    # Define the fields we want to extract based on data-source
    fields = ["name", "image", "occupation", "birthday", "eyes", "hair", "debut"]

    for field in fields:
        if field == "image":
            # For the image(s), we need to look inside the <figure> or tabbed <div>
            images = []
            
            # First, check for a simple <figure> tag with the data-source="image" (for single images)
            figure = soup.find("figure", {"data-source": field})
            if figure:
                img_tag = figure.find("img")
                if img_tag:
                    images.append(img_tag.get("src"))
            
            # Now, check for tabbed images under the class 'pi-image-collection'
            image_collection = soup.find("div", {"data-source": field})
            if image_collection:
                # Find all <figure> tags within the tabbed content
                for tab_content in image_collection.find_all("div", class_="wds-tab__content"):
                    img_tag = tab_content.find("img")
                    if img_tag:
                        images.append(img_tag.get("src"))
            
            # Store the images list (either single or multiple)
            character_info[field] = images if images else None
        else:
            # For other fields, we look for a <div> tag with the corresponding 'data-source'
            div = soup.find("div", {"data-source": field})
            if div:
                text = clean_text(div.get_text())
                character_info[field] = text
            else:
                character_info[field] = None

    return character_info

# Function to get character links from a page
def get_character_links(page_url):
    # Fetch the page with character links
    response = requests.get(page_url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")

    # Find all character links (members of the category)
    character_links = []
    for link in soup.select("div.category-page__members a.category-page__member-link"):
        char_name = link.text.strip()
        char_url = BASE_URL + link["href"]
        character_links.append({"name": char_name, "url": char_url})

    return character_links, soup

# Function to save data incrementally to the JSON file after each character
def save_to_json(data, filename="characters.json"):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            existing_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = []

    existing_data.append(data)

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, indent=4, ensure_ascii=False)

# Start with the first category page that doesn't contain "*" characters
current_page_url = CHARACTER_LIST_URL

# Loop through pages until no next page is available
while current_page_url:
    print(f"Fetching page: {current_page_url}")
    
    # Get character links from the current page
    character_links, soup = get_character_links(current_page_url)

    # Loop through the character links and extract data
    for char in character_links:
        print(f"Starting {char['name']} scraping")
        if "Category" in char['name'] :
            print("Not a character : skipping")
        else : 
            time.sleep(1)  # Adding a delay between requests
            char_response = requests.get(char["url"], headers=HEADERS)
            char_soup = BeautifulSoup(char_response.text, "html.parser")

            # Extract character details from the page
            character_data = extract_character_data(char_soup)

            # Add name and URL to the data
            character_data["name"] = char["name"]
            character_data["url"] = char["url"]

            # Save the character data after processing each character
            save_to_json(character_data)

    # Check if there is a "next page" link
    next_page_link = soup.find("a", {"class": "category-page__pagination-next"})
    
    if next_page_link:
        # If there's a next page, update the current_page_url to the next page
        current_page_url = BASE_URL + next_page_link["href"]
    else:
        # No more pages, exit the loop
        current_page_url = None

print("✅ Scraping Complete! Data saved incrementally in characters.json")
