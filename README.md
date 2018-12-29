# CTC Word Beam Search for Chinese Pinyin

For from https://github.com/githubharald/CTCWordBeamSearch

- CNN算法输出的matrix是基于拼音训练的模型。
- 给每个拼音/标点标号使用数字编码

## Demo
```
Sample: 1
Filenames: ./data/nlp_ctc_word_beam_search_pinyin/mat_0.csv|./data/nlp_ctc_word_beam_search_pinyin/gt_0.txt
Result:       "_ gei3 _ _ bian4 _ _ xiao3 _ _ jin3 _ _ jia1 _ shi4 _ _ fen1 _"
Ground Truth: "gei3 bian4 xiao3 jin3 jia1 si4 fen1"
Editdistance: 1
Accumulated CER and WER so far: CER: 0.143 WER: 0.143
```

## Build
```
python setup.py sdist bdist_wheel
```
The output .whl is in `dist` directory
