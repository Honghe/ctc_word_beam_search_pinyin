from __future__ import print_function
from __future__ import division
import editdistance

from .Metrics import Metrics
from .DataLoader import DataLoader
from .WordBeamSearch import wordBeamSearch

# Settings
from .file_dict import PinyinDict

sampleEach = 1
dataset = 'nlp_ctc_word_beam_search_pinyin'
useNGrams = False

# main
if __name__ == '__main__':

    # load dataset
    pinyinDict = PinyinDict('dict.txt')
    loader = DataLoader(dataset, pinyinDict, sampleEach)
    print('Decoding ' + str(loader.getNumSamples()) + ' samples now.')
    print('')

    # TODO
    # metrics calculates CER and WER for dataset
    m = Metrics(loader.lm.getWordChars())

    # write results to csv
    # csv = Utils.CSVWriter()

    # decode each sample from dataset
    for (idx, data) in enumerate(loader):
        # decode matrix
        # TODO useNGrams=True even bad performance
        res = wordBeamSearch(data.mat, 10, loader.lm, useNGrams)
        print('Sample: ' + str(idx + 1))
        print('Filenames: ' + data.fn)
        print('Result:       "' + ' '.join(pinyinDict.decode(res)) + '"')
        print('Ground Truth: "' + data.gt + '"')
        data_gt_splited = pinyinDict.encode(data.gt.split())
        res_clean = [i for i in res if i != len(pinyinDict.pinyinMap())-1]
        strEditDist = str(editdistance.eval(res_clean, data_gt_splited))
        print('Editdistance: ' + strEditDist)

        # output CER and WER
        m.addSample(data_gt_splited, res_clean)
        print('Accumulated CER and WER so far: CER: {:.3f} WER: {:.3f}'.format(m.getCER(), m.getWER()))

        # output to csv
        # csv.write([res, data.gt, strEditDist])

