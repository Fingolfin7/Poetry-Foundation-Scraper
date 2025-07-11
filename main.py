import os
from Poems import Poems
from clean_encoding import clean
from save_to_file import save_to_file
from ColourText import format_text


def main():
    poems = Poems()
    os.system('')

    while True:
        # print(poems.random_poem())
        search_name = input("Enter poem name: ").strip()
        search_poet = input("Enter poet: ").strip()

        # clean the input to match the format in the poems.json file
        search_name = clean(search_name)
        search_poet = clean(search_poet)

        # print(f"Reformatted search name: {search_name}")
        # print(f"Reformatted search poet: {search_poet}")

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

        print("\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
