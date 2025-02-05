# Fandom Scrapper

A tool to help you scrap characters data from a specified fandom

# ⚠ Disclaimer ⚠ :

Be warned this tool was made only by myself with a fairly limited knowledge of scrapping as such don't be surprised if errors happen.
Keep in mind that this code requires a bit of knowledge to use (there is no UI and you have to edit the code in order to use it) but I still tried to make it somewhat easy to go through and change what you want.
This tool also might not work with every fandom, some don't have *Categories:Characters* pages they may have different names. It's up to you to check that

# Before using

This code requires a couple libraries in order to work just run the following command to install them :
```
pip install -r requirements.txt
```


# How it works

The code provided scraps characters from the [**Ace Attorney** Fandom](https://aceattorney.fandom.com/wiki/Category:Characters).

There is 2 python scripts :
- **single_character.py** : Scraps data for a single specified character (just change the link to the character you want)
- **all_characters.py** : Scraps data for every character

The functionment is the same for both the only difference being that **all_characters** repeats the operations of **single_characters** for every character

## Single Character

At the very top of **single_character.py** the constant *CHARACTER_PAGE_URL* contains the link to the page of the character you want to scrap, in our case **https://aceattorney.fandom.com/wiki/Phoenix_Wright**

In the **extract_character_data()** function we specify the fields we want. We then go through every field, depending on the fields the operations may differ :
- *single value* field : If a field only has one value we store it as one in the Json file
- *multiple values* field : Those require a bit more effort, later in the function there is another array where you specify what fields have multiple values, those wil be stored as an array in the Json file
- *image* is a special case as when a character has one or multiple images, they are scraped differently. In the end even a single image is stored in an array
  
The fields are then cleaned, here is what's removed :
- Fields descriptions
- "*" asterisks
- Text in parenthesis
  
Example of field cleaning :
- Occupation : Defense attorney (July 20, 2027 - present) // Starting text
- <s>Occupation :</s> Defense attorney (July 20, 2027 - present)  // Field description
- Defense attorney <s>(July 20, 2027 - present)</s> // Parenthesis
- Defense attorney // Final Text

## Every Character

For **all_characters** the link isn't for a single character but for the character page : **https://aceattorney.fandom.com/wiki/Category:Characters**. 

*Note that as a personal preference the link is actually **https://aceattorney.fandom.com/wiki/Category:Characters?from=1** meaning the scraping will start at page one instead of the default page.*
*This removes every non-canon character from being scrapped. If you truly want every single character keep the default **Category:Characters** link without **?from=1***

The way we get data for all character isn't very complicated. We just go through each subpage of the top link (page 1, page2, ...).
When we finish with a subpage we go to the next :
```
    next_page_link = soup.find("a", {"class": "category-page__pagination-next"})
    
    if next_page_link and next_page_link.get("href"):
        current_page_url = next_page_link["href"]
```

Between each each request, ```time.sleep(1)``` has been added, this ensures there is 1 second of delay between each one. 
This is to avoid getting timeout from the fandom page, if you still get blocked try increasing the delay. Keep in mind this will make the total scrapping time longer.

# Added Details 

The tool ins't limited to only scrapping character data, you can theoretically do it on every **Category** page but some things may have to be tweaked.

If you ever want to use this inside your code feel free to do it but please credit me if you do.
