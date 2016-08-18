# -*- coding: utf-8 -*-

'''
Created on 2016-8-16

@author: chin
'''

import numpy as np
import re
import codecs
import preprocess

LABEL_ID = {'B': 0, 'M':1, 'E':2, 'S':3}

NUM_LABEL = "NumLabel"  # 特殊标记


class HiddenMarkovModel(object):
    def __init__(self):
        self.p_trans = None
        self.p_emission = None
        self.p_start = None

        self.wd_dict = {}   # wd -- wd_id
        self.wd_list = []   # wd_id -- wd


    def training(self, filename):
        with open(filename) as fr:
            for line in fr:
                for wd in line.decode("utf-8"):
                    if wd not in self.wd_list:
                        self.wd_dict[wd] = len(self.wd_list)
                        self.wd_list.append(wd)
            # Add a special label
            self.wd_dict[NUM_LABEL] = len(self.wd_list)
            self.wd_list.append(NUM_LABEL)

            self.p_trans = np.ones((4,4))
            self.p_emission = np.ones((4, len(self.wd_list)))
            self.p_start = np.ones(4)

            fr.seek(0)
            last_label = None
            for line in fr:
                for wd in line.decode("utf-8").split():
                    wd = wd.strip()
                    if preprocess.is_rules(wd) or (len(wd) == 1):
                        if preprocess.is_rules(wd):
                            wd = NUM_LABEL
                        self.p_emission[LABEL_ID['S']][self.wd_dict[wd]] += 1
                        if last_label:
                            self.p_trans[LABEL_ID[last_label]][LABEL_ID['S']] += 1
                        else:
                            self.p_start[LABEL_ID['S']] += 1
                        last_label = 'S'

                    elif len(wd) >= 2:
                        self.p_emission[LABEL_ID['B']][self.wd_dict[wd[0]]] += 1

                        if last_label:
                            self.p_trans[LABEL_ID[last_label]][LABEL_ID['B']] += 1
                        else:
                            self.p_start[LABEL_ID['B']] += 1
                        last_label = 'B'

                        for i in range(1, len(wd)-1):
                            self.p_emission[LABEL_ID['M']][self.wd_dict[wd[i]]] += 1
                            self.p_trans[LABEL_ID[last_label]][LABEL_ID['M']] += 1
                            last_label = 'M'
                        
                        self.p_emission[LABEL_ID['E']][self.wd_dict[wd[-1]]] += 1
                        self.p_trans[LABEL_ID[last_label]][LABEL_ID['E']] += 1
                        last_label = 'E'

                last_label = None
        # normlization
        self.p_start = self.p_start / np.sum(self.p_start)
        self.p_trans = self.p_trans / np.sum(self.p_trans, axis=1)[:, np.newaxis]
        self.p_emission = self.p_emission / np.sum(self.p_emission, axis=1)[:, np.newaxis]
        self.p_emission[:, self.wd_dict[NUM_LABEL]] = [0.0, 0.0, 0.0, 1.0]


    def segment_s(self, sentence):
        '''
        segment a sentence
        '''
        # TODO split sentence to words, we may treat some words like '2002' as a single word
        sentence = self._split_to_words(sentence)
        if len(sentence) == 1:
            return sentence

        # TODO 对未在词典中出现的字的处理
        simu_emission = np.array([1.0 / len(self.p_start)] * len(self.p_start))
        
        best_forward = np.zeros((len(self.p_start), len(sentence)))
        if preprocess.is_rules(sentence[0]):
            forward_prob = np.array(self.p_start * self.p_emission[:, self.wd_dict[NUM_LABEL]])
        elif sentence[0] in self.wd_list:
                forward_prob = np.array(self.p_start * self.p_emission[:, self.wd_dict[sentence[0]]])
        else:
            forward_prob = np.array(self.p_start * simu_emission)

        for wd_ix in range(1, len(sentence)):
            if preprocess.is_rules(sentence[wd_ix]):
                tmp_prob = np.dot(np.dot(np.diag(forward_prob), self.p_trans), np.diag(self.p_emission[:, self.wd_dict[NUM_LABEL]]))
            elif sentence[wd_ix] in self.wd_dict:
                tmp_prob = np.dot(np.dot(np.diag(forward_prob), self.p_trans), np.diag(self.p_emission[:, self.wd_dict[sentence[wd_ix]]]))
            else:
                tmp_prob = np.dot(np.dot(np.diag(forward_prob), self.p_trans), np.diag(simu_emission))

            best_forward[:, wd_ix] = np.argmax(tmp_prob, axis=0)
            forward_prob = np.max(tmp_prob, axis=0)
        label_ids = [np.argmax(forward_prob)]
        for i in range(len(sentence))[:0:-1]:
            label_ids.insert(0, best_forward[:, i][label_ids[0]])

        segmented_sentence = []
        i_pos = 0
        for i in range(len(sentence)):
            if label_ids[i] == LABEL_ID['S']:
                segmented_sentence.append(sentence[i])
            elif label_ids[i] == LABEL_ID['B']:
                i_pos = i
            elif label_ids[i] == LABEL_ID['E']:
                segmented_sentence.append("".join(sentence[i_pos:i+1]))
        if label_ids[-1] not in [LABEL_ID['S'], LABEL_ID['E']]:
            segmented_sentence.append("".join(sentence[i_pos:]))
        if np.array_equal(forward_prob, np.zeros(4)):
            print "ZERO:", "\t".join(sentence)

        return segmented_sentence


    def segment_f(self, in_filename, out_filename):
        '''
        segment a special file
        '''
        with open(in_filename) as fr:
            with codecs.open(out_filename,'w','utf-8') as fw:
                for line in fr:
                    line = line.decode("utf-8").strip()
                    if not line:
                        break

                    sents = self._split_to_sentence(line)
                    for sent in sents:
                        if len(sent):
                            fw.write("\t".join(self.segment_s(sent.strip())))
                            fw.write("\t")
                    fw.write("\n")

    
    def _judge_type(self, wd):
        if wd.isdigit():
            return "digit"
        elif wd.isalpha():
            return "alpha"
        elif u'\u4e00' <= wd <= u'\u9fa5':
            return "chinese"
        else:
            return "else"


    def _split_to_sentence(self, line, filter_digit_alpha=True):
        sents = []
        last_pt = 0
        for i in range(1, len(line)):
#             if self._judge_type(line[i]) != self._judge_type(line[i-1]):
#                 sents.append(line[last_pt:i])
#                 last_pt = i
            if line[i] in u'。，？！、：“”《》；':
                sents.append(line[last_pt:i+1])
                last_pt = i+1
        sents.append(line[last_pt:])
        return sents


    def _split_to_words(self, sentence):
        sent = []
        i_pos = 0
        while i_pos < len(sentence):
            cur_word = sentence[i_pos]
            if cur_word in preprocess.numCn or cur_word in preprocess.numMath:
                max_len = preprocess.rules(sentence, i_pos)
            else:
                max_len = 1
            sent.append(sentence[i_pos : i_pos+max_len])
            i_pos += max_len
        return sent


if __name__ == "__main__":
    hmm = HiddenMarkovModel()
#     print "training..."
#     hmm.training("../icwb2-data/training/pku_training.utf8")
#     print "segment..."
#     hmm.segment_f("../icwb2-data/testing/pku_test.utf8", "pku_result.utf8")

    print "training..."
    hmm.training("../icwb2-data/training/msr_training.utf8")
    print "segment..."
    hmm.segment_f("../icwb2-data/testing/msr_test.utf8", "msr_result.utf8")

#     hmm.training("training.utf8")
#     hmm.segment_f("test.utf8", "result.utf8")
#     print "\t".join(hmm.segment_s(u'江泽民'))

#     for sent in hmm._split_to_words(u'江泽民'):
#         print sent

    
