import os
from pathvalidate import sanitize_filename


def save_to_file(title, poet, poem,
                 file_type=".txt", dir_path=os.path.abspath(os.path.dirname(__file__))):

    if file_type[0] != '.':
        file_type = '.' + file_type

    filename = f"{title} by {poet}{file_type}"
    filename = sanitize_filename(filename)

    if not os.path.exists(dir_path):
        os.mkdir(dir_path)

    filepath = os.path.join(dir_path, filename)

    with open(filepath, 'w') as quill:
        quill.write(poem)
