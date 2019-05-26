import json
import re
import operator
from urllib.parse import urlparse
import matplotlib.pyplot as plt
import random

RAW_DATA_FILE = 'Sarcasm_Headlines_Dataset.json'
MODIFIED_DATA_FILE = 'sarcasm_prepaired.json'
LEXEM_COUNT = 5
MINIMUM_OCCURENCEC = 2
SARCASM_BORDER = 0.2
SECTION_SIZE = 2
FILTRATIONS_COUNT = 1


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


def get_lexem_sarcasm_lvl(sarcastic_lex, non_sarcastic_lex):
    n_sarc = 0
    n_non_sarc = 0
    for value in sarcastic_lex.values():
        n_sarc = n_sarc + value
    for value in non_sarcastic_lex.values():
        n_non_sarc = n_non_sarc + value

    sarcasm_lvl = {}
    for key in sarcastic_lex.keys():
        key = key.lower()
        try:
            pSar = sarcastic_lex[key] / n_sarc
            pNonSar = non_sarcastic_lex[key] / n_non_sarc
            p = pSar / (pSar + pNonSar)
            sarcasm_lvl[key] = p
        except KeyError:
            sarcasm_lvl[key] = 0.99

    for key in non_sarcastic_lex.keys():
        key = key.lower()
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


def read_data(prep_data):
    with open(prep_data) as json_file:
        data = json.load(json_file)
        mappedData = list(
            map(lambda p: Article(p['headline'], p['is_sarcastic'], p['article_link']), data['sarkazmas']))
        return mappedData


def get_separated_articles(parsed_data):
    return list(filter(lambda x: x.is_sarcastic == 1, parsed_data)), list(
        filter(lambda x: x.is_sarcastic == 0, parsed_data))


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


def test_data(art, isSarc, lexem_sarcasm_lvl):
    correct = 0

    for a in art:
        p = test_article_sarcasm(a, lexem_sarcasm_lvl)
        if isSarc == 1:
            if p >= SARCASM_BORDER:
                correct = correct + 1
        else:
            if p < SARCASM_BORDER:
                correct = correct + 1
    return correct

def test_article_sarcasm(art, lexem_sarcasm_lvl):
    art_words_sarc = {}
    words = get_lex({art})
    for word in words:
        if word == '':
            continue
        word = word.lower()
        try:
            x = lexem_sarcasm_lvl[word]
        except KeyError:
            x = 0.4
        x = abs(x - 0.5)
        art_words_sarc[word] = x

    art_words_sarc = sorted(art_words_sarc.items(), key=operator.itemgetter(1))
    art_words_sarc.reverse()

    n = min(LEXEM_COUNT, len(art_words_sarc))
    j = 0
    pp1 = 1
    pp2 = 2

    for key in art_words_sarc:
        if j >= n:
            break
        try:
            sarcLvl = lexem_sarcasm_lvl[key[0]]
        except KeyError:
            sarcLvl = 0.4
        pp1 = pp1 * sarcLvl
        pp2 = pp2 * (1 - sarcLvl)
        j = j + 1
    pp2 = pp2 + pp1
    p = pp1 / pp2
    return p

def get_urls(articles):
    urls = dict()

    for article in articles:
        if article.article_link in urls:
            urls[article.article_link] += 1
        else:
            urls[article.article_link] = 1

    return urls


def filter_lex(sarcastic_lex, not_sarcastic_lex, minimum_count):
    return dict(filter(lambda x: x[1] > minimum_count or x[0] in not_sarcastic_lex, sarcastic_lex.items())), dict(
        filter(lambda x: x[1] > minimum_count or x[0] in sarcastic_lex, not_sarcastic_lex.items()))

def filter_training_data(art, isSarc, sarcasm_lvl):
    i = 0
    for a in art:
        p = test_article_sarcasm(a, sarcasm_lvl)
        if isSarc == 1:
            if p < 0.01:
                del art[i]
                i = i - 1
        else:
            if p > 0.99:
                del art[i]
                i = i - 1
        i = i + 1
    return art

def build_word_map(data):
    output = {}
    i = 0
    for lex in data:
        output[lex] = i
        i = i + 1
    return output

def build_embedding_matrix(data, dim):
    output = {}
    for lex in data:
        output[lex] = {}
        for i in range(dim):
            output[lex][i] = random.random()
    return output

def sigmoid(x):
    e = 2.71828182845
    try:
        return 1 / (1 + e**(-1 * x))
    except OverflowError:
        if x > 0:
            return 0.9
        else:
            return -0.9

def nn_test(data, Wh, Wo, bh, bo, n_hidden_neurons):
    Etotal = 0
    for art in data:
        # suskaiciuojamos tinko output reiksmes
        words = get_lex({art})
        netH = {}
        outH = {}
        for i in range(n_hidden_neurons):
            netH[i] = 0
            outH[i] = 0
            for word in words:
                try:
                    netH[i] = netH[i] + Wh[i][word_map[word]] + bh
                except KeyError:
                    continue
            outH[i] = sigmoid(netH[i])
        netO = {}
        outO = {}
        for i in range(2):
            netO[i] = 0
            for j in range(n_hidden_neurons):
                netO[i] = netO[i] + outH[j] * Wo[i][j] + bo
            outO[i] = sigmoid(netO[i])

        # suskaiciuojama klaidos funkcija
        E = 0
        if art.is_sarcastic == 0:
            E = ((0.9 - outO[0]) ** 2 + (-0.9 - outO[1]) ** 2) / 2
        else:
            E = ((-0.9 - outO[0]) ** 2 + (0.9 - outO[1]) ** 2) / 2
        Etotal = Etotal + E
    return Etotal

def nn_test_data(data, Wh, Wo, bh, bo, n_hidden_neurons, isSarcastic):
    correct = 0
    for art in data:
        words = get_lex({art})
        netH = {}
        outH = {}
        for i in range(n_hidden_neurons):
            netH[i] = 0
            outH[i] = 0
            for word in words:
                try:
                    netH[i] = netH[i] + Wh[i][word_map[word]] + bh
                except KeyError:
                    continue
            outH[i] = sigmoid(netH[i])
        netO = {}
        outO = {}
        for i in range(2):
            netO[i] = 0
            for j in range(n_hidden_neurons):
                netO[i] = netO[i] + outH[j] * Wo[i][j] + bo
            outO[i] = sigmoid(netO[i])
        if isSarcastic == 1:
            if outO[1] > outO[0]:
                correct = correct + 1
        else:
            if outO[0] > outO[1]:
                correct = correct + 1
    return correct / len(data)

def nn_train(data, word_map):
    n_hidden_neurons = 16;
    n_max_train = 100;
    n_validation = 3;
    # duomenys suskirstomi į apmokymo rinkinius
    train_set = data[:len(data) * 9 // 10]
    validation_set = data[len(data) * 9 // 10:]
    # priskiriamos pradinės reiksmes jungciu svoriams
    speed = 0.00001
    Wh = {}
    for i in range(n_hidden_neurons):
        wh = {}
        for j in range(len(word_map)):
            wh[j] = 0.4
        Wh[i] = wh

    Wo = {}
    for i in range(2):
        wo = {}
        for j in range(n_hidden_neurons):
            wo[j] = 0.4
        Wo[i] = wo

    bh = 0.01
    bo = 0.01

    print(nn_test(validation_set, Wh, Wo, bh, bo, n_hidden_neurons))

    WhStable = {}
    WoStable = {}
    Estable = -1
    false_train = 0

    for ii in range(n_max_train):
        WhNew = {}
        WhNewSum = {}
        for i in range(n_hidden_neurons):
            whNew = {}
            whNewSum = {}
            for j in range(len(word_map)):
                whNew[j] = 0
                whNewSum[j] = 0
            WhNew[i] = whNew
            WhNewSum[i] = whNewSum
        WoNew = {}
        for i in range(2):
            woNew = {}
            for j in range(n_hidden_neurons):
                woNew[j] = 0
            WoNew[i] = woNew

        for art in train_set:
            # suskaiciuojamos tinko output reiksmes
            words = get_lex({art})
            netH = {}
            outH = {}
            for i in range(n_hidden_neurons):
                netH[i] = 0
                outH[i] = 0
                for word in words:
                    try:
                        netH[i] = netH[i] + Wh[i][word_map[word]]
                    except KeyError:
                        continue
                netH[i] = netH[i] + bh
                outH[i] = sigmoid(netH[i])
            netO = {}
            outO = {}
            for i in range(2):
                netO[i] = 0
                for j in range(n_hidden_neurons):
                    netO[i] = netO[i] + outH[j] * Wo[i][j]
                netO[i] = netO[i] + bo
                outO[i] = sigmoid(netO[i])

            # suskaiciuojama klaidos funkcija
            E = 0
            if art.is_sarcastic == 0:
                E = ((0.9 - outO[0])**2 + (-0.9 - outO[1])**2) / 2
            else:
                E = ((-0.9 - outO[0])**2 + (0.9 - outO[1])**2) / 2

            # perskaiciuojami tinklo svoriai
            # išorinis sluoksnis
            for i in range(n_hidden_neurons):
                if art.is_sarcastic == 0:
                    WoNew[0][i] = WoNew[0][i] + Wo[0][i] + speed * (0.9 - outO[0]) * outO[0] * (1 - outO[0]) * outH[i]
                else:
                    WoNew[0][i] = WoNew[0][i] + Wo[0][i] + speed * (-0.9 - outO[0]) * outO[0] * (1 - outO[0]) * outH[i]
            for i in range(n_hidden_neurons):
                if art.is_sarcastic == 0:
                    WoNew[1][i] = WoNew[1][i] + Wo[1][i] + speed * (-0.9 - outO[1]) * outO[1] * (1 - outO[1]) * outH[i]
                else:
                    WoNew[1][i] = WoNew[1][i] + Wo[1][i] + speed * (0.9 - outO[1]) * outO[1] * (1 - outO[1]) * outH[i]

            # pasleptas sluoksnis
            for i in range(n_hidden_neurons):
                for word in words:
                    try:
                        if art.is_sarcastic == 0:
                            WhNew[i][word_map[word]] = -(0.9 - outO[0]) * outO[0] * (1 - outO[0]) * Wh[i][word_map[word]] - \
                                                       (-0.9 - outO[1]) * outO[1] * (1 - outO[1])* Wh[i][word_map[word]]
                        else:
                            WhNew[i][word_map[word]] = -(-0.9 - outO[0]) * outO[0] * (1 - outO[0]) * Wh[i][word_map[word]] - \
                                                       (0.9 - outO[1]) * outO[1] * (1 - outO[1]) * Wh[i][word_map[word]]
                        # WhNew[i][word_map[word]] = WhNew[i][word_map[word]] * Wh[i][word_map[word]]
                        WhNew[i][word_map[word]] = WhNew[i][word_map[word]] * outH[i] * (1 - outH[i]) * 1
                        WhNew[i][word_map[word]] = Wh[i][word_map[word]] - speed * WhNew[i][word_map[word]]
                    except KeyError:
                        continue
                    WhNewSum[i][word_map[word]] = WhNewSum[i][word_map[word]] + WhNew[i][word_map[word]]

        # atnaujinami tinklo svoriai
        for i in range(2):
            for j in range(n_hidden_neurons):
                Wo[i][j] = WoNew[i][j] / len(train_set)
        for i in range(n_hidden_neurons):
            for j in range(len(Wh[i])):
                Wh[i][j] = WhNewSum[i][j] / len(Wh[i])

        Enew = nn_test(validation_set, Wh, Wo, bh, bo, n_hidden_neurons)
        print(ii, ") ", Enew)
        if (Estable == -1.0 or Enew < Estable):
            Estable = Enew
            WhStable = Wh
            WoStable = Wo
            false_train = 0
        else:
            false_train = false_train + 1
            if false_train >= n_validation:
                break

    return WhStable, WoStable, bo, bh, n_hidden_neurons




if __name__ == '__main__':
    data_prep(RAW_DATA_FILE, MODIFIED_DATA_FILE)
    parsed_data = read_data(MODIFIED_DATA_FILE)

    i = 0
    sarcasm_result = 0;
    not_sarcasm_result = 0;

    for x in range(SECTION_SIZE):

        sarcastic_articles, not_sarcastic_articles = get_separated_articles(
            parsed_data[:len(parsed_data) * x // SECTION_SIZE] + parsed_data[
                                                                 len(parsed_data) * (x + 1) // SECTION_SIZE:])
        for j in range(FILTRATIONS_COUNT):
            sarcastic_lex = get_lex(sarcastic_articles)
            not_sarcastic_lex = get_lex(not_sarcastic_articles)

            # Duomenu pasifiltravimui, jei nenorima, jog labai mazo kiekio leksemos, esancios tik vienoje leksemu puseje, neisdarkytu rezultatu
            f_slex, f_nslex = filter_lex(sarcastic_lex, not_sarcastic_lex, MINIMUM_OCCURENCEC)

            lexem_sarcasm_lvl = get_lexem_sarcasm_lvl(f_slex, f_nslex)
            filter_training_data(sarcastic_articles, 1, lexem_sarcasm_lvl)
            filter_training_data(not_sarcastic_articles, 0, lexem_sarcasm_lvl)
        sarcastic_test_data, not_sarcastic_test_data = get_separated_articles(parsed_data[len(parsed_data) * x // SECTION_SIZE : len(parsed_data) * (x + 1) // SECTION_SIZE])

        word_map = build_word_map(lexem_sarcasm_lvl)
        Wh, Wo, bo, bh, n_hidden_neurons = nn_train(parsed_data, word_map)
        nn_sarcastic_test_results = nn_test_data(sarcastic_test_data, Wh, Wo, bh, bo, n_hidden_neurons, 1)
        nn_not_sarcastic_test_results = nn_test_data(not_sarcastic_test_data, Wh, Wo, bh, bo, n_hidden_neurons, 0)
        print(" ****** NN test " + str(i) + " ******* ")
        print(nn_sarcastic_test_results)
        print(nn_not_sarcastic_test_results)

        # sarcasm_test_result = test_data(sarcastic_test_data, 1, lexem_sarcasm_lvl) / len(sarcastic_test_data)
        # sarcasm_result = sarcasm_result + sarcasm_test_result
        # not_sarcasm_test_result = test_data(not_sarcastic_test_data, 0, lexem_sarcasm_lvl) / len(not_sarcastic_test_data)
        # not_sarcasm_result = not_sarcasm_result + not_sarcasm_test_result
        # print(" ****** test " + str(i) + " ******* ")
        # print(sarcasm_test_result)
        # print(not_sarcasm_test_result)
        # print()
        # i = i + 1
        # # # plot
        # # plt.scatter(list(lexem_sarcasm_lvl.keys())[-1000:], list(lexem_sarcasm_lvl.values())[-1000:])
        # # plt.show()

    print("Sarcasm detected at: " + str(sarcasm_result / SECTION_SIZE * 100) + "% rate")
    print("Not sarcasm detected at: " + str(not_sarcasm_result / SECTION_SIZE * 100) + "% rate")

