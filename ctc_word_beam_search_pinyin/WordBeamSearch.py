from __future__ import print_function
from __future__ import division

from ctc_word_beam_search_pinyin.LanguageModel import LanguageModel

from ctc_word_beam_search_pinyin.Beam import Beam, BeamList
import numpy as np

from ctc_word_beam_search_pinyin.file_dict import PinyinDict

def wordBeamSearch(mat, beamWidth, lm, useNGrams):
    "decode matrix, use given beam width and language model"
    chars = lm.getAllChars()
    # blankIdx = len(chars)  # blank label is supposed to be last label in RNN output
    blankIdx = len(chars) - 1
    maxT, _ = mat.shape  # shape of RNN output: TxC

    genesisBeam = Beam(lm, useNGrams, blankIdx)  # empty string
    last = BeamList()  # list of beams at time-step before beginning of RNN output
    last.addBeam(genesisBeam)  # start with genesis beam

    # go over all time-steps
    for t in range(maxT):
        curr = BeamList()  # list of beams at current time-step

        # go over best beams
        bestBeams = last.getBestBeams(beamWidth)  # get best beams
        for beam in bestBeams:
            # calc probability that beam ends with non-blank
            prNonBlank = 0
            if not beam.isTextEmptyOrAllCtcBlank():
                # char at time-step t must also occur at t-1
                labelIdx = chars.index(beam.getText()[-1])
                prNonBlank = beam.getPrNonBlank() * mat[t, labelIdx]

            # calc probability that beam ends with blank
            prBlank = beam.getPrTotal() * mat[t, blankIdx]

            # save result
            # TODO fix use 1420 for '' of original code
            curr.addBeam(beam.createChildBeam(blankIdx, prBlank, prNonBlank))

            # extend current beam with characters according to language model
            nextChars = beam.getNextChars()
            for c in nextChars:
                # extend current beam with new character
                labelIdx = chars.index(c)
                if not beam.isTextEmptyOrAllCtcBlank and beam.getText()[-1] == c:
                    prNonBlank = mat[t, labelIdx] * beam.getPrBlank()  # same chars must be separated by blank
                else:
                    prNonBlank = mat[t, labelIdx] * beam.getPrTotal()  # different chars can be neighbours

                # save result
                curr.addBeam(beam.createChildBeam(c, 0, prNonBlank))

        # move current beams to next time-step
        last = curr

    # return most probable beam
    last.completeBeams(lm)
    bestBeams = last.getBestBeams(1)  # sort by probability
    return bestBeams[0].getText()


if __name__ == '__main__':
    import io

    dictfile = io.StringIO('''
a
b
 
''')
    pinyinDict = PinyinDict(dictfile)
    testLM = LanguageModel(
        '''
a#b#a a#a b#b a#b b
''',
        pinyinDict,
        '''_''')
    # matrix [a, b, _, CTC-blank]
    testMat = np.array([[0.3, 0.1, 0, 0.6], [0.3, 0.1, 0, 0.6]])
    testBW = 25
    res = wordBeamSearch(testMat, testBW, testLM, False)
    print('Result: "' + ' '.join(pinyinDict.decode(res)) + '"')
