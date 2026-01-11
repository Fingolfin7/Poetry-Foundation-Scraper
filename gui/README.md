# Poetry Foundation Explorer - GUI

A modern, user-friendly graphical interface for exploring and managing poetry from the Poetry Foundation database.

## 🚀 Quick Start

### Running the Application

```bash
python gui_app.py
```

## 📋 Features

### Search & Discovery
- **Smart Search**: Search by poem title, poet name, or both
- **Local & Online**: Searches local database first, then Poetry Foundation if needed
- **Random Poem**: Discover poetry serendipitously
- **Browse Poets**: View all poets in the database
- **Browse by Poet**: See all poems by a specific poet

### Interactive Interface
- **Clickable Links**: Click on poet names to see their poems
- **Click Poem Titles**: Click any poem title to read it instantly
- **Responsive UI**: Background searches don't freeze the interface
- **Modern Design**: Clean, professional appearance with emoji icons

### Save & Share
- **Save Poems**: Save any poem as a text file
- **Copy to Clipboard**: Quick copy for sharing
- **Context Menus**: Right-click for copy/paste options
- **Keyboard Shortcuts**: Enter to search, Ctrl+C/V for copy/paste

## 🏗️ Architecture

The GUI has been refactored into a modular structure for better maintainability:

```
gui/
├── __init__.py          # Package initialization
├── app.py               # Main application class
├── styles.py            # Styling and theme configuration
├── widgets.py           # Widget creation and layout
├── search_handlers.py   # Search functionality
├── display_handlers.py  # Display and list operations
└── event_handlers.py    # Event handling and user interactions
```

### Module Responsibilities

- **app.py**: Main `PoemAppGUI` class that orchestrates all components
- **styles.py**: Centralized color schemes and text tag configurations
- **widgets.py**: Widget creation, layout management, and event binding
- **search_handlers.py**: Local and online search logic
- **display_handlers.py**: Poem display, random selection, and listing operations
- **event_handlers.py**: Click handlers, context menus, save/copy operations

## 🎨 Customization

### Colors
Edit `gui/styles.py` to customize the color scheme:

```python
class AppStyles:
    BG_COLOR = "#f5f6fa"
    DARK_BG = "#2c3e50"
    ACCENT_COLOR = "#3498db"
    SUCCESS_COLOR = "#27ae60"
    # ... more colors
```

### Fonts
Modify font settings in `gui/styles.py`:

```python
font=('Segoe UI', 10)  # For labels
font=('Georgia', 11)   # For poem text
```

## 🔧 Development

### Adding New Features

1. **New Search Feature**: Add to `search_handlers.py`
2. **New Display Feature**: Add to `display_handlers.py`
3. **New UI Element**: Add to `widgets.py`
4. **New Event Handler**: Add to `event_handlers.py`

### Code Structure Benefits

- **Separation of Concerns**: Each module has a single responsibility
- **Easy Testing**: Individual modules can be tested independently
- **Maintainability**: Changes to one feature don't affect others
- **Scalability**: Easy to add new features without bloating one file

## 📝 Usage Tips

1. **Quick Search**: Type and press Enter - no need to click the button
2. **Alternative Results**: If a poem isn't found, related poems are shown
3. **Navigation**: Use clickable links to browse through poets and poems
4. **Save Location**: Choose where to save poems using the file dialog
5. **Copy Everything**: Use "Copy to Clipboard" to copy all visible content

## 🐛 Troubleshooting

### GUI Won't Start
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check that the `gui/` directory is in the same folder as `gui_app.py`

### Poems Not Found
- The application needs `poems.json` for local searches
- Online search requires internet connection

### Visual Issues
- The app is optimized for Windows with Segoe UI font
- Minimum window size: 800x600

## 🔗 Related Files

- **gui_main.py**: Original monolithic version (kept for reference)
- **main.py**: Command-line interface version
- **Poems.py**: Core poem data handling class

## 📄 License

See main README.md for project license information.

