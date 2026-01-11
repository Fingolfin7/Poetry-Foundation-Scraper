# Scrape poems from the Poetry Foundation and build your personal offline treasure trove!

## Introduction
I came across the [Poetry Foundation](https://www.poetryfoundation.org/) website and spent a lot of time reading 
through the large of poems they have. 
I thought it was a good idea to practice making web-scrapers while building a personal offline collection of poems 
that I could read whenever I wanted. 

Along the way I found a large number of poems on Kaggle (can't remember exactle where from) and decided to include 
those files in a cleaned up/formatted json file (poems_old.json) with the project as a starter.
This project is the result of that effort.

## Project Structure

### Main Applications
- **`gui_app.py`**: 🎨 **NEW!** Modern graphical user interface (recommended)
- **`main.py`**: Command-line interface for searching and saving poems
- **`random_poem.py`**: Get a random poem from the collection

### GUI Package (`gui/`)
The GUI has been refactored into a clean, modular structure:
- **`app.py`**: Main application class
- **`styles.py`**: Theming and color configuration
- **`widgets.py`**: Widget creation and layout
- **`search_handlers.py`**: Search functionality
- **`display_handlers.py`**: Display operations
- **`event_handlers.py`**: Event handling
- **`README.md`**: Detailed GUI documentation

### Core Files
- **`Poems.py`**: Main `Poems` class for scraping and managing poems
- **`scraper.py`**: Web scraping functionality
- **`ChromeDrivers.py`**: Chrome WebDriver manager
- **`poems.json`**: Your personal poem collection (auto-created)
- **`poems_old.json`**: Starter collection from Kaggle dataset

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

### 🎨 Graphical Interface (Recommended)

Run the GUI application for the best experience:

```cmd
python gui_app.py
```

Features:
- Modern, intuitive interface with clickable links
- Search locally and online seamlessly
- Browse all poets and their poems
- Random poem discovery
- Save poems to custom locations
- Copy to clipboard functionality
- Right-click context menus
- Responsive design with background searches

See `gui/README.md` for detailed documentation.

### 💻 Command-Line Interface

For terminal users, run the classic CLI:

```cmd
python main.py
```

Pretty simple - follow the prompts to search for poems by title or author. 
After each search, you can choose to save the poem to a text file or continue searching. Saved text files are stored in
the `File Saves` directory in the project folder.

### 🎲 Random Poem

Get a random poem from your collection:

```cmd
python random_poem.py
```

### How It Works

All searches are automatically saved to the `poems.json` file for offline searching. Future searches will first search 
the offline collection before scraping the website for faster results.



