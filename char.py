import requests
from bs4 import BeautifulSoup
import json
import pandas as pd

# Base URL for Fandom
BASE_URL = "https://aceattorney.fandom.com"

# Phoenix Wright's page URL (or any character page you want to scrape)
CHARACTER_PAGE_URL = "https://aceattorney.fandom.com/wiki/Phoenix_Wright"

# Headers to mimic a browser request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Function to clean extracted text
def clean_text(text):
    return text.strip() if text else None

# Function to extract character data using the "data-source" attribute
def extract_character_data(soup):
    character_info = {}
    
    # Define the fields we want to extract based on data-source
    fields = [
        "image", "occupation", "birthday", "status", "eyes", "hair", 
        "family", "friends", "affiliates", "japanese", "amusical", "debut"
    ]
    
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
            # For other fields, we can use the div with data-source
            div = soup.find("div", {"data-source": field})
            if div:
                # Extract the text inside the div, clean it up
                text = clean_text(div.get_text())
                character_info[field] = text
            else:
                character_info[field] = None  # If no div is found, set it to None

    return character_info

# Fetch the character page
response = requests.get(CHARACTER_PAGE_URL, headers=HEADERS)
soup = BeautifulSoup(response.text, "html.parser")

# Extract character details from the "data-source" attributes
character_data = extract_character_data(soup)

# Append the name and URL (for reference)
character_data["name"] = "Leona Clyde"  # You can change this dynamically if needed
character_data["url"] = CHARACTER_PAGE_URL

# Save as JSON
with open("leona_clyde.json", "w", encoding="utf-8") as f:
    json.dump([character_data], f, indent=4, ensure_ascii=False)

# Save as CSV
df = pd.DataFrame([character_data])
df.to_csv("leona_clyde.csv", index=False, encoding="utf-8")

print(f"✅ Scraping Complete! Leona Clyde's data saved in leona_clyde.json and leona_clyde.csv")
