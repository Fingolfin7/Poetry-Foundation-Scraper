"""
Event Handlers Module
Handles user interaction events like clicks, keyboard shortcuts, and context menus.
"""

import tkinter as tk
import re
from tkinter import messagebox, filedialog
from clean_encoding import clean


class EventHandlers:
    """Handles user interaction events"""

    def __init__(self, app):
        """
        Initialize with reference to main app
        Args:
            app: Main PoemAppGUI instance
        """
        self.app = app
        self.focused_widget = None

    def create_context_menu(self):
        """Create context menus for copy/paste/cut"""
        self.entry_context_menu = tk.Menu(self.app.root, tearoff=0)
        self.entry_context_menu.add_command(label="Cut", command=self.cut_text)
        self.entry_context_menu.add_command(label="Copy", command=self.copy_text)
        self.entry_context_menu.add_command(label="Paste", command=self.paste_text)
        self.entry_context_menu.add_separator()
        self.entry_context_menu.add_command(label="Select All", command=self.select_all)

        self.text_context_menu = tk.Menu(self.app.root, tearoff=0)
        self.text_context_menu.add_command(label="Copy", command=self.copy_text_widget)
        self.text_context_menu.add_separator()
        self.text_context_menu.add_command(label="Select All", command=self.select_all_text)

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
        """Copy selected text from text widget"""
        try:
            self.app.results_text.event_generate('<<Copy>>')
        except:
            pass

    def select_all_text(self):
        """Select all text in text widget"""
        try:
            self.app.results_text.tag_add(tk.SEL, "1.0", tk.END)
        except:
            pass

    def on_poet_click(self, event):
        """Handle click on a poet name"""
        # Get the index of the click
        index = self.app.results_text.index(f"@{event.x},{event.y}")

        # Find which clickable region was clicked
        for region, data in self.app.clickable_data.items():
            start, end = region.split(':')
            if self.app.results_text.compare(start, '<=', index) and \
               self.app.results_text.compare(index, '<', end):
                if data[0] == 'poet':
                    poet_name = data[1]
                    self.app.display_handlers.clear_results()
                    self.app.display_handlers.list_poems_by_poet(poet_name)
                    self.app.status_var.set(f"Showing poems by: {poet_name}")
                break

    def on_poem_click(self, event):
        """Handle click on a poem title"""
        # Get the index of the click
        index = self.app.results_text.index(f"@{event.x},{event.y}")

        # Find which clickable region was clicked
        for region, data in self.app.clickable_data.items():
            start, end = region.split(':')
            if self.app.results_text.compare(start, '<=', index) and \
               self.app.results_text.compare(index, '<', end):
                if data[0] == 'poem':
                    poet_name = data[1]
                    poem_title = data[2]

                    # Get the poem from the database (ORM-backed)
                    poem_row = self.app.poems.db.get_poem_by_poet_and_title(poet_name, poem_title)
                    if poem_row:
                        poem = clean(poem_row['content'], False)

                        self.app.display_handlers.clear_results()
                        self.app.display_handlers.display_poem(poem_title, poet_name, poem)
                        self.app.current_poem_data = (poem_title, poet_name, poem)
                        self.app.status_var.set(f"Displaying: '{poem_title}' by {poet_name}")
                break

    def save_poem(self):
        """Save the current poem to a file with user-chosen location"""
        if not self.app.current_poem_data:
            messagebox.showwarning("No Poem Selected",
                                  "Please search for and display a poem first before saving.")
            return

        title, poet, poem = self.app.current_poem_data

        # Create a safe filename
        safe_title = re.sub(r'[<>:"/\\|?*]', '', title)[:100]
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
            self.app.status_var.set(f"✓ Saved: '{title}' by {poet}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save poem:\n{str(e)}")
            self.app.status_var.set("✗ Error saving poem")

    def copy_to_clipboard(self):
        """Copy the current results to clipboard"""
        text = self.app.results_text.get(1.0, tk.END).strip()

        if not text:
            messagebox.showwarning("No Content", "No content to copy.")
            return

        self.app.root.clipboard_clear()
        self.app.root.clipboard_append(text)
        messagebox.showinfo("Success", "Content copied to clipboard!")
        self.app.status_var.set("Copied to clipboard ✓")

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
