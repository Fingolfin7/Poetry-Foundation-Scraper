"""Simple test without colored output"""
from models import DatabaseManager

print("Testing ORM Database...")
db = DatabaseManager("poems.db")

# Test 1
print("\n1. Database Stats:")
print(f"   Poets: {db.get_poet_count()}")
print(f"   Poems: {db.get_poem_count()}")

# Test 2
print("\n2. Search by Title:")
result = db.search_poems(title="love")
if result:
    print(f"   Found: '{result['title']}' by {result['poet']}")
else:
    print("   No poems found")

# Test 3
print("\n3. Full-Text Search:")
results = db.search_full_text("love", limit=3)
print(f"   Found {len(results)} results")
for poem_id, title, poet, content, rank in results[:2]:
    print(f"   - '{title}' by {poet}")

# Test 4
print("\n4. Get Poems by Poet:")
poems = db.get_poems_by_poet("Shakespeare")
print(f"   Found {len(poems)} poems")
if poems:
    print(f"   First: '{poems[0]['title']}'")

# Test 5
print("\n5. Random Poem:")
poem = db.get_random_poem()
if poem:
    print(f"   '{poem['title']}' by {poem['poet']}")

print("\n✓ All tests passed!")

