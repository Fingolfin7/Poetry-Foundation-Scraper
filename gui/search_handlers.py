"""
Search Handlers Module
Handles all search-related functionality for poems.
"""

import tkinter as tk
from tkinter import messagebox
import threading
from clean_encoding import clean


class SearchHandlers:
    """Handles poem search operations (local and online)"""

    def __init__(self, app):
        """
        Initialize with reference to main app
        Args:
            app: Main PoemAppGUI instance
        """
        self.app = app

    def search_poem(self):
        """Search for a poem"""
        poem_name = self.app.poem_name_entry.get().strip()
        poet_name = self.app.poet_name_entry.get().strip()

        if not poem_name and not poet_name:
            messagebox.showwarning("Input Required",
                                     "Please enter a poem name or poet name.")
            return

        self.app.status_var.set("Searching locally...")
        self.app.root.update()

        # Clean the input
        search_name = clean(poem_name) if poem_name else ""
        search_poet = clean(poet_name) if poet_name else ""

        # DB-backed local search (single query)
        title, poet, poem = self._search_local(search_name, search_poet)

        if poem:
            # Found locally
            self.app.display_handlers.clear_results()
            poem = clean(poem, False)
            self.app.display_handlers.display_poem(title, poet, poem)
            self.app.current_poem_data = (title, poet, poem)
            self.app.status_var.set(f"Found: '{title}' by {poet}")
        else:
            # Not found locally, try online search in background thread
            self.app.display_handlers.clear_results()
            self.app.results_text.insert(tk.END, "Searching locally... Not found.\n", 'info')
            self.app.results_text.insert(tk.END, "🌐 Searching online (Poetry Foundation)...\n\n", 'info')
            self.app.status_var.set("🌐 Searching online - please wait...")
            self.app.root.update()

            # Run online search in separate thread
            search_thread = threading.Thread(
                target=self._search_online_thread,
                args=(search_name, search_poet),
                daemon=True
            )
            search_thread.start()

    def _search_local(self, title, poet):
        """Search for a poem in local database (ORM-backed)."""
        result = self.app.poems.db.search_poems(title=title, poet_name=poet)
        if not result:
            return None, None, None
        return result['title'], result['poet'], result['content']

    def _search_online_thread(self, search_name, search_poet):
        """Search online in a background thread"""
        try:
            title, poet, poem = self.app.poems.search(search_name, search_poet)
            # Schedule UI update on main thread
            self.app.root.after(0, self._handle_online_search_result,
                              title, poet, poem, search_name, search_poet)
        except Exception as e:
            self.app.root.after(0, self._handle_search_error, str(e))

    def _handle_online_search_result(self, title, poet, poem, search_name, search_poet):
        """Handle the result of online search (runs on main thread)"""
        self.app.display_handlers.clear_results()

        if poem:
            # Found online
            poem = clean(poem, False)
            self.app.results_text.insert(tk.END, "✓ Found online!\n\n", 'info')
            self.app.display_handlers.display_poem(title, poet, poem)
            self.app.current_poem_data = (title, poet, poem)
            self.app.status_var.set(f"Found online: '{title}' by {poet}")
        else:
            # Not found anywhere
            self.app.results_text.insert(tk.END, "Poem not found online either.\n\n", 'error')

            if search_poet:
                self.app.results_text.insert(tk.END, f"Poems by {search_poet}:\n\n", 'info')
                self.app.display_handlers.list_poems_by_poet(search_poet)

            if search_name:
                self.app.results_text.insert(tk.END, f"\nPoems containing '{search_name}':\n\n", 'info')
                self.app.display_handlers.search_poems_with_term(search_name)

            self.app.current_poem_data = None
            self.app.status_var.set("Poem not found - showing alternatives")

    def _handle_search_error(self, error_msg):
        """Handle search error (runs on main thread)"""
        self.app.results_text.insert(tk.END, f"Error during search: {error_msg}\n", 'error')
        self.app.status_var.set("Search error occurred")

    def fulltext_search(self):
        """
        NEW: Full-text search in poem content using FTS5
        Searches inside the actual text of poems
        """
        query = self.app.fulltext_entry.get().strip()

        if not query:
            messagebox.showwarning("Input Required",
                                     "Please enter a search query.")
            return

        self.app.status_var.set("Searching poem content...")
        self.app.display_handlers.clear_results()
        self.app.root.update()

        # Run search in background thread
        search_thread = threading.Thread(
            target=self._fulltext_search_thread,
            args=(query,),
            daemon=True
        )
        search_thread.start()

    def _fulltext_search_thread(self, query):
        """Run full-text search in background thread"""
        try:
            results = self.app.poems.search_full_text(query, limit=50)
            self.app.root.after(0, self._handle_fulltext_results, query, results)
        except Exception as e:
            self.app.root.after(0, self._handle_search_error, str(e))

    def _handle_fulltext_results(self, query, results):
        """Display full-text search results on main thread"""
        self.app.display_handlers.clear_results()

        if results:
            self.app.results_text.insert(
                tk.END,
                f"🔍 Full-Text Search Results for: '{query}'\n",
                'title'
            )
            self.app.results_text.insert(
                tk.END,
                f"Found {len(results)} poems matching your search\n\n",
                'info'
            )

            for i, (poem_id, title, poet_name, content, rank) in enumerate(results, 1):
                # Make title clickable
                self.app.results_text.insert(tk.END, f"{i}. ", 'info')
                self.app.results_text.insert(tk.END, f"'{title}'", 'poem_link')
                self.app.results_text.insert(tk.END, f" by ", 'info')
                self.app.results_text.insert(tk.END, f"{poet_name}", 'poet_link')
                self.app.results_text.insert(tk.END, f"\n", 'info')

                # Show snippet of matching content (first 150 chars)
                snippet = content[:150].replace('\n', ' ') + "..." if len(content) > 150 else content
                self.app.results_text.insert(tk.END, f"   {snippet}\n\n", 'poem_text')

            self.app.status_var.set(f"Found {len(results)} poems matching '{query}'")
        else:
            self.app.results_text.insert(
                tk.END,
                f"No poems found matching: '{query}'\n\n",
                'error'
            )
            self.app.results_text.insert(
                tk.END,
                "💡 Try different keywords or use AND/OR operators\n",
                'info'
            )
            self.app.results_text.insert(
                tk.END,
                "   Examples: 'love AND heart', '\"exact phrase\"', 'NEAR(death life, 5)'\n",
                'info'
            )
            self.app.status_var.set("No results found")
