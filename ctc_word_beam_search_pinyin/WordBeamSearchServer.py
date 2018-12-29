import io
import os

import numpy as np
import pkg_resources

from ctc_word_beam_search_pinyin.WordBeamSearch import wordBeamSearch
from ctc_word_beam_search_pinyin.file_dict import PinyinDict

from ctc_word_beam_search_pinyin.LanguageModel import LanguageModel


class WordBeamSearchServer:
    def __init__(self, dictfile=None, corpusfile=None):
        if dictfile:
            self.pinyinDict = PinyinDict(dictfile)
        else:
            self.pinyinDict = PinyinDict(pkg_resources.resource_filename(__name__, "dict.txt"))
        if corpusfile:
            self.corpus = open(corpusfile).read()
        else:
            self.corpus = open(
                pkg_resources.resource_filename(__name__, 'data/nlp_ctc_word_beam_search_pinyin/corpus.txt')).read()

        self.lm = LanguageModel(
            self.corpus,
            self.pinyinDict,
            '''''')

    def decode(self, mat):
        beamwidth = 25
        res = wordBeamSearch(mat, beamwidth, self.lm, False)
        blankIndex = len(self.pinyinDict.pinyinMap().keys()) - 1
        # delete blankIndex
        res = [i for i in res if i != blankIndex]

        return res


if __name__ == '__main__':
    mat = np.genfromtxt(
        open(pkg_resources.resource_filename(__name__, 'data/nlp_ctc_word_beam_search_pinyin/mat_0.csv')),
        delimiter=';')[:, :-1]
    wordBeamSearchServer = WordBeamSearchServer()
    r = wordBeamSearchServer.decode(mat)
    print(r)
