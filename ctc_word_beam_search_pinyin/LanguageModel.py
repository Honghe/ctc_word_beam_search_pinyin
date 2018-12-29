from __future__ import division
from __future__ import print_function

from ctc_word_beam_search_pinyin.PrefixTree import PrefixTree
from ctc_word_beam_search_pinyin.TransformedDict import TransformedDict
from ctc_word_beam_search_pinyin.file_dict import PinyinDict


def isIntList(l):
    isTrue = True
    for i in l:
        if not type(i) is int:
            isTrue = False
    return isTrue


def preProcessCorpus(text):
    '''
    使用#作为单词间的间隔
    e.g. 给#某某#加10分
    :param text:
    :return: [sentence, word, char]
    '''
    corpus = []
    for l in text.split('\n'):
        if l != '':
            corpus.append([word.split() for word in l.split('#')])
    return corpus


def preProcessChars(text):
    chars = []
    for l in text.split('\n'):
        # not strip
        if l != '':
            chars.append(l)
    return chars

def uniqueListOfLists(ll):
    return [list(x) for x in set(tuple(x) for x in ll)]

class LanguageModel:
    "unigram/bigram LM, add-k smoothing"

    def __init__(self, corpus, pinyinDict, nonWordChars):
        '''read text from filename, specify chars which are contained in dataset, specify chars which form words
        汉字转成拼音并使用数字编码, 因cnn+ctc模型是使用拼音而不是音素训练的
        :param corpus, each line one sentence with separating words by #
        '''
        self.pinyinDict = pinyinDict
        # preprocess
        corpus = preProcessCorpus(corpus)
        # pinyin to number
        corpus = [[pinyinDict.encode(words) for words in sentence] for sentence in corpus]
        chars = list(self.pinyinDict.pinyinMap().keys())
        nonWordChars = preProcessChars(nonWordChars)
        # pinyin to number
        nonWordChars = self.pinyinDict.encode(nonWordChars)
        wordChars = list(set(chars) - set(nonWordChars))

        self.smoothing = False
        self.addK = 1.0 if self.smoothing else 0.0
        allWords = [word for sentence in corpus for word in sentence]
        self.uniqueWords = uniqueListOfLists(allWords)
        self.numWords = len(allWords)
        self.numUniqueWords = len(self.uniqueWords)

        # create unigrams
        self.unigrams = TransformedDict([])
        for w in allWords:
            if w not in self.unigrams:
                self.unigrams[w] = 0
            self.unigrams[w] += 1 / self.numWords

        # create unnormalized bigrams
        bigrams = TransformedDict([])
        for sentence in corpus:
            for i in range(len(sentence) - 1):
                w1 = sentence[i]
                w2 = sentence[i + 1]
                if w1 not in bigrams:
                    bigrams[w1] = TransformedDict([])
                if w2 not in bigrams[w1]:
                    bigrams[w1][w2] = self.addK  # add-K
                bigrams[w1][w2] += 1


        # normalize bigrams
        for w1 in bigrams.keys():
            # sum up
            probSum = self.numUniqueWords * self.addK  # add-K smoothing
            for w2 in bigrams[w1].keys():
                probSum += bigrams[w1][w2]
            # and divide
            for w2 in bigrams[w1].keys():
                bigrams[w1][w2] /= probSum
        self.bigrams = bigrams

        # create prefix tree
        self.tree = PrefixTree()  # create empty tree
        for sentence in corpus:
            self.tree.addWords(sentence)  # add all unique words to tree

        # list of all chars, word chars and nonword chars
        self.allChars = chars
        self.wordChars = wordChars
        self.nonWordChars = nonWordChars

    def getNextWords(self, text):
        "text must be prefix of a word"
        return self.tree.getNextWords(text)

    def getNextWordsPinyin(self, text):
        if type(text) is list and not isIntList(text):
            text = self.pinyinDict.encode(text)
        words = self.getNextWords(text)
        "text must be prefix of a word"
        words_pinyin = []
        for word in words:
            words_pinyin.append(self.pinyinDict.decode(word))
        return words_pinyin

    def getNextChars(self, text):
        "text must be prefix of a word"
        nextChars = self.tree.getNextChars(text)

        # if in between two words or if word ends, add non-word chars
        if (text == '') or (self.isWord(text)):
            nextChars += self.getNonWordChars()

        return nextChars

    def getNextCharsPinyin(self, text):
        if type(text) is list and not isIntList(text):
            text = self.pinyinDict.encode(text)
        return self.pinyinDict.decode(self.getNextChars(text))

    def getWordChars(self):
        return self.wordChars

    def getNonWordChars(self):
        return self.nonWordChars

    def getNonWordCharsPinyin(self):
        return self.pinyinDict.decode(self.nonWordChars)

    def getAllChars(self):
        return self.allChars

    def getAllCharsPinyin(self):
        chars = self.getAllChars()
        return self.pinyinDict.decode(chars)

    def isWord(self, text):
        if not isIntList(text):
            text = self.pinyinDict.encode(text)
        return self.tree.isWord(text)

    def getUnigramProb(self, w):
        "prob of seeing word w."
        if type(w) is list and not isIntList(w):
            w = self.pinyinDict.encode(w)
        val = self.unigrams.get(w)
        if val != None:
            return val
        return 0

    def getBigramProb(self, w1, w2):
        "prob of seeing words w1 w2 next to each other."
        val1 = self.bigrams.get(w1)
        if val1 != None:
            val2 = val1.get(w2)
            if val2 != None:
                return val2
            return self.addK / (self.getUnigramProb(w1) * self.numUniqueWords + self.numUniqueWords)
        return 0

    def getBigramProbPinyin(self, w1, w2):
        w1 = self.pinyinDict.encode(w1)
        w2 = self.pinyinDict.encode(w2)
        return self.getBigramProb(w1, w2)

if __name__ == '__main__':
    import io

    dictfile = io.StringIO('''
 
,
.
:
0
1
2
3
4
5
6
7
8
9''')
    pinyinDict = PinyinDict(dictfile)
    lm = LanguageModel(
        '''
1 2#1#1 3#1 2#1 5#2 3 4
2 5 2 6
''',
        pinyinDict,
        '''
 
,
.
:'''
    )
    prefix = ['1']
    print('getNextChars:', lm.getNextCharsPinyin(prefix))
    print('getNonWordChars:', lm.getNonWordCharsPinyin())
    print('getNextWordsPinyin:', lm.getNextWordsPinyin(prefix))
    print('isWord:', lm.isWord(prefix))
    print('getBigramProb:', lm.getBigramProbPinyin(['1', '2'], ['1', '5']))
