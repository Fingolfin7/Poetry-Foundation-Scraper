import os
from Poems import Poems
from save_to_file import save_to_file
from ColourText import format_text


def main():
    poems = Poems()
    os.system('')
    
    while True:
        title, poet, poem = poems.random_poem()

        if poem is not None:
            poem = format_text("[italics]{}[reset]".format(poem))
            print(poem)

            x = input(
                format_text("\n[cyan]Save to file?[reset]\n[Y/N]:")
            ).lower()

            if x == 'y':
                save_to_file(title, poet, poem)

        print("\n")


if __name__ == "__main__":
    main()
