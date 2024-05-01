# Scrape poems from the Poetry Foundation and build your personal offline treasure trove!

## Introduction
I came across the [Poetry Foundation](https://www.poetryfoundation.org/) website and spent a lot of time reading 
through the large of poems they have. 
I thought it was a good idea to practice making web-scrapers while building a personal offline collection of poems 
that I could read whenever I wanted. 

Along the way I found a large number of poems on Kaggle (can't remember exactle where from) and decided to include 
those files in a cleaned up/formatted json file (poems_old.json) with the project as a starter.
This project is the result of that effort.

## Project Files
The following are the more important files in the project:
- `main`: allows the user to search specific poems by title, author and then prints them to the console. 
  Users can also save the poems to a separate text file.
- `random_poem.py`: get a random poem from the collection and print it to the console.
- `Poems.py`: contains the main `Poems` class that is used to scrape the poems from the Poetry Foundation website.
- `scraper.py`: contains a function that does the actual scraping of the poems from the website.
- `ChromeDrivers.py`: the file that contains a custom manager class for creating a chrome driver instance and or downloading 
  the appropriate driver for the user's version of Chrome to the project directory if it doesn't exist.
- `poems_old.json`: contains poems from the Kaggle csv file I found in a cleaned up format. 
(this is normally separate from your main save file, poems.json, but you can always rename it and use 
these as a starting point)

## Setup

Download the project files and run the following command in the project directory to install the required packages 
(a virtual environment would be a good idea):

```cmd
pip install -r requirements.txt
```

If you'd like, rename the `poems_old.json` file to `poems.json` to use the Kaggle poems as a starting point. Or start 
from scratch by deleting the `poems.json` file (or ignoring it) and running the `main.py` file to scrape the your own 
from the Poetry Foundation website.

## Usage

Pretty simple, run the `main` file and follow the prompts to search for poems by title or author. 
After each search, you can choose to save the poem to a text file or continue searching. Saved text files are stored in
the `File Saves` directory in the project folder.

All searches are automatically saved to the `poems.json` file for offline searching. Future searches will first search 
the offline collection before scraping the website for faster results.

If you'd like to get a random poem from the collection, run the `random_poem.py` file.


