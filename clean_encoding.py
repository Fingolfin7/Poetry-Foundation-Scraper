import re
import unidecode


def clean(in_string="", add_line_breaks=False):
    in_string = re.sub(r"[•]", "", in_string)
    in_string = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', "", in_string)

    if add_line_breaks:
        in_string = re.sub(r'\s{2,}(?=[A-Z])', '\n', in_string)

    in_string = unidecode.unidecode(in_string)

    try:
        in_string = in_string.encode("ascii", errors="ignore").decode()
    except UnicodeEncodeError:
        try:
            in_string = in_string.encode("latin-1", errors="ignore").decode()
        except UnicodeEncodeError:
            in_string = in_string.encode("utf-8", errors="ignore").decode()

    return in_string