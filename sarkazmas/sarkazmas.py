import json
import re
from urllib.parse import urlparse

RAW_DATA_FILE = 'Sarcasm_Headlines_Dataset.json'
MODIFIED_DATA_FILE = 'sarcasm_prepaired.json'

class Article:
    def __init__(self, headline, is_sarcastic, article_link):
        self.headline = headline
        self.is_sarcastic = is_sarcastic
        self.article_link = urlparse(article_link).netloc

    def __str__(self):
        return "Sarcastic: {0}, Headline: {1}".format(self.is_sarcastic, self.headline)

    __repr__ = __str__

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

def read_data(prep_data):
    with open(prep_data) as json_file:
        data = json.load(json_file)
        mappedData = list(map(lambda p: Article(p['headline'], p['is_sarcastic'], p['article_link']), data['sarkazmas']))
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

def get_urls(articles):
    urls = dict()
    
    for article in articles:    
        if article.article_link in urls:
            urls[article.article_link] += 1
        else:
            urls[article.article_link] = 1

    return urls

if __name__ == '__main__':
    data_prep(RAW_DATA_FILE, MODIFIED_DATA_FILE)
    parsed_data = read_data(MODIFIED_DATA_FILE)
    
    sarcastic_articles, not_sarcastic_articles = get_filtered_articles(parsed_data)
    print(get_urls(sarcastic_articles))
    print(get_urls(not_sarcastic_articles))

    sarcastic_lex = get_lex(sarcastic_articles)
    not_sarcastic_lex = get_lex(not_sarcastic_articles)

    print(sarcastic_lex)
    print(not_sarcastic_lex)
