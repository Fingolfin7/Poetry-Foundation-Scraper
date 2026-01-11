"""
Quick test of the ORM database
"""
from models import DatabaseManager
from ColourText import format_text

def test():
    print(format_text("[bright cyan]Testing ORM Database...[reset]\n"))

    db = DatabaseManager("poems.db")

    # Test 1: Count
    print(format_text("[bright cyan]Test 1: Database Stats[reset]"))
    poet_count = db.get_poet_count()
    poem_count = db.get_poem_count()
    print(format_text(f"  [bright green]✓ Found {poet_count} poets and {poem_count} poems[reset]"))

    # Test 2: Search by title
    print(format_text("\n[bright cyan]Test 2: Search by Title[reset]"))
    result = db.search_poems(title="love")
    if result:
        print(format_text(f"  [bright green]✓ Found: '{result['title']}' by {result['poet']}[reset]"))
    else:
        print(format_text("  [bright yellow]⚠ No poems found with 'love' in title[reset]"))

    # Test 3: Full-text search
    print(format_text("\n[bright cyan]Test 3: Full-Text Search[reset]"))
    try:
        results = db.search_full_text("love", limit=5)
        if results:
            print(format_text(f"  [bright green]✓ Found {len(results)} results:[reset]"))
            for i, (poem_id, title, poet_name, content, rank) in enumerate(results[:3], 1):
                print(format_text(f"    {i}. [bright yellow]'{title}' by {poet_name}[reset]"))
        else:
            print(format_text("  [bright yellow]⚠ No poems found with 'love' in content[reset]"))
    except Exception as e:
        print(format_text(f"  [bright red]✗ Error: {e}[reset]"))

    # Test 4: Get poems by poet
    print(format_text("\n[bright cyan]Test 4: Get Poems by Poet[reset]"))
    poems = db.get_poems_by_poet("Shakespeare")
    if poems:
        print(format_text(f"  [bright green]✓ Found {len(poems)} poems by {poems[0]['poet']}[reset]"))
        for i, poem in enumerate(poems[:3], 1):
            print(format_text(f"    {i}. [bright yellow]{poem['title']}[reset]"))
    else:
        print(format_text("  [bright yellow]⚠ No poems found for 'Shakespeare'[reset]"))

    # Test 5: Random poem
    print(format_text("\n[bright cyan]Test 5: Random Poem[reset]"))
    poem = db.get_random_poem()
    if poem:
        print(format_text(f"  [bright green]✓ Random poem: '{poem['title']}' by {poem['poet']}[reset]"))
    else:
        print(format_text("  [bright red]✗ No random poem found[reset]"))

    print(format_text("\n[bright green]✓ All tests completed![reset]\n"))

if __name__ == '__main__':
    test()

