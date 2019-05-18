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

if __name__ == '__main__':
    raw_data = 'Sarcasm_Headlines_Dataset.json'
    prep_data = 'sarcasm_prepaired.json'
    data_prep(raw_data, prep_data)
    with open(prep_data) as json_file:
        data = json.load(json_file)
        for p in data['sarkazmas']:
            d = Article(p['headline'], p['is_sarcastic'])
            print(d)