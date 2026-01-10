import os
from Poems import Poems
from clean_encoding import clean
from save_to_file import save_to_file
from ColourText import format_text


def main():
    poems = Poems()
    os.system('')

    while True:
        print(format_text("\n[bright cyan]╔══════════════════════════════════════╗[reset]"))
        print(format_text("[bright cyan]║   Poetry Foundation Search           ║[reset]"))
        print(format_text("[bright cyan]╚══════════════════════════════════════╝[reset]"))
        print(format_text("[cyan]1.[reset] Search by title/poet"))
        print(format_text("[cyan]2.[reset] Full-text search (search inside poems)"))
        print(format_text("[cyan]3.[reset] Random poem"))
        print(format_text("[cyan]4.[reset] List all poets"))
        print(format_text("[cyan]5.[reset] Exit"))

        choice = input(format_text("\n[bright yellow]Choose an option (1-5):[reset] ")).strip()

        if choice == '1':
            # Search by title/poet
            search_name = input("Enter poem name: ").strip()
            search_poet = input("Enter poet: ").strip()

            # Clean the input
            search_name = clean(search_name)
            search_poet = clean(search_poet)

            title, poet, poem = poems.search(search_name, search_poet)

            if poem:
                poem = clean(poem, False)
                poem = format_text("[italics]{}[reset]".format(poem))
                print(poem)

                x = input(
                    format_text("\n[cyan]Save to file?[reset]\n[Y/N]:")
                ).lower()

                if x == 'y':
                    save_to_file(title, poet, poem, ".txt", "File Saves")
                input("Press enter to continue...")
            else:
                print(format_text(f"\n[cyan]Searching for poems by {search_poet}...[reset]"))
                poems.list_all_by_poet(search_poet)

                print(format_text(f"\n[cyan]Searching for any poems with the term(s) [italic]{search_name}[reset]"
                                  f"[cyan]...[reset]\n"))
                poems.search_poems_with_term(search_name)

        elif choice == '2':
            # NEW: Full-text search
            search_query = input(format_text("\n[bright yellow]Enter search query:[reset] ")).strip()
            print(format_text(f"\n[cyan]Searching poem content for: '{search_query}'...[reset]\n"))

            results = poems.search_full_text(search_query, limit=20)

            if results:
                print(format_text(f"[bright green]Found {len(results)} results:[reset]\n"))
                for i, (poem_id, title, poet_name, content, rank) in enumerate(results, 1):
                    print(format_text(f"[bright yellow]{i}. '{title}'[reset] by [cyan]{poet_name}[reset]"))

                # Ask if user wants to view a poem
                view = input(format_text("\n[cyan]Enter number to view poem (or press Enter to skip):[reset] ")).strip()
                if view.isdigit() and 1 <= int(view) <= len(results):
                    idx = int(view) - 1
                    _, title, poet_name, content, _ = results[idx]
                    content = clean(content, False)
                    content = format_text("[italics]{}[reset]".format(content))
                    print(f"\n{content}\n")

                    x = input(format_text("\n[cyan]Save to file?[reset]\n[Y/N]:")).lower()
                    if x == 'y':
                        save_to_file(title, poet_name, content, ".txt", "File Saves")
            else:
                print(format_text(f"[bright red]No poems found matching '{search_query}'[reset]"))

            input("Press enter to continue...")

        elif choice == '3':
            # Random poem
            title, poet, poem = poems.random_poem()
            if poem:
                poem = clean(poem, False)
                poem = format_text("[italics]{}[reset]".format(poem))
                print(f"\n{format_text(f'[bright yellow]{title}[reset] by [cyan]{poet}[reset]')}\n")
                print(poem)

                x = input(format_text("\n[cyan]Save to file?[reset]\n[Y/N]:")).lower()
                if x == 'y':
                    save_to_file(title, poet, poem, ".txt", "File Saves")
                input("Press enter to continue...")
            else:
                print(format_text("[bright red]No poems in database[reset]"))
                input("Press enter to continue...")

        elif choice == '4':
            # List all poets
            poems.list_all_poets()
            input("\nPress enter to continue...")

        elif choice == '5':
            print(format_text("[bright cyan]Goodbye![reset]"))
            break

        else:
            print(format_text("[bright red]Invalid choice. Please enter 1-5.[reset]"))
            input("Press enter to continue...")

        # Removed old code that was always running

        print("\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
