"""
Display Handlers Module
Handles displaying poems, lists, and managing the results widget.
"""

import tkinter as tk
import random
from clean_encoding import clean


class DisplayHandlers:
    """Handles display operations for poems and lists"""

    def __init__(self, app):
        """
        Initialize with reference to main app
        Args:
            app: Main PoemAppGUI instance
        """
        self.app = app

    def display_poem(self, title, poet, poem):
        """Display a poem in the results text widget"""
        self.app.results_text.insert(tk.END, f"{title}\n", 'title')
        self.app.results_text.insert(tk.END, f"by {poet}\n\n", 'poet')
        self.app.results_text.insert(tk.END, "─" * 50 + "\n\n", 'info')
        self.app.results_text.insert(tk.END, f"{poem}\n", 'poem')

    def clear_results(self):
        """Clear the results text widget"""
        self.app.results_text.delete(1.0, tk.END)
        self.app.clickable_data = {}

    def random_poem(self):
        """Display a random poem"""
        self.app.status_var.set("Getting random poem...")
        self.app.root.update()

        poems_dict = self.app.poems.get_dict()

        # Check if we have any poems
        if not poems_dict:
            tk.messagebox.showerror("Error", "No poems in database.")
            self.app.status_var.set("No poems available")
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
            self.app.current_poem_data = (random_title, random_poet, poem)
            self.app.status_var.set(f"Random poem: '{random_title}' by {random_poet}")
        else:
            tk.messagebox.showerror("Error", "Could not retrieve a random poem.")
            self.app.status_var.set("Error getting random poem")

    def list_all_poets(self):
        """List all poets in the database"""
        self.clear_results()
        self.app.clickable_data = {}
        self.app.results_text.insert(tk.END, "📚 All Poets in Database:\n\n", 'title')
        self.app.results_text.insert(tk.END, "(Click on a poet's name to see their poems)\n\n", 'info')

        poems_dict = self.app.poems.get_dict()
        for index, poet in enumerate(sorted(poems_dict.keys()), 1):
            poem_count = len(poems_dict[poet])

            # Insert the number
            self.app.results_text.insert(tk.END, f"{index}. ")

            # Insert poet name as clickable
            start_idx = self.app.results_text.index(tk.INSERT)
            self.app.results_text.insert(tk.END, poet, 'clickable_poet')
            end_idx = self.app.results_text.index(tk.INSERT)

            # Store poet data for this clickable region
            self.app.clickable_data[f"{start_idx}:{end_idx}"] = ('poet', poet)

            # Insert the rest
            self.app.results_text.insert(tk.END, f" ({poem_count} poem{'s' if poem_count != 1 else ''})\n")

        self.app.current_poem_data = None
        self.app.status_var.set(f"Listed {len(poems_dict)} poets - click a name to view poems")

    def list_poems_by_poet_button(self):
        """List poems by poet from the poet name entry field"""
        poet_name = self.app.poet_name_entry.get().strip()

        if not poet_name:
            tk.messagebox.showwarning("Input Required",
                                     "Please enter a poet name to list their poems.")
            return

        self.clear_results()
        self.list_poems_by_poet(poet_name)
        self.app.current_poem_data = None
        self.app.status_var.set(f"Listed poems by: {poet_name}")

    def list_poems_by_poet(self, poet_name):
        """List all poems by a specific poet"""
        poems_dict = self.app.poems.get_dict()
        found = False

        for poet_key in poems_dict:
            if poet_name.lower() in poet_key.lower():
                self.app.results_text.insert(tk.END, f"📖 Poems by {poet_key}:\n\n", 'title')
                self.app.results_text.insert(tk.END, "(Click on a poem title to read it)\n\n", 'info')

                for index, poem_title in enumerate(poems_dict[poet_key], 1):
                    # Insert the number
                    self.app.results_text.insert(tk.END, f"  {index}. ")

                    # Insert poem title as clickable
                    start_idx = self.app.results_text.index(tk.INSERT)
                    self.app.results_text.insert(tk.END, poem_title, 'clickable_poem')
                    end_idx = self.app.results_text.index(tk.INSERT)

                    # Store poem data for this clickable region
                    self.app.clickable_data[f"{start_idx}:{end_idx}"] = ('poem', poet_key, poem_title)

                    self.app.results_text.insert(tk.END, "\n")

                self.app.results_text.insert(tk.END, "\n")
                found = True
                break

        if not found:
            self.app.results_text.insert(tk.END,
                                        f"Couldn't find poet: {poet_name.capitalize()}\n",
                                        'error')

    def search_poems_with_term(self, search_term):
        """Search for poems containing a specific term"""
        poems_dict = self.app.poems.get_dict()
        found_any = False

        for poet, poems in poems_dict.items():
            matching_poems = [p for p in poems if search_term.lower() in p.lower()]

            if matching_poems:
                self.app.results_text.insert(tk.END, f"By {poet}:\n", 'info')
                for index, poem in enumerate(matching_poems, 1):
                    # Insert the number
                    self.app.results_text.insert(tk.END, f"  {index}. ")

                    # Insert poem title as clickable
                    start_idx = self.app.results_text.index(tk.INSERT)
                    self.app.results_text.insert(tk.END, poem, 'clickable_poem')
                    end_idx = self.app.results_text.index(tk.INSERT)

                    # Store poem data for this clickable region
                    self.app.clickable_data[f"{start_idx}:{end_idx}"] = ('poem', poet, poem)

                    self.app.results_text.insert(tk.END, "\n")
                self.app.results_text.insert(tk.END, "\n")
                found_any = True

        if not found_any:
            self.app.results_text.insert(tk.END,
                                        f"No poems found containing '{search_term}'\n",
                                        'error')

