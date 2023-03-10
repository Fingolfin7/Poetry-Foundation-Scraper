import os
from Poems import Poems
from save_to_file import save_to_file
from ColourText import format_text


def main():
    poems = Poems()
    os.system('')

    while True:
        # print(poems.random_poem())
        name = input("Enter poem name: ")
        poet = input("Enter poet: ")

        title, poet, poem = poems.search(f"{name}", f"{poet}")

        if poem is not None:
            poem = format_text("[italics]{}[reset]".format(poem))
            print(poem)

            x = input(
                format_text("\n[cyan]Save to file?[reset]\n[Y/N]:")
            ).lower()

            if x == 'y':
                save_to_file(title, poet, poem, ".txt", "File Saves")

        print("\n")


if __name__ == "__main__":
    main()
