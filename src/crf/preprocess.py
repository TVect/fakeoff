# -*- coding: utf-8 -*-

'''
Created on 2016-8-19

@author: chin
'''

import codecs


PUNC = u'。，？！、：“”《》（）；'
BEGIN_PUNC = u'“《（'
END_PUNC = u'。，？！、：”》）；'


def doc_to_sentence_iter(filename):
    with codecs.open(filename, "r", encoding="utf-8") as fr:
        for line in fr:
            line = line.strip()
            sent = []
            i_pos = 0
            for i in xrange(len(line)):
                if line[i].isspace():
                    if i > i_pos:
                        sent.append(line[i_pos:i])
                    i_pos = i+1
                elif u'\u4e00' <= line[i] <= u'\u9fa5':
                    if i > i_pos:
                        sent.append(line[i_pos:i])
                    sent.append(line[i])
                    i_pos = i+1
                elif line[i] in PUNC:
                    if i > i_pos:
                        sent.append(line[i_pos:i])
                    if line[i] in END_PUNC: 
                        sent.append(line[i])
                        i_pos = i+1
                    if sent: yield sent
                    sent = []
#                 elif line[i] in PUNC:
#                     if i > i_pos:
#                         sent.append(line[i_pos:i])
#                     sent.append(line[i])
#                     i_pos = i+1
#                     yield sent
#                     sent = []
            if i_pos < len(line): 
                sent.append(line[i_pos:])
            if sent: yield sent



if __name__ == "__main__":
    filename = "../training.utf8"
    for sent in doc_to_sentence_iter(filename):
        print "/".join(sent)
