"""
Migration script to convert poems.json to SQLite database using SQLAlchemy ORM
"""
import json
import os
import shutil
from datetime import datetime
from models import DatabaseManager
from ColourText import format_text


def migrate_json_to_sqlite(json_path="poems.json", db_path="poems.db", backup=True):
    """
    Migrate poems from JSON file to SQLite database

    Args:
        json_path: Path to the JSON file
        db_path: Path to the SQLite database (will be created)
        backup: Whether to create a backup of the JSON file
    """
    print(format_text("[bright cyan]╔══════════════════════════════════════════════╗[reset]"))
    print(format_text("[bright cyan]║  Poetry Foundation → SQLite Migration       ║[reset]"))
    print(format_text("[bright cyan]╚══════════════════════════════════════════════╝[reset]\n"))

    # Check if JSON file exists
    if not os.path.exists(json_path):
        print(format_text(f"[bright red]✗ Error: {json_path} not found![reset]"))
        return False

    # Backup JSON file if requested
    if backup:
        backup_path = json_path.replace('.json', f'_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        try:
            shutil.copy(json_path, backup_path)
            print(format_text(f"[bright green]✓ Backup created: {backup_path}[reset]"))
        except Exception as e:
            print(format_text(f"[bright yellow]⚠ Warning: Could not create backup: {e}[reset]"))

    # Load JSON data
    print(format_text(f"[bright cyan]→ Loading data from {json_path}...[reset]"))
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(format_text(f"[bright green]✓ Loaded {len(data)} poets[reset]"))
    except Exception as e:
        print(format_text(f"[bright red]✗ Error loading JSON: {e}[reset]"))
        return False

    # Create database
    print(format_text(f"\n[bright cyan]→ Creating database: {db_path}...[reset]"))
    try:
        db = DatabaseManager(db_path)
        print(format_text(f"[bright green]✓ Database initialized with ORM models[reset]"))
    except Exception as e:
        print(format_text(f"[bright red]✗ Error creating database: {e}[reset]"))
        return False

    # Migrate data
    print(format_text(f"\n[bright cyan]→ Migrating poems...[reset]"))
    poem_count = 0
    poet_count = 0
    errors = []

    for poet_name, poems in data.items():
        poet_count += 1
        print(format_text(f"[bright yellow]  Migrating poems by: {poet_name}[reset]"))

        for title, content in poems.items():
            try:
                db.add_poem(title, poet_name, content)
                poem_count += 1
                print(format_text(f"[bright green]    ✓ {title}[reset]"))
            except Exception as e:
                errors.append((poet_name, title, str(e)))
                print(format_text(f"[bright red]    ✗ {title}: {e}[reset]"))

    # Summary
    print(format_text("\n[bright cyan]╔══════════════════════════════════════════════╗[reset]"))
    print(format_text("[bright cyan]║           Migration Summary                  ║[reset]"))
    print(format_text("[bright cyan]╚══════════════════════════════════════════════╝[reset]"))
    print(format_text(f"[bright green]✓ Poets migrated:  {poet_count}[reset]"))
    print(format_text(f"[bright green]✓ Poems migrated:  {poem_count}[reset]"))

    if errors:
        print(format_text(f"[bright red]✗ Errors:          {len(errors)}[reset]"))
        print(format_text("\n[bright red]Error details:[reset]"))
        for poet, title, error in errors:
            print(format_text(f"  [bright red]• {title} by {poet}: {error}[reset]"))
    else:
        print(format_text(f"[bright green]✓ Errors:          0[reset]"))

    # Verify migration
    print(format_text(f"\n[bright cyan]→ Verifying migration...[reset]"))
    db_poets = db.get_poet_count()
    db_poems = db.get_poem_count()
    print(format_text(f"[bright green]✓ Database contains: {db_poets} poets, {db_poems} poems[reset]"))

    # Success message
    print(format_text("\n[bright green]═══════════════════════════════════════════════[reset]"))
    print(format_text("[bright green]✓ Migration completed successfully![reset]"))
    print(format_text("[bright green]═══════════════════════════════════════════════[reset]\n"))

    # Next steps
    print(format_text("[bright cyan]Next steps:[reset]"))
    print(format_text("  1. Test the new database with: [bright yellow]python test_database.py[reset]"))
    print(format_text("  2. Update your application to use the new ORM models"))
    print(format_text(f"  3. Keep [bright yellow]{json_path}[reset] as a backup"))

    return True


def test_migration(db_path="poems.db"):
    """Test the migrated database with sample queries"""
    print(format_text("\n[bright cyan]╔══════════════════════════════════════════════╗[reset]"))
    print(format_text("[bright cyan]║           Testing Database                   ║[reset]"))
    print(format_text("[bright cyan]╚══════════════════════════════════════════════╝[reset]\n"))

    db = DatabaseManager(db_path)

    # Test 1: Get all poets
    print(format_text("[bright cyan]Test 1: All Poets[reset]"))
    poets = db.get_all_poets()
    for poet_name, count in poets:
        print(format_text(f"  [bright yellow]• {poet_name}[reset] ({count} poems)"))

    # Test 2: Search for a poem
    print(format_text("\n[bright cyan]Test 2: Search by Title[reset]"))
    result = db.search_poems(title="love")
    if result:
        print(format_text(f"  [bright green]✓ Found: '{result['title']}' by {result['poet']}[reset]"))
    else:
        print(format_text("  [bright yellow]No poems found with 'love' in title[reset]"))

    # Test 3: Full-text search
    print(format_text("\n[bright cyan]Test 3: Full-Text Search[reset]"))
    results = db.search_full_text("love", limit=5)
    if results:
        print(format_text(f"  [bright green]✓ Found {len(results)} results:[reset]"))
        for poem_id, title, poet_name, content, rank in results:
            print(format_text(f"    [bright yellow]• '{title}' by {poet_name}[reset]"))
    else:
        print(format_text("  [bright yellow]No poems found with 'love' in content[reset]"))

    print(format_text("\n[bright green]✓ All tests completed![reset]\n"))


if __name__ == '__main__':
    import sys

    # Parse command line arguments
    json_path = sys.argv[1] if len(sys.argv) > 1 else "poems.json"
    db_path = sys.argv[2] if len(sys.argv) > 2 else "poems.db"

    # Run migration
    success = migrate_json_to_sqlite(json_path, db_path)

    # Test if successful
    if success:
        test_migration(db_path)

