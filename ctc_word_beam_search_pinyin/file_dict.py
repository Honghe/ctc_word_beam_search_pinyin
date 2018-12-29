#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
获取符号字典列表的
'''


class PinyinDict:
    def __init__(self, datapath):
        self.dict = self._genPinyinDict(datapath)

    def _genPinyinDict(self, datapath):
        '''
        加载拼音符号列表，用于标记符号
        返回一个列表list类型变量
        '''
        # if is not file
        if not hasattr(datapath, 'read'):
            txt_obj = open(datapath, 'r', encoding='UTF-8')  # 打开文件并读入
        else:
            txt_obj = datapath
        txt_text = txt_obj.read()
        txt_lines = txt_text.split('\n')  # 文本分割
        list_symbol = []  # 初始化符号列表
        for i, v in enumerate(txt_lines):
            if (v != ''):
                txt_l = v.split('\t')
                list_symbol.append(txt_l[0])
        txt_obj.close()
        # CTC-blank
        list_symbol.append('_')
        return {k: v for k,v in  enumerate(list_symbol)}

    def pinyinMap(self):
        '''
        id to pinyin
        :return:
        '''
        return self.dict

    def pinyinMapInverse(self):
        '''
        pinyin to id
        :return:
        '''
        d = {}
        for i, v in self.dict.items():
            d[v] = i
        return d

    def decode(self, ids):
        '''
        ids to text
        :param ids:
        :return:
        '''
        pinMap = self.pinyinMap()
        return [pinMap[i] for i in ids]

    def encode(self, text):
        '''
        text to ids
        :param text:
        :return:
        '''
        pinyinInverse = self.pinyinMapInverse()
        return [pinyinInverse[i] for i in text]

if __name__ == '__main__':
    pinyinDict = PinyinDict('dict.txt')
    pinyindi = pinyinDict.pinyinMapInverse()
    print('\n'.join(pinyindi.keys()))
