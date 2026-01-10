import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import random
import re
from Poems import Poems
from clean_encoding import clean
from save_to_file import save_to_file


class PoemAppGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Poetry Foundation Explorer")
        self.root.geometry("1000x750")
        self.root.minsize(800, 600)

        # Initialize Poems object
        self.poems = Poems()

        # Configure style
        self.setup_style()

        # Create main container
        self.create_widgets()

    def setup_style(self):
        """Configure the application style"""
        style = ttk.Style()
        style.theme_use('clam')

        # Modern color scheme
        bg_color = "#f5f6fa"
        dark_bg = "#2c3e50"
        accent_color = "#3498db"
        accent_hover = "#2980b9"
        success_color = "#27ae60"

        self.root.configure(bg=bg_color)

        # Title styling
        style.configure('Title.TLabel',
                       font=('Segoe UI', 20, 'bold'),
                       background=bg_color,
                       foreground=dark_bg,
                       padding=10)

        # Label styling
        style.configure('TLabel',
                       font=('Segoe UI', 10),
                       background=bg_color,
                       foreground=dark_bg)

        # Button styling with modern look
        style.configure('TButton',
                       font=('Segoe UI', 9, 'bold'),
                       padding=8,
                       relief='flat')

        style.map('TButton',
                 background=[('active', accent_hover), ('!active', accent_color)],
                 foreground=[('active', 'white'), ('!active', 'white')])

        # Action button styling (for Save, Copy)
        style.configure('Action.TButton',
                       font=('Segoe UI', 9, 'bold'),
                       padding=8,
                       relief='flat')

        style.map('Action.TButton',
                 background=[('active', '#229954'), ('!active', success_color)],
                 foreground=[('active', 'white'), ('!active', 'white')])

        # Entry styling
        style.configure('TEntry',
                       font=('Segoe UI', 10),
                       fieldbackground='white',
                       borderwidth=2)

        # LabelFrame styling
        style.configure('TLabelframe',
                       background=bg_color,
                       borderwidth=2,
                       relief='solid')

        style.configure('TLabelframe.Label',
                       font=('Segoe UI', 10, 'bold'),
                       background=bg_color,
                       foreground=dark_bg)

    def create_widgets(self):
        """Create all GUI widgets"""
        # Header with gradient-like effect
        header_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        header_frame.pack_propagate(False)

        title_label = tk.Label(header_frame,
                              text="🎭 Poetry Foundation Explorer",
                              font=('Segoe UI', 24, 'bold'),
                              bg='#2c3e50',
                              fg='white')
        title_label.pack(expand=True)

        subtitle_label = tk.Label(header_frame,
                                 text="Discover, Explore, and Save Beautiful Poetry",
                                 font=('Segoe UI', 10, 'italic'),
                                 bg='#2c3e50',
                                 fg='#ecf0f1')
        subtitle_label.pack()

        # Search Frame with enhanced styling
        search_frame = ttk.LabelFrame(self.root, text="  🔍 Search Poems  ", padding=15)
        search_frame.pack(pady=(0, 15), padx=20, fill=tk.X)

        # Poem Name
        ttk.Label(search_frame, text="Poem Title:").grid(row=0, column=0, sticky=tk.W, pady=8, padx=(5, 10))
        self.poem_name_entry = ttk.Entry(search_frame, width=40, font=('Segoe UI', 11))
        self.poem_name_entry.grid(row=0, column=1, pady=8, padx=5, sticky=tk.EW)

        # Poet Name
        ttk.Label(search_frame, text="Poet Name:").grid(row=1, column=0, sticky=tk.W, pady=8, padx=(5, 10))
        self.poet_name_entry = ttk.Entry(search_frame, width=40, font=('Segoe UI', 11))
        self.poet_name_entry.grid(row=1, column=1, pady=8, padx=5, sticky=tk.EW)

        search_frame.columnconfigure(1, weight=1)

        # Buttons Frame with better layout
        button_frame = ttk.Frame(search_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(15, 5))

        ttk.Button(button_frame, text="🔍 Search",
                  command=self.search_poem, width=12).pack(side=tk.LEFT, padx=4)
        ttk.Button(button_frame, text="📋 By Poet",
                  command=self.list_poems_by_poet_button, width=12).pack(side=tk.LEFT, padx=4)
        ttk.Button(button_frame, text="🎲 Random",
                  command=self.random_poem, width=12).pack(side=tk.LEFT, padx=4)
        ttk.Button(button_frame, text="📜 All Poets",
                  command=self.list_all_poets, width=12).pack(side=tk.LEFT, padx=4)
        ttk.Button(button_frame, text="🗑️ Clear",
                  command=self.clear_results, width=10).pack(side=tk.LEFT, padx=4)

        # Status Bar with modern design (pack FIRST to bottom)
        status_frame = tk.Frame(self.root, bg='#34495e', height=30)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        status_frame.pack_propagate(False)

        self.status_var = tk.StringVar()
        self.status_var.set("Ready to explore poetry ✨")
        status_bar = tk.Label(status_frame,
                             textvariable=self.status_var,
                             bg='#34495e',
                             fg='#ecf0f1',
                             font=('Segoe UI', 9),
                             anchor=tk.W,
                             padx=10)
        status_bar.pack(fill=tk.BOTH, expand=True)

        # Action Buttons Frame with enhanced styling (pack SECOND to bottom, above status bar)
        action_frame = ttk.Frame(self.root)
        action_frame.pack(side=tk.BOTTOM, pady=10, padx=20, fill=tk.X)

        ttk.Button(action_frame, text="💾 Save to File",
                  command=self.save_poem, style='Action.TButton', width=18).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(action_frame, text="📋 Copy to Clipboard",
                  command=self.copy_to_clipboard, style='Action.TButton', width=20).pack(side=tk.LEFT, padx=5, pady=5)

        # Add a help button
        ttk.Button(action_frame, text="❓ Help",
                  command=self.show_help, width=12).pack(side=tk.RIGHT, padx=5, pady=5)

        # Results Frame with enhanced styling (pack AFTER bottom elements so it fills remaining space)
        results_frame = ttk.LabelFrame(self.root, text="  📖 Results  ", padding=15)
        results_frame.pack(pady=(0, 10), padx=20, fill=tk.BOTH, expand=True)

        # Text widget with scrollbar and better styling
        self.results_text = scrolledtext.ScrolledText(
            results_frame,
            wrap=tk.WORD,
            font=('Georgia', 11),
            padx=15,
            pady=15,
            bg='#ffffff',
            fg='#2c3e50',
            relief=tk.FLAT,
            borderwidth=0,
            insertbackground='#3498db'
        )
        self.results_text.pack(fill=tk.BOTH, expand=True)

        # Configure text tags for formatting with enhanced styling
        self.results_text.tag_configure('title',
                                       font=('Georgia', 16, 'bold'),
                                       foreground='#2c3e50',
                                       spacing1=10,
                                       spacing3=5)
        self.results_text.tag_configure('poet',
                                       font=('Georgia', 13, 'italic'),
                                       foreground='#7f8c8d',
                                       spacing3=10)
        self.results_text.tag_configure('poem',
                                       font=('Georgia', 12),
                                       foreground='#34495e',
                                       spacing1=5,
                                       lmargin1=20,
                                       lmargin2=20)
        self.results_text.tag_configure('info',
                                       font=('Segoe UI', 10, 'italic'),
                                       foreground='#3498db',
                                       spacing3=5)
        self.results_text.tag_configure('error',
                                       font=('Segoe UI', 10, 'bold'),
                                       foreground='#e74c3c')
        self.results_text.tag_configure('list_item',
                                       font=('Segoe UI', 10),
                                       foreground='#2c3e50',
                                       spacing1=3)

        # Configure clickable tags with hover effect
        self.results_text.tag_configure('clickable_poet',
                                       font=('Segoe UI', 10, 'bold'),
                                       foreground='#27ae60',
                                       underline=1)
        self.results_text.tag_configure('clickable_poem',
                                       font=('Segoe UI', 10),
                                       foreground='#3498db',
                                       underline=1)
        self.results_text.tag_bind('clickable_poet', '<Button-1>', self.on_poet_click)
        self.results_text.tag_bind('clickable_poem', '<Button-1>', self.on_poem_click)
        self.results_text.tag_bind('clickable_poet', '<Enter>', lambda e: self.results_text.config(cursor='hand2'))
        self.results_text.tag_bind('clickable_poet', '<Leave>', lambda e: self.results_text.config(cursor=''))
        self.results_text.tag_bind('clickable_poem', '<Enter>', lambda e: self.results_text.config(cursor='hand2'))
        self.results_text.tag_bind('clickable_poem', '<Leave>', lambda e: self.results_text.config(cursor=''))


        # Bind Enter key to search
        self.poem_name_entry.bind('<Return>', lambda e: self.search_poem())
        self.poet_name_entry.bind('<Return>', lambda e: self.search_poem())

        # Add context menu for copy/paste/cut
        self.create_context_menu()

        # Bind context menu to entry fields and text widget
        self.poem_name_entry.bind('<Button-3>', self.show_context_menu)
        self.poet_name_entry.bind('<Button-3>', self.show_context_menu)
        self.results_text.bind('<Button-3>', self.show_text_context_menu)

        # Store current poem data and clickable data
        self.current_poem_data = None
        self.clickable_data = {}

    def create_context_menu(self):
        """Create context menus for copy/paste/cut"""
        self.entry_context_menu = tk.Menu(self.root, tearoff=0)
        self.entry_context_menu.add_command(label="Cut", command=self.cut_text)
        self.entry_context_menu.add_command(label="Copy", command=self.copy_text)
        self.entry_context_menu.add_command(label="Paste", command=self.paste_text)
        self.entry_context_menu.add_separator()
        self.entry_context_menu.add_command(label="Select All", command=self.select_all)

        self.text_context_menu = tk.Menu(self.root, tearoff=0)
        self.text_context_menu.add_command(label="Copy", command=self.copy_text_widget)
        self.text_context_menu.add_separator()
        self.text_context_menu.add_command(label="Select All", command=self.select_all_text)

        self.focused_widget = None

    def show_context_menu(self, event):
        """Show context menu for entry widgets"""
        self.focused_widget = event.widget
        try:
            self.entry_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.entry_context_menu.grab_release()

    def show_text_context_menu(self, event):
        """Show context menu for text widget"""
        try:
            self.text_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.text_context_menu.grab_release()

    def cut_text(self):
        """Cut text from entry widget"""
        if self.focused_widget:
            try:
                self.focused_widget.event_generate('<<Cut>>')
            except:
                pass

    def copy_text(self):
        """Copy text from entry widget"""
        if self.focused_widget:
            try:
                self.focused_widget.event_generate('<<Copy>>')
            except:
                pass

    def paste_text(self):
        """Paste text to entry widget"""
        if self.focused_widget:
            try:
                self.focused_widget.event_generate('<<Paste>>')
            except:
                pass

    def select_all(self):
        """Select all text in entry widget"""
        if self.focused_widget:
            try:
                self.focused_widget.select_range(0, tk.END)
            except:
                pass

    def copy_text_widget(self):
        """Copy selected text from results text widget"""
        try:
            selected_text = self.results_text.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.root.clipboard_clear()
            self.root.clipboard_append(selected_text)
        except:
            pass

    def select_all_text(self):
        """Select all text in results widget"""
        self.results_text.tag_add(tk.SEL, "1.0", tk.END)
        self.results_text.mark_set(tk.INSERT, "1.0")
        self.results_text.see(tk.INSERT)

    def search_poem(self):
        """Search for a poem"""
        poem_name = self.poem_name_entry.get().strip()
        poet_name = self.poet_name_entry.get().strip()

        if not poem_name and not poet_name:
            messagebox.showwarning("Input Required",
                                  "Please enter a poem name or poet name.")
            return

        self.status_var.set("Searching locally...")
        self.root.update()

        # Clean the input
        search_name = clean(poem_name) if poem_name else ""
        search_poet = clean(poet_name) if poet_name else ""

        # First check local database
        poems_dict = self.poems.get_dict()
        title, poet, poem = self._search_local(search_name, search_poet, poems_dict)

        if poem:
            # Found locally
            self.clear_results()
            poem = clean(poem, False)
            self.display_poem(title, poet, poem)
            self.current_poem_data = (title, poet, poem)
            self.status_var.set(f"Found: '{title}' by {poet}")
        else:
            # Not found locally, try online search in background thread
            self.clear_results()
            self.results_text.insert(tk.END, "Searching locally... Not found.\n", 'info')
            self.results_text.insert(tk.END, "🌐 Searching online (Poetry Foundation)...\n\n", 'info')
            self.status_var.set("🌐 Searching online - please wait...")
            self.root.update()

            # Run online search in separate thread
            search_thread = threading.Thread(
                target=self._search_online_thread,
                args=(search_name, search_poet),
                daemon=True
            )
            search_thread.start()

    def _search_local(self, title, poet, poems_dict):
        """Search for a poem in local database"""
        for key in poems_dict:
            if poet.lower() in key.lower():
                for poem_title in poems_dict[key]:
                    if title.lower() in poem_title.lower():
                        return poem_title, key, poems_dict[key][poem_title]
        return None, None, None

    def _search_online_thread(self, search_name, search_poet):
        """Search online in a background thread"""
        try:
            title, poet, poem = self.poems.search(search_name, search_poet)

            # Schedule UI update on main thread
            self.root.after(0, self._handle_online_search_result, title, poet, poem, search_name, search_poet)
        except Exception as e:
            self.root.after(0, self._handle_search_error, str(e))

    def _handle_online_search_result(self, title, poet, poem, search_name, search_poet):
        """Handle the result of online search (runs on main thread)"""
        self.clear_results()

        if poem:
            # Found online
            poem = clean(poem, False)
            self.results_text.insert(tk.END, "✓ Found online!\n\n", 'info')
            self.display_poem(title, poet, poem)
            self.current_poem_data = (title, poet, poem)
            self.status_var.set(f"Found online: '{title}' by {poet}")
        else:
            # Not found anywhere
            self.results_text.insert(tk.END, "Poem not found online either.\n\n", 'error')

            if search_poet:
                self.results_text.insert(tk.END, f"Poems by {search_poet}:\n\n", 'info')
                self.list_poems_by_poet(search_poet)

            if search_name:
                self.results_text.insert(tk.END, f"\nPoems containing '{search_name}':\n\n", 'info')
                self.search_poems_with_term(search_name)

            self.current_poem_data = None
            self.status_var.set("Poem not found - showing alternatives")

    def _handle_search_error(self, error_msg):
        """Handle search error (runs on main thread)"""
        self.results_text.insert(tk.END, f"Error during search: {error_msg}\n", 'error')
        self.status_var.set("Search error occurred")

    def display_poem(self, title, poet, poem):
        """Display a poem in the results text widget"""
        self.results_text.insert(tk.END, f"{title}\n", 'title')
        self.results_text.insert(tk.END, f"by {poet}\n\n", 'poet')
        self.results_text.insert(tk.END, "─" * 50 + "\n\n", 'info')
        self.results_text.insert(tk.END, f"{poem}\n", 'poem')

    def random_poem(self):
        """Display a random poem"""
        self.status_var.set("Getting random poem...")
        self.root.update()

        poems_dict = self.poems.get_dict()

        # Check if we have any poems
        if not poems_dict:
            messagebox.showerror("Error", "No poems in database.")
            self.status_var.set("No poems available")
            return

        # Get a random poet
        random_poet = random.choice(list(poems_dict.keys()))

        # Get a random poem from that poet
        random_title = random.choice(list(poems_dict[random_poet].keys()))
        poem = poems_dict[random_poet][random_title]

        if poem:
            self.clear_results()
            poem = clean(poem, False)
            self.display_poem(random_title, random_poet, poem)
            self.current_poem_data = (random_title, random_poet, poem)
            self.status_var.set(f"Random poem: '{random_title}' by {random_poet}")
        else:
            messagebox.showerror("Error", "Could not retrieve a random poem.")
            self.status_var.set("Error getting random poem")

    def list_all_poets(self):
        """List all poets in the database"""
        self.clear_results()
        self.clickable_data = {}
        self.results_text.insert(tk.END, "📚 All Poets in Database:\n\n", 'title')
        self.results_text.insert(tk.END, "(Click on a poet's name to see their poems)\n\n", 'info')

        poems_dict = self.poems.get_dict()
        for index, poet in enumerate(sorted(poems_dict.keys()), 1):
            poem_count = len(poems_dict[poet])

            # Insert the number and opening parenthesis
            self.results_text.insert(tk.END, f"{index}. ")

            # Insert poet name as clickable
            start_idx = self.results_text.index(tk.INSERT)
            self.results_text.insert(tk.END, poet, 'clickable_poet')
            end_idx = self.results_text.index(tk.INSERT)

            # Store poet data for this clickable region
            self.clickable_data[f"{start_idx}:{end_idx}"] = ('poet', poet)

            # Insert the rest
            self.results_text.insert(tk.END, f" ({poem_count} poem{'s' if poem_count != 1 else ''})\n")

        self.current_poem_data = None
        self.status_var.set(f"Listed {len(poems_dict)} poets - click a name to view poems")

    def list_poems_by_poet_button(self):
        """List poems by poet from the poet name entry field"""
        poet_name = self.poet_name_entry.get().strip()

        if not poet_name:
            messagebox.showwarning("Input Required",
                                  "Please enter a poet name to list their poems.")
            return

        self.clear_results()
        self.list_poems_by_poet(poet_name)
        self.current_poem_data = None
        self.status_var.set(f"Listed poems by: {poet_name}")

    def list_poems_by_poet(self, poet_name):
        """List all poems by a specific poet"""
        poems_dict = self.poems.get_dict()
        found = False

        for poet_key in poems_dict:
            if poet_name.lower() in poet_key.lower():
                self.results_text.insert(tk.END, f"📖 Poems by {poet_key}:\n\n", 'title')
                self.results_text.insert(tk.END, "(Click on a poem title to read it)\n\n", 'info')

                for index, poem_title in enumerate(poems_dict[poet_key], 1):
                    # Insert the number
                    self.results_text.insert(tk.END, f"  {index}. ")

                    # Insert poem title as clickable
                    start_idx = self.results_text.index(tk.INSERT)
                    self.results_text.insert(tk.END, poem_title, 'clickable_poem')
                    end_idx = self.results_text.index(tk.INSERT)

                    # Store poem data for this clickable region
                    self.clickable_data[f"{start_idx}:{end_idx}"] = ('poem', poet_key, poem_title)

                    self.results_text.insert(tk.END, "\n")

                self.results_text.insert(tk.END, "\n")
                found = True
                break

        if not found:
            self.results_text.insert(tk.END,
                                    f"Couldn't find poet: {poet_name.capitalize()}\n",
                                    'error')

    def search_poems_with_term(self, search_term):
        """Search for poems containing a specific term"""
        poems_dict = self.poems.get_dict()
        found_any = False

        for poet, poems in poems_dict.items():
            matching_poems = [p for p in poems if search_term.lower() in p.lower()]

            if matching_poems:
                self.results_text.insert(tk.END, f"By {poet}:\n", 'info')
                for index, poem in enumerate(matching_poems, 1):
                    # Insert the number
                    self.results_text.insert(tk.END, f"  {index}. ")

                    # Insert poem title as clickable
                    start_idx = self.results_text.index(tk.INSERT)
                    self.results_text.insert(tk.END, poem, 'clickable_poem')
                    end_idx = self.results_text.index(tk.INSERT)

                    # Store poem data for this clickable region
                    self.clickable_data[f"{start_idx}:{end_idx}"] = ('poem', poet, poem)

                    self.results_text.insert(tk.END, "\n")
                self.results_text.insert(tk.END, "\n")
                found_any = True

        if not found_any:
            self.results_text.insert(tk.END,
                                    f"No poems found containing '{search_term}'\n",
                                    'error')

    def on_poet_click(self, event):
        """Handle click on a poet name"""
        # Get the index of the click
        index = self.results_text.index(f"@{event.x},{event.y}")

        # Find which clickable region was clicked
        for region, data in self.clickable_data.items():
            start, end = region.split(':')
            if self.results_text.compare(start, '<=', index) and self.results_text.compare(index, '<', end):
                if data[0] == 'poet':
                    poet_name = data[1]
                    self.clear_results()
                    self.list_poems_by_poet(poet_name)
                    self.status_var.set(f"Showing poems by: {poet_name}")
                break

    def on_poem_click(self, event):
        """Handle click on a poem title"""
        # Get the index of the click
        index = self.results_text.index(f"@{event.x},{event.y}")

        # Find which clickable region was clicked
        for region, data in self.clickable_data.items():
            start, end = region.split(':')
            if self.results_text.compare(start, '<=', index) and self.results_text.compare(index, '<', end):
                if data[0] == 'poem':
                    poet_name = data[1]
                    poem_title = data[2]

                    # Get the poem from the database
                    poems_dict = self.poems.get_dict()
                    if poet_name in poems_dict and poem_title in poems_dict[poet_name]:
                        poem = poems_dict[poet_name][poem_title]
                        poem = clean(poem, False)

                        self.clear_results()
                        self.display_poem(poem_title, poet_name, poem)
                        self.current_poem_data = (poem_title, poet_name, poem)
                        self.status_var.set(f"Displaying: '{poem_title}' by {poet_name}")
                break

    def clear_results(self):
        """Clear the results text widget"""
        self.results_text.delete(1.0, tk.END)
        self.clickable_data = {}

    def save_poem(self):
        """Save the current poem to a file with user-chosen location"""
        if not self.current_poem_data:
            messagebox.showwarning("No Poem Selected",
                                  "Please search for and display a poem first before saving.")
            return

        title, poet, poem = self.current_poem_data

        # Create a safe filename
        safe_title = re.sub(r'[<>:"/\\|?*]', '', title)[:100]  # Remove invalid chars and limit length
        safe_poet = re.sub(r'[<>:"/\\|?*]', '', poet)[:50]
        default_filename = f"{safe_title} by {safe_poet}.txt"

        # Ask user where to save
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[
                ("Text Files", "*.txt"),
                ("Markdown Files", "*.md"),
                ("All Files", "*.*")
            ],
            initialfile=default_filename,
            title="Save Poem As"
        )

        if not file_path:  # User cancelled
            return

        try:
            # Create the content
            content = f"{title}\nby {poet}\n\n{'─' * 50}\n\n{poem}\n"

            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            messagebox.showinfo("Success! 💾",
                               f"Poem saved successfully!\n\nLocation: {file_path}")
            self.status_var.set(f"✓ Saved: '{title}' by {poet}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save poem:\n{str(e)}")
            self.status_var.set("✗ Error saving poem")

    def copy_to_clipboard(self):
        """Copy the current results to clipboard"""
        text = self.results_text.get(1.0, tk.END).strip()

        if not text:
            messagebox.showwarning("No Content", "No content to copy.")
            return

        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        messagebox.showinfo("Success", "Content copied to clipboard!")
        self.status_var.set("Copied to clipboard ✓")

    def show_help(self):
        """Show help dialog with feature explanations"""
        help_text = """🎭 Poetry Foundation Explorer - Quick Guide

🔍 SEARCH:
• Enter poem title and/or poet name
• Press Enter or click Search button
• Searches locally first, then online if needed

🖱️ CLICKABLE LINKS:
• Green underlined text = clickable
• Click poet names to see their poems
• Click poem titles to read them

✂️ COPY/PASTE:
• Right-click on entry fields for context menu
• Right-click on results to copy text
• Use Ctrl+C, Ctrl+V shortcuts

📋 FEATURES:
• By Poet: List all poems by a specific poet
• Random: Get a random poem
• All Poets: Browse all poets in database
• Save: Save current poem to a text file

💡 TIP: When searching online, the UI stays 
responsive - you can still click around!
"""
        messagebox.showinfo("Help - How to Use", help_text)


def main():
    root = tk.Tk()
    app = PoemAppGUI(root)
    root.mainloop()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

