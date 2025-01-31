import requests
from bs4 import BeautifulSoup
import json

# Character page URL
CHARACTER_PAGE_URL = "https://aceattorney.fandom.com/wiki/Phoenix_Wright"

# Headers to mimic a browser request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def remove_parentheses(text):
    result = []
    stack = 0  # Keeps track of opened parentheses

    for char in text:
        if char == "(":
            stack += 1
        elif char == ")" and stack > 0:
            stack -= 1
            continue  # Skip adding this character
        if stack == 0:
            result.append(char)

    return "".join(result).strip()


# Function to clean extracted text
def clean_text(text, as_list=False):
    if text:
        text = text.strip()
        text = text.split("\n", 1)[1]  # Removes the description of the field
        text = text.replace("*", "")  # Removes asterisks
        text = remove_parentheses(text)  # Properly remove nested parentheses
        
        if as_list:
            return [item.strip() for item in text.split("  ") if item.strip()]  # Splitting on double spaces
        return text.strip()
    return None

# Function to extract character data using the "data-source" attribute
def extract_character_data(soup):
    character_info = {}

    # Define the fields we want to extract based on data-source
    fields = ["image", "occupation", "birthday", "status", "eyes", "hair", "french", "debut"]
    
    for field in fields:
        if field == "image":
            # Handling multiple images
            images = []
            
            # Single image case
            figure = soup.find("figure", {"data-source": field})
            if figure:
                img_tag = figure.find("img")
                if img_tag:
                    images.append(img_tag.get("src"))

            # Multiple images case (in tabs)
            image_collection = soup.find("div", {"data-source": field})
            if image_collection:
                for tab_content in image_collection.find_all("div", class_="wds-tab__content"):
                    img_tag = tab_content.find("img")
                    if img_tag:
                        images.append(img_tag.get("src"))

            # Store images as a list
            character_info[field] = images if images else None

        else:
            # Extract text from div with data-source attribute
            div = soup.find("div", {"data-source": field})
            if div:
                as_list = field in ["occupation", "french"]  # Store these as arrays   
                text = clean_text(div.get_text(), as_list=as_list)
                character_info[field] = text
            else:
                character_info[field] = None  # Set to None if field is missing

    return character_info

# Fetch the character page
response = requests.get(CHARACTER_PAGE_URL, headers=HEADERS)
soup = BeautifulSoup(response.text, "html.parser")

# Extract character details
character_data = extract_character_data(soup)

# Append the name and URL (for reference)
character_data["name"] = CHARACTER_PAGE_URL.split("/", 4)[4].replace("_", " ")
character_data["url"] = CHARACTER_PAGE_URL

# Save as JSON
with open("single_char.json", "w", encoding="utf-8") as f:
    json.dump([character_data], f, indent=4, ensure_ascii=False)

print(f"✅ Scraping Complete! {character_data['name']}'s data saved in single_char.json")
