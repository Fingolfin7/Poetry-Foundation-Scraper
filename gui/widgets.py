"""
Widgets Module
Handles creation and layout of GUI widgets.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from gui.styles import AppStyles


class WidgetBuilder:
    """Builds and configures GUI widgets"""

    def __init__(self, app):
        """
        Initialize with reference to main app
        Args:
            app: Main PoemAppGUI instance
        """
        self.app = app

    def create_header(self):
        """Create header section with title"""
        header_frame = tk.Frame(self.app.root, bg=AppStyles.DARK_BG, height=80)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        header_frame.pack_propagate(False)

        title_label = tk.Label(
            header_frame,
            text="🎭 Poetry Foundation Explorer",
            font=('Segoe UI', 24, 'bold'),
            bg=AppStyles.DARK_BG,
            fg='white'
        )
        title_label.pack(expand=True)

        subtitle_label = tk.Label(
            header_frame,
            text="Discover, Explore, and Save Beautiful Poetry",
            font=('Segoe UI', 10, 'italic'),
            bg=AppStyles.DARK_BG,
            fg=AppStyles.STATUS_FG
        )
        subtitle_label.pack()

    def create_search_frame(self):
        """Create search input section"""
        search_frame = ttk.LabelFrame(self.app.root, text="  🔍 Search Poems  ", padding=15)
        search_frame.pack(pady=(0, 15), padx=20, fill=tk.X)

        # Poem Name
        ttk.Label(search_frame, text="Poem Title:").grid(
            row=0, column=0, sticky=tk.W, pady=8, padx=(5, 10)
        )
        self.app.poem_name_entry = ttk.Entry(search_frame, width=40, font=('Segoe UI', 11))
        self.app.poem_name_entry.grid(row=0, column=1, pady=8, padx=5, sticky=tk.EW)

        # Poet Name
        ttk.Label(search_frame, text="Poet Name:").grid(
            row=1, column=0, sticky=tk.W, pady=8, padx=(5, 10)
        )
        self.app.poet_name_entry = ttk.Entry(search_frame, width=40, font=('Segoe UI', 11))
        self.app.poet_name_entry.grid(row=1, column=1, pady=8, padx=5, sticky=tk.EW)

        # NEW: Full-text search query
        ttk.Label(search_frame, text="Search Content:").grid(
            row=2, column=0, sticky=tk.W, pady=8, padx=(5, 10)
        )
        self.app.fulltext_entry = ttk.Entry(search_frame, width=40, font=('Segoe UI', 11))
        self.app.fulltext_entry.grid(row=2, column=1, pady=8, padx=5, sticky=tk.EW)

        # Info label for full-text search
        info_label = ttk.Label(
            search_frame,
            text="💡 Search inside poem text (e.g., 'love AND heart', '\"exact phrase\"')",
            font=('Segoe UI', 8, 'italic'),
            foreground='gray'
        )
        info_label.grid(row=3, column=1, sticky=tk.W, padx=5)

        search_frame.columnconfigure(1, weight=1)

        # Buttons
        self._create_search_buttons(search_frame)

    def _create_search_buttons(self, parent):
        """Create search action buttons"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(15, 5))

        ttk.Button(
            button_frame, text="🔍 Search",
            command=self.app.search_handlers.search_poem, width=12
        ).pack(side=tk.LEFT, padx=4)

        # NEW: Full-text search button
        ttk.Button(
            button_frame, text="📝 Search Content",
            command=self.app.search_handlers.fulltext_search, width=14
        ).pack(side=tk.LEFT, padx=4)

        ttk.Button(
            button_frame, text="📋 By Poet",
            command=self.app.display_handlers.list_poems_by_poet_button, width=12
        ).pack(side=tk.LEFT, padx=4)

        ttk.Button(
            button_frame, text="🎲 Random",
            command=self.app.display_handlers.random_poem, width=12
        ).pack(side=tk.LEFT, padx=4)

        ttk.Button(
            button_frame, text="📜 All Poets",
            command=self.app.display_handlers.list_all_poets, width=12
        ).pack(side=tk.LEFT, padx=4)

        ttk.Button(
            button_frame, text="🗑️ Clear",
            command=self.app.display_handlers.clear_results, width=10
        ).pack(side=tk.LEFT, padx=4)

    def create_status_bar(self):
        """Create status bar at bottom"""
        status_frame = tk.Frame(self.app.root, bg=AppStyles.STATUS_BG, height=30)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        status_frame.pack_propagate(False)

        self.app.status_var = tk.StringVar()
        self.app.status_var.set("Ready to explore poetry ✨")

        status_bar = tk.Label(
            status_frame,
            textvariable=self.app.status_var,
            bg=AppStyles.STATUS_BG,
            fg=AppStyles.STATUS_FG,
            font=('Segoe UI', 9),
            anchor=tk.W,
            padx=10
        )
        status_bar.pack(fill=tk.BOTH, expand=True)

    def create_action_buttons(self):
        """Create action buttons (Save, Copy, Help)"""
        action_frame = ttk.Frame(self.app.root)
        action_frame.pack(side=tk.BOTTOM, pady=10, padx=20, fill=tk.X)

        ttk.Button(
            action_frame, text="💾 Save to File",
            command=self.app.event_handlers.save_poem,
            style='Action.TButton', width=18
        ).pack(side=tk.LEFT, padx=5, pady=5)

        ttk.Button(
            action_frame, text="📋 Copy to Clipboard",
            command=self.app.event_handlers.copy_to_clipboard,
            style='Action.TButton', width=20
        ).pack(side=tk.LEFT, padx=5, pady=5)

        ttk.Button(
            action_frame, text="❓ Help",
            command=self.app.event_handlers.show_help, width=12
        ).pack(side=tk.RIGHT, padx=5, pady=5)

    def create_results_frame(self):
        """Create results display area"""
        results_frame = ttk.LabelFrame(self.app.root, text="  📖 Results  ", padding=15)
        results_frame.pack(pady=(0, 10), padx=20, fill=tk.BOTH, expand=True)

        # Text widget with scrollbar
        self.app.results_text = scrolledtext.ScrolledText(
            results_frame,
            wrap=tk.WORD,
            font=('Georgia', 11),
            padx=15,
            pady=15,
            bg='#ffffff',
            fg=AppStyles.TEXT_COLOR,
            relief=tk.FLAT,
            borderwidth=0,
            insertbackground=AppStyles.ACCENT_COLOR
        )
        self.app.results_text.pack(fill=tk.BOTH, expand=True)

        # Configure text tags
        AppStyles.configure_text_tags(self.app.results_text)

    def bind_events(self):
        """Bind keyboard and mouse events"""
        # Enter key bindings
        self.app.poem_name_entry.bind('<Return>',
                                     lambda e: self.app.search_handlers.search_poem())
        self.app.poet_name_entry.bind('<Return>',
                                     lambda e: self.app.search_handlers.search_poem())

        # Context menu bindings
        self.app.poem_name_entry.bind('<Button-3>',
                                     self.app.event_handlers.show_context_menu)
        self.app.poet_name_entry.bind('<Button-3>',
                                     self.app.event_handlers.show_context_menu)
        self.app.results_text.bind('<Button-3>',
                                  self.app.event_handlers.show_text_context_menu)

        # Clickable text bindings
        self.app.results_text.tag_bind('clickable_poet', '<Button-1>',
                                      self.app.event_handlers.on_poet_click)
        self.app.results_text.tag_bind('clickable_poem', '<Button-1>',
                                      self.app.event_handlers.on_poem_click)

        # Cursor hover effects
        self.app.results_text.tag_bind('clickable_poet', '<Enter>',
                                      lambda e: self.app.results_text.config(cursor='hand2'))
        self.app.results_text.tag_bind('clickable_poet', '<Leave>',
                                      lambda e: self.app.results_text.config(cursor=''))
        self.app.results_text.tag_bind('clickable_poem', '<Enter>',
                                      lambda e: self.app.results_text.config(cursor='hand2'))
        self.app.results_text.tag_bind('clickable_poem', '<Leave>',
                                      lambda e: self.app.results_text.config(cursor=''))

