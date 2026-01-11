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

        poem = self.app.poems.db.get_random_poem()

        if poem:
            self.clear_results()
            poem_text = clean(poem['content'], False)
            self.display_poem(poem['title'], poem['poet'], poem_text)
            self.app.current_poem_data = (poem['title'], poem['poet'], poem_text)
            self.app.status_var.set(f"Random poem: '{poem['title']}' by {poem['poet']}")
        else:
            tk.messagebox.showerror("Error", "No poems in database.")
            self.app.status_var.set("No poems available")

    def list_all_poets(self):
        """List all poets in the database"""
        self.clear_results()
        self.app.clickable_data = {}
        self.app.results_text.insert(tk.END, "📚 All Poets in Database:\n\n", 'title')
        self.app.results_text.insert(tk.END, "(Click on a poet's name to see their poems)\n\n", 'info')

        poets = self.app.poems.db.get_poets_with_counts()
        for index, (poet, poem_count) in enumerate(poets, 1):
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
        self.app.status_var.set(f"Listed {len(poets)} poets - click a name to view poems")

    def list_poems_by_poet(self, poet_name):
        """List all poems by a specific poet"""
        poems = self.app.poems.db.get_poems_by_poet(poet_name)
        found = False

        if poems:
            poet_key = poems[0]['poet']
            self.app.results_text.insert(tk.END, f"📖 Poems by {poet_key}:\n\n", 'title')
            self.app.results_text.insert(tk.END, "(Click on a poem title to read it)\n\n", 'info')

            for index, poem in enumerate(poems, 1):
                poem_title = poem['title']
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

        if not found:
            self.app.results_text.insert(tk.END,
                                        f"Couldn't find poet: {poet_name.capitalize()}\n",
                                        'error')

    def search_poems_with_term(self, search_term):
        """Search for poems containing a specific term in their title (DB-backed)"""
        results = self.app.poems.db.search_poem_titles(search_term=search_term, limit=500)
        found_any = False

        # Group by poet
        grouped = {}
        for row in results:
            grouped.setdefault(row['poet'], []).append(row['title'])

        for poet, titles in grouped.items():
            self.app.results_text.insert(tk.END, f"By {poet}:\n", 'info')
            for index, poem_title in enumerate(titles, 1):
                # Insert the number
                self.app.results_text.insert(tk.END, f"  {index}. ")

                # Insert poem title as clickable
                start_idx = self.app.results_text.index(tk.INSERT)
                self.app.results_text.insert(tk.END, poem_title, 'clickable_poem')
                end_idx = self.app.results_text.index(tk.INSERT)

                # Store poem data for this clickable region
                self.app.clickable_data[f"{start_idx}:{end_idx}"] = ('poem', poet, poem_title)

                self.app.results_text.insert(tk.END, "\n")
            self.app.results_text.insert(tk.END, "\n")
            found_any = True

        if not found_any:
            self.app.results_text.insert(tk.END,
                                        f"No poems found containing '{search_term}'\n",
                                        'error')

    def list_poems_by_poet_button(self):
        """List poems by poet from the poet name entry field"""
        poet_name = self.app.poet_name_entry.get().strip()

        if not poet_name:
            tk.messagebox.showwarning(
                "Input Required",
                "Please enter a poet name to list their poems."
            )
            return

        self.clear_results()
        self.list_poems_by_poet(poet_name)
        self.app.current_poem_data = None
        self.app.status_var.set(f"Listed poems by: {poet_name}")
