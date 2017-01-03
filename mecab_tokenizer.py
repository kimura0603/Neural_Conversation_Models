# -*- coding: utf-8 -*-
import MeCab

mt = MeCab.Tagger("mecabrc")

def mecab_tokenizer(sentence):

    res = mt.parseToNode(sentence)

    out = []
    while res:
        s = res.surface
        if s:
            out.append(s)
        res = res.next
    return out

