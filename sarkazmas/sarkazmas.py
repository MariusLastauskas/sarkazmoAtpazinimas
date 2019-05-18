import json
import re
import operator

RAW_DATA_FILE = 'Sarcasm_Headlines_Dataset.json'
MODIFIED_DATA_FILE = 'sarcasm_prepaired.json'

class Article:
    def __init__(self, headline, is_sarcastic):
        self.headline = headline
        self.is_sarcastic = is_sarcastic

    def __str__(self):
        return "Sarcastic: {0}, Headline: {1}".format(self.is_sarcastic, self.headline)

    __repr__ = __str__

class Article:
    def __init__(self, headline, is_sarcastic):
        self.headline = headline
        self.is_sarcastic = is_sarcastic

    def __str__(self):
        return "Sarcastic: {0}, Headline: {1}".format(self.is_sarcastic, self.headline)

def data_prep(dir_path, exit_path):
    open(exit_path, 'w').close()
    fout = open(exit_path, 'a')
    print(dir_path)
    fin = open(dir_path, 'r')

    fout.write('{"sarkazmas" : [')

    line = fin.readline()
    while line != "":
        fout.write(line + ',')
        nextLine = fin.readline()
        if nextLine == "":
            fout.write(line)
        line = nextLine

    fout.write(']}')

    fout.close()
    fin.close()

def get_lexem_sarcasm_lvl(sarcastic_lex, non_sarcastic_lex):
    n_sarc = 0
    n_non_sarc = 0
    for value in sarcastic_lex.values():
        n_sarc = n_sarc + value
    for value in non_sarcastic_lex.values():
        n_non_sarc = n_non_sarc + value

    sarcasm_lvl = {}
    for key in sarcastic_lex.keys():
        try:
            pSar = sarcastic_lex[key] / n_sarc
            pNonSar = non_sarcastic_lex[key] / n_non_sarc
            p = pSar / (pSar + pNonSar)
            sarcasm_lvl[key] = p
        except KeyError:
            sarcasm_lvl[key] = 0.99

    for key in non_sarcastic_lex.keys():
        try:
            sarcasm_lvl[key]
        except KeyError:
            try:
                pSar = sarcastic_lex[key] / n_sarc
                pNonSar = sarcastic_lex[key] / n_non_sarc
                p = pSar / (pSar + pNonSar)
                sarcasm_lvl[key] = p
            except KeyError:
                sarcasm_lvl[key] = 0.01
        except TypeError:
            continue

    return sarcasm_lvl

# def test_sarcasm(sarcastic_articles, non_sarcastic_articles):
#
#     for i in range(n_cross_validation):

def read_data(prep_data):
    with open(prep_data) as json_file:
        data = json.load(json_file)
        mappedData = list(map(lambda p: Article(p['headline'], p['is_sarcastic']), data['sarkazmas']))
        return mappedData

def get_filtered_articles(parsed_data):
    return list(filter(lambda x: x.is_sarcastic == 1, parsed_data)), list(filter(lambda x: x.is_sarcastic == 0, parsed_data))

def get_lex(articles):
    lex = dict()
    
    for article in articles:
        words = re.split(r'\W+', article.headline)

        for word in words:
            if word in lex:
                lex[word] += 1
            else:
                lex[word] = 1

    return lex

if __name__ == '__main__':
    data_prep(RAW_DATA_FILE, MODIFIED_DATA_FILE)
    parsed_data = read_data(MODIFIED_DATA_FILE)
    
    sarcastic_articles, not_sarcastic_articles = get_filtered_articles(parsed_data)

    sarcastic_lex = get_lex(sarcastic_articles)
    not_sarcastic_lex = get_lex(not_sarcastic_articles)

    lexem_sarcasm_lvl = get_lexem_sarcasm_lvl(sarcastic_lex, not_sarcastic_lex)

    lexem_sarcasm_lvl = sorted(lexem_sarcasm_lvl.items(), key=operator.itemgetter(1))
    print(lexem_sarcasm_lvl)