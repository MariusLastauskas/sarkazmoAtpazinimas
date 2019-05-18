import json

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

def get_lexem_spam_name(sarcastic_lex, non_sarcastic_lex):
    n_sarc = 0
    n_non_sarc = 0
    for value in sarcastic_lex.values():
        sarcastic_n = n_sarc + value['count']
    for value in non_sarcastic_lex.values():
        non_sarcastic_n = n_non_sarc + value['count']

    sarcasm_lvl = {}
    for key in sarcastic_lex.keys():
        try:
            pSar = sarcastic_lex[key] / n_sarc
            pNonSar = non_sarcastic_lex[key] / n_non_sarc
            p = pSar / (pSar / pNonSar)
            sarcasm_lvl[key] = p
        except KeyError:
            sarcasm_lvl[key] = 0.99

    for key in non_sarcastic_lex.key():
        try:
            sarcasm_lvl[key]
        except KeyError:
            try:
                pSar = sarcastic_lex[key] / n_sarc
                pNonSar = sarcastic_lex[key] / n_non_sarc
                p = pSar / (pSar / pNonSar)
                sarcasm_lvl[key] = p
            except KeyError:
                sarcasm_lvl = 0.01

    return sarcasm_lvl

# def test_sarcasm(sarcastic_articles, non_sarcastic_articles):
#
#     for i in range(n_cross_validation):


if __name__ == '__main__':
    raw_data = 'Sarcasm_Headlines_Dataset.json'
    prep_data = 'sarcasm_prepaired.json'
    data_prep(raw_data, prep_data)
    articles = {}
    n_cross_validation = 10

    with open(prep_data) as json_file:
        data = json.load(json_file)
        i = 0
        for p in data['sarkazmas']:
            d = Article(p['headline'], p['is_sarcastic'])
            articles[i] = d
            i = i + 1
        # print(articles[5])

    for i in range(n)
