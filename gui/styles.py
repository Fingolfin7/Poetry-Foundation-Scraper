"""
GUI Styling Configuration
Centralizes all color schemes and style configurations for the application.
"""

from tkinter import ttk


class AppStyles:
    """Manages application-wide styling"""

    # Color scheme
    BG_COLOR = "#f5f6fa"
    DARK_BG = "#2c3e50"
    ACCENT_COLOR = "#3498db"
    ACCENT_HOVER = "#2980b9"
    SUCCESS_COLOR = "#27ae60"
    SUCCESS_HOVER = "#229954"
    ERROR_COLOR = "#e74c3c"
    TEXT_COLOR = "#2c3e50"
    SUBTLE_TEXT = "#7f8c8d"
    POEM_TEXT = "#34495e"
    STATUS_BG = "#34495e"
    STATUS_FG = "#ecf0f1"

    @staticmethod
    def configure_styles(root, style):
        """Configure all application styles"""
        style.theme_use('clam')
        root.configure(bg=AppStyles.BG_COLOR)

        # Title styling
        style.configure('Title.TLabel',
                       font=('Segoe UI', 20, 'bold'),
                       background=AppStyles.BG_COLOR,
                       foreground=AppStyles.DARK_BG,
                       padding=10)

        # Label styling
        style.configure('TLabel',
                       font=('Segoe UI', 10),
                       background=AppStyles.BG_COLOR,
                       foreground=AppStyles.DARK_BG)

        # Button styling
        style.configure('TButton',
                       font=('Segoe UI', 9, 'bold'),
                       padding=8,
                       relief='flat')

        style.map('TButton',
                 background=[('active', AppStyles.ACCENT_HOVER),
                           ('!active', AppStyles.ACCENT_COLOR)],
                 foreground=[('active', 'white'), ('!active', 'white')])

        # Action button styling (for Save, Copy)
        style.configure('Action.TButton',
                       font=('Segoe UI', 9, 'bold'),
                       padding=8,
                       relief='flat')

        style.map('Action.TButton',
                 background=[('active', AppStyles.SUCCESS_HOVER),
                           ('!active', AppStyles.SUCCESS_COLOR)],
                 foreground=[('active', 'white'), ('!active', 'white')])

        # Entry styling
        style.configure('TEntry',
                       font=('Segoe UI', 10),
                       fieldbackground='white',
                       borderwidth=2)

        # LabelFrame styling
        style.configure('TLabelframe',
                       background=AppStyles.BG_COLOR,
                       borderwidth=2,
                       relief='solid')

        style.configure('TLabelframe.Label',
                       font=('Segoe UI', 10, 'bold'),
                       background=AppStyles.BG_COLOR,
                       foreground=AppStyles.DARK_BG)

    @staticmethod
    def configure_text_tags(text_widget):
        """Configure text widget tags for different content types"""
        text_widget.tag_configure('title',
                                 font=('Georgia', 16, 'bold'),
                                 foreground=AppStyles.TEXT_COLOR,
                                 spacing1=10,
                                 spacing3=5)

        text_widget.tag_configure('poet',
                                 font=('Georgia', 13, 'italic'),
                                 foreground=AppStyles.SUBTLE_TEXT,
                                 spacing3=10)

        text_widget.tag_configure('poem',
                                 font=('Georgia', 12),
                                 foreground=AppStyles.POEM_TEXT,
                                 spacing1=5,
                                 lmargin1=20,
                                 lmargin2=20)

        text_widget.tag_configure('info',
                                 font=('Segoe UI', 10, 'italic'),
                                 foreground=AppStyles.ACCENT_COLOR,
                                 spacing3=5)

        text_widget.tag_configure('error',
                                 font=('Segoe UI', 10, 'bold'),
                                 foreground=AppStyles.ERROR_COLOR)

        text_widget.tag_configure('list_item',
                                 font=('Segoe UI', 10),
                                 foreground=AppStyles.TEXT_COLOR,
                                 spacing1=3)

        text_widget.tag_configure('clickable_poet',
                                 font=('Segoe UI', 10, 'bold'),
                                 foreground=AppStyles.SUCCESS_COLOR,
                                 underline=1)

        text_widget.tag_configure('clickable_poem',
                                 font=('Segoe UI', 10),
                                 foreground=AppStyles.ACCENT_COLOR,
                                 underline=1)

