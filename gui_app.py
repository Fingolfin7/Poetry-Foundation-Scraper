"""
Poetry Foundation Explorer - GUI Application
Entry point for the graphical user interface.
"""

import tkinter as tk
from tkinter import messagebox
from gui import PoemAppGUI


def main():
    """Main entry point for the GUI application"""
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

