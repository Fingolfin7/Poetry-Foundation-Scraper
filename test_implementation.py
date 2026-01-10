"""
Quick test to verify the complete implementation
"""
print("Testing Poetry Foundation Scraper with ORM Database...\n")

# Test 1: Import Poems class
print("1. Testing Poems class import...")
try:
    from Poems import Poems
    print("   ✓ Poems class imported successfully")
except Exception as e:
    print(f"   ✗ Error: {e}")
    exit(1)

# Test 2: Initialize Poems with database
print("\n2. Testing database connection...")
try:
    poems = Poems()
    print("   ✓ Database connected successfully")
except Exception as e:
    print(f"   ✗ Error: {e}")
    exit(1)

# Test 3: Get statistics
print("\n3. Testing database statistics...")
try:
    stats = poems.get_statistics()
    print(f"   ✓ Found {stats['total_poets']} poets")
    print(f"   ✓ Found {stats['total_poems']} poems")
except Exception as e:
    print(f"   ✗ Error: {e}")
    exit(1)

# Test 4: Search by title
print("\n4. Testing title search...")
try:
    title, poet, text = poems.search("sonnet", "")
    if title:
        print(f"   ✓ Found: '{title}' by {poet}")
    else:
        print("   ⚠ No results (but search worked)")
except Exception as e:
    print(f"   ✗ Error: {e}")
    exit(1)

# Test 5: Full-text search (NEW!)
print("\n5. Testing full-text search...")
try:
    results = poems.search_full_text("love", limit=5)
    if results:
        print(f"   ✓ Found {len(results)} poems containing 'love'")
        if len(results) > 0:
            _, title, poet, _, _ = results[0]
            print(f"   ✓ First result: '{title}' by {poet}")
    else:
        print("   ⚠ No results (but search worked)")
except Exception as e:
    print(f"   ✗ Error: {e}")
    exit(1)

# Test 6: Random poem
print("\n6. Testing random poem...")
try:
    title, poet, text = poems.random_poem()
    if title:
        print(f"   ✓ Random poem: '{title}' by {poet}")
    else:
        print("   ⚠ No random poem found")
except Exception as e:
    print(f"   ✗ Error: {e}")
    exit(1)

# Test 7: List all poets
print("\n7. Testing list all poets...")
try:
    poems.list_all_poets()
    print("   ✓ Listed all poets successfully")
except Exception as e:
    print(f"   ✗ Error: {e}")
    exit(1)

print("\n" + "="*50)
print("✓ ALL TESTS PASSED!")
print("="*50)
print("\nYour Poetry Foundation Scraper is ready to use!")
print("\nTry:")
print("  python main.py       # CLI with menu")
print("  python gui_app.py    # GUI with full-text search")

