import os
import json
import random
from scraper import scrape_poem
from ColourText import format_text
from check_internet import check_internet


class Poems:
    def __init__(self, file="poems.json"):
        self.__dict = {}
        self.base_path = os.path.abspath(os.path.dirname(__file__))
        self.path = os.path.join(self.base_path, file)
        self.__load()

    def __load(self):
        if not os.path.exists(self.path):
            return

        with open(self.path, 'r') as reader:
            jsonStr = reader.read()
            self.__dict = json.loads(jsonStr)

    def get_dict(self):
        return self.__dict

    def add_poem(self, title, poet, poem):
        if poet not in self.__dict:
            self.__dict[poet] = {}
        if poet in self.__dict:
            self.__dict[poet][title] = poem

        self.save()

    def save(self):
        json_data = json.dumps(self.__dict, indent=4)
        with open(self.path, "w") as js_writer:
            js_writer.write(json_data)
            js_writer.close()

    def random_poem(self):
        return self.__search_dict(random.choice(list(self.__dict.keys())))

    def __search_dict(self, title, poet=""):
        for key in self.__dict:
            if poet.lower() in key.lower():
                for poem_title in self.__dict[key]:
                    if title.lower() in poem_title.lower():
                        print(
                            format_text(f"Found: [bright yellow][italic]'{poem_title}' by "
                                        f"'{key}'[reset]")
                        )
                        return poem_title, key, self.__dict[key][poem_title]
        return None, None, None

    def list_all_by_poet(self, poet):
        for poem_key in self.__dict:
            if poet.lower() in poem_key.lower():
                print(format_text(f"Poems by [bright yellow][italic]{poem_key}[reset]"))

                for index, poem_title in enumerate(self.__dict[poem_key]):
                    print(format_text(f"[bright yellow][italic]{index + 1}. {poem_title}[reset]"))
                print()
                return

        print(format_text(f"[bright red]Couldn't find poet: {poet.capitalize()}[reset]"))
        return

    def list_all_poets(self):
        print(format_text(f"[bright yellow][italic]Poets:[reset]"))
        for index, poet in enumerate(self.__dict):
            poem_count = len(self.__dict[poet])
            print(format_text(f"[bright yellow][italic]{index + 1}. {poet} ({poem_count})[reset]"))

    def search_poems_with_term(self, search_term):
        print(format_text(f"[bright yellow][italic]Poems with term: {search_term}[reset]"))

        def filter_poem(poem):
            return search_term.lower() in poem.lower()

        for poet, poems in self.__dict.items():
            by_poet = list(filter(filter_poem, poems))

            if by_poet:
                print(format_text(f"[bright yellow][italic]Poems by {poet}:[reset]"))

                for index, poem in enumerate(by_poet):
                    print(format_text(f"[bright yellow][italic]{index + 1}. {poem}[reset]"))

    def search(self, title: str, poet=""):
        poem_title, poem_poet, poem_text = self.__search_dict(title, poet)

        if poem_text is None and check_internet():
            print("Searching on the poetry foundation")
            try:
                pTitle, pPoet, pBody = scrape_poem(title, poet)
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
            # self.list_all_by_poet(poet)
            return None, None, None

