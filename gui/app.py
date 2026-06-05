"""
Main Application Module
The main PoemAppGUI class that orchestrates all components.
"""

from tkinter import ttk
from Poems import Poems
from app_paths import resource_path
from gui.styles import AppStyles
from gui.widgets import WidgetBuilder
from gui.search_handlers import SearchHandlers
from gui.display_handlers import DisplayHandlers
from gui.event_handlers import EventHandlers


class PoemAppGUI:
    """Main GUI Application for Poetry Foundation Explorer"""

    def __init__(self, root):
        """
        Initialize the GUI application
        Args:
            root: Tk root window
        """
        self.root = root
        self.root.title("Poetry Foundation Explorer")
        self.root.geometry("1100x820")
        self.root.minsize(900, 650)

        # Set an app icon (prefer Windows .ico, fallback to .xbm)
        try:
            self.root.iconbitmap(resource_path("assets/app_icon.ico"))
        except Exception:
            try:
                self.root.iconbitmap("@" + resource_path("assets/app_icon.xbm"))
            except Exception:
                # If icon setting fails (platform/theme), ignore.
                pass

        # Initialize Poems data object
        self.poems = Poems()

        # Storage for current poem and clickable data
        self.current_poem_data = None
        self.clickable_data = {}

        # Initialize handler objects (they need reference to self)
        self.search_handlers = SearchHandlers(self)
        self.display_handlers = DisplayHandlers(self)
        self.event_handlers = EventHandlers(self)
        self.widget_builder = WidgetBuilder(self)

        # Configure styles
        self._setup_styles()

        # Build the GUI
        self._create_widgets()

    def _setup_styles(self):
        """Configure application-wide styles"""
        style = ttk.Style()
        AppStyles.configure_styles(self.root, style)

    def _create_widgets(self):
        """Create and layout all GUI widgets"""
        # Build widgets in order (bottom elements first for proper packing)
        self.widget_builder.create_header()
        self.widget_builder.create_search_frame()
        self.widget_builder.create_status_bar()
        self.widget_builder.create_action_buttons()
        self.widget_builder.create_results_frame()

        # Create context menus
        self.event_handlers.create_context_menu()

        # Bind all events
        self.widget_builder.bind_events()
