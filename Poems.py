"""
Poems facade backed by a SQLite database via SQLAlchemy ORM.

All searches and listings are database-backed (no JSON export/filtering).
"""
import os
import random
import logging
from scraper import PoetryScraper
from ColourText import format_text
from check_internet import check_internet
from models import DatabaseManager
from app_paths import get_runtime_dir


class Poems:
    def __init__(self, db_path="poems.db", log_level=logging.DEBUG):
        """
        Initialize Poems class with ORM database

        Args:
            db_path: Path to SQLite database file (default: poems.db)
            log_level: Logging level for scraper
        """
        # Store DB next to the running entry point (exe folder in frozen mode).
        runtime_dir = get_runtime_dir()
        self.db_path = os.path.join(runtime_dir, db_path)

        # Initialize database manager (ORM)
        self.db = DatabaseManager(self.db_path)

        # Initialize scraper for online searches
        self.scraper = PoetryScraper(log_level=log_level)

    # get_dict() removed: application is DB/ORM-only.

    def add_poem(self, title, poet, poem):
        """
        Add a poem to the database

        Args:
            title: Poem title
            poet: Poet name
            poem: Poem content
        """
        self.db.add_poem(title, poet, poem)

    def save(self):
        """
        Save operation (no-op with ORM as changes are auto-committed)
        Kept for backward compatibility
        """
        # With ORM, saves happen automatically in transactions
        # This method is kept for backward compatibility but does nothing
        pass

    def random_poem(self):
        """
        Get a random poem

        Returns:
            tuple: (title, poet, content) or (None, None, None)
        """
        poem = self.db.get_random_poem()
        if poem:
            return poem['title'], poem['poet'], poem['content']

        # If no poems in database, search for a random one online
        poets = self.db.get_all_poets()
        if poets:
            random_poet = random.choice(poets)[0]
            return self.__search_db("", random_poet)

        return None, None, None

    def __search_db(self, title, poet=""):
        """Private helper to search the local SQLite database (ORM-backed)."""
        poem = self.db.search_poems(title=title, poet_name=poet)
        if poem:
            print(
                format_text(f"Found: [bright yellow][italic]'{poem['title']}' by "
                            f"'{poem['poet']}'[reset]")
            )
            return poem['title'], poem['poet'], poem['content']
        return None, None, None

    def list_all_by_poet(self, poet):
        """
        List all poems by a specific poet

        Args:
            poet: Poet name (case-insensitive partial match)
        """
        poems = self.db.get_poems_by_poet(poet)

        if poems:
            poet_name = poems[0]['poet']
            print(format_text(f"Poems by [bright yellow][italic]{poet_name}[reset]"))

            for index, poem in enumerate(poems):
                print(format_text(f"[bright yellow][italic]{index + 1}. {poem['title']}[reset]"))
            print()
            return

        print(format_text(f"[bright red]Couldn't find poet: {poet.capitalize()}[reset]"))

    def list_all_poets(self):
        """List all poets with poem counts"""
        poets = self.db.get_all_poets()

        if poets:
            print(format_text(f"[bright yellow][italic]Poets:[reset]"))
            for index, (poet_name, poem_count) in enumerate(poets):
                print(format_text(f"[bright yellow][italic]{index + 1}. {poet_name} ({poem_count})[reset]"))
        else:
            print(format_text(f"[bright red]No poets in database[reset]"))

    def search_poems_with_term(self, search_term):
        """
        Search for poems with a term in the title (DB-backed, single query)

        Args:
            search_term: Term to search for in poem titles
        """
        print(format_text(f"[bright yellow][italic]Poems with term: {search_term}[reset]"))

        results = self.db.search_poem_titles(search_term=search_term, limit=500)
        if not results:
            print(format_text(f"[bright red]No poems found with term: {search_term}[reset]"))
            return

        # Group by poet for display
        current_poet = None
        idx = 0
        for row in results:
            poet_name = row['poet']
            title = row['title']
            if poet_name != current_poet:
                current_poet = poet_name
                idx = 0
                print(format_text(f"[bright yellow][italic]Poems by {poet_name}:[reset]"))
            idx += 1
            print(format_text(f"[bright yellow][italic]{idx}. {title}[reset]"))

    def search_full_text(self, query, limit=50):
        """
        Full-text search in poem content (NEW FEATURE!)

        Args:
            query: Search query (supports FTS5 syntax)
            limit: Maximum number of results

        Returns:
            list: List of tuples (poem_id, title, poet_name, content, rank)

        Example queries:
            - Simple: "love"
            - AND: "love AND heart"
            - Phrase: '"shall i compare thee"'
            - Proximity: 'NEAR(love death, 5)'
        """
        print(format_text(f"[bright yellow][italic]Full-text search for: {query}[reset]"))

        results = self.db.search_full_text(query, limit)

        if results:
            print(format_text(f"[bright green]Found {len(results)} results:[reset]"))
            for poem_id, title, poet_name, content, rank in results:
                print(format_text(f"[bright yellow][italic]• '{title}' by {poet_name}[reset]"))
        else:
            print(format_text(f"[bright red]No results found for: {query}[reset]"))

        return results

    def search(self, title: str, poet=""):
        """
        Search for a poem by title and/or poet
        Searches locally first, then online if not found

        Args:
            title: Poem title
            poet: Poet name (optional)

        Returns:
            tuple: (title, poet, content) or (None, None, None)
        """
        # Search in local database first
        poem_title, poem_poet, poem_text = self.__search_db(title, poet)

        # If not found locally and internet is available, search online
        if poem_text is None and check_internet():
            print("Searching on the poetry foundation")
            try:
                pTitle, pPoet, pBody = self.scraper.scrape_poem(title, poet)

                # Add to database
                self.add_poem(pTitle, pPoet, pBody)

                print(format_text(f"Found: [bright green][italic]'{pTitle}' by "
                                  f"'{pPoet}'[reset]"))
                return pTitle, pPoet, pBody

            except AttributeError:
                print(format_text(f"[bright red]Something went wrong :(\nCouldn't find {title} by {poet}[reset]"))
            except Exception as e:
                print(format_text(f"[bright red]{e}[reset]"))
            except KeyboardInterrupt:
                print(format_text(f"[bright red]Keyboard Interrupt[reset]"))
                raise KeyboardInterrupt

        if poem_text:
            return poem_title, poem_poet, poem_text
        else:
            return None, None, None

    def get_statistics(self):
        """
        Get database statistics (NEW FEATURE!)

        Returns:
            dict: Statistics about the database
        """
        return {
            'total_poets': self.db.get_poet_count(),
            'total_poems': self.db.get_poem_count(),
            'poets': self.db.get_all_poets()
        }
