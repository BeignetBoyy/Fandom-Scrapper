import requests
from bs4 import BeautifulSoup
import json
import time

# Category Page with character links (excluding the first page with "*")
CHARACTER_LIST_URL = "https://aceattorney.fandom.com/wiki/Category:Characters?from=1"

# Headers to mimic a browser request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def remove_parentheses(text):
    result = []
    stack = 0  

    for char in text:
        if char == "(":
            stack += 1
        elif char == ")" and stack > 0:
            stack -= 1
            continue  
        if stack == 0:
            result.append(char)

    return "".join(result).strip()


def clean_text(text, as_list=False):
    if text:
        text = text.strip()
        text = text.split("\n", 1)[-1]  
        text = text.replace("*", "")  
        text = remove_parentheses(text)  
        
        if as_list:
            return [item.strip() for item in text.split("  ") if item.strip()]  
        return text.strip()
    return None


def extract_character_data(soup):
    character_info = {}

    fields = ["image", "occupation", "birthday", "status", "eyes", "hair", "french", "debut"]

    for field in fields:
        if field == "image":
            images = []
            figure = soup.find("figure", {"data-source": field})
            if figure:
                img_tag = figure.find("img")
                if img_tag:
                    images.append(img_tag.get("src"))
            
            image_collection = soup.find("div", {"data-source": field})
            if image_collection:
                for tab_content in image_collection.find_all("div", class_="wds-tab__content"):
                    img_tag = tab_content.find("img")
                    if img_tag:
                        images.append(img_tag.get("src"))
            
            character_info[field] = images if images else None
        else:
            div = soup.find("div", {"data-source": field})
            if div:
                as_list = field in ["occupation", "french"]  
                text = clean_text(div.get_text(), as_list=as_list)
                character_info[field] = text
            else:
                character_info[field] = None  

    return character_info


def get_character_links(page_url):
    try:
        response = requests.get(page_url, headers=HEADERS)
        response.raise_for_status()  
        soup = BeautifulSoup(response.text, "html.parser")

        character_links = []
        for link in soup.select("div.category-page__members a.category-page__member-link"):
            char_name = link.text.strip()
            char_url = page_url
            character_links.append({"name": char_name, "url": char_url})

        return character_links, soup
    except requests.RequestException as e:
        print(f"❌ Error fetching page {page_url}: {e}")
        return [], None


def save_to_json(data, filename="characters.json"):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            existing_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = []

    existing_data.append(data)

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, indent=4, ensure_ascii=False)


current_page_url = CHARACTER_LIST_URL

while current_page_url:
    print(f"📖 Fetching page: {current_page_url}")
    
    character_links, soup = get_character_links(current_page_url)
    if not soup:
        print("⚠️ Skipping due to an error retrieving the page.")
        break  

    for char in character_links:
        print(f"🔍 Scraping {char['name']}...")
        if "Category" in char['name']:
            print("⚠️ Not a character, skipping.")
            continue  

        try:
            time.sleep(1) # Waiting 1 second between each query to avoid getting timeout 
            char_response = requests.get(char["url"], headers=HEADERS)
            char_response.raise_for_status()  
            char_soup = BeautifulSoup(char_response.text, "html.parser")

            character_data = extract_character_data(char_soup)
            character_data["name"] = char["name"]
            character_data["url"] = char["url"]

            save_to_json(character_data)
        except requests.RequestException as e:
            print(f"❌ Error fetching character {char['name']}: {e}")

    next_page_link = soup.find("a", {"class": "category-page__pagination-next"})
    
    if next_page_link and next_page_link.get("href"):
        current_page_url = next_page_link["href"]
    else:
        print("✅ No more pages.")
        break  

print("🎉 Scraping Complete! Data saved incrementally in characters.json")
