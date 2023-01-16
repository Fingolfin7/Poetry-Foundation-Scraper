import json

def make_list():
    mydict = {}
    with open("poems_old.json", 'r') as reader:
        jsonStr = reader.read()
        mydict = json.loads(jsonStr)

    title_list = []
    poet_list = list(mydict.keys())

    for poet in poet_list:
        title_list.append([poem for poem in mydict[poet]])

    return list(zip(poet_list, title_list))
