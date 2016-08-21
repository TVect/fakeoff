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

ENG_LABEL = "EngLabel"  # 特殊标记


class HiddenMarkovModel(object):
    def __init__(self):
        self.p_trans = None
        self.p_emission = None
        self.p_start = None

        self.wd_dict = {}   # wd -- wd_id
        self.wd_list = []   # wd_id -- wd


    def training(self, filename):
#         with open(filename) as fr:
#             for line in fr:
#                 for wd in line.decode("utf-8"):
#                     if wd not in self.wd_list:
#                         self.wd_dict[wd] = len(self.wd_list)
#                         self.wd_list.append(wd)
        with codecs.open(filename, "r", "utf-8") as fr:
            for line in fr:
                for wd in line:
                    if wd not in self.wd_list:
                        self.wd_dict[wd] = len(self.wd_list)
                        self.wd_list.append(wd)

        # Add a special label
        self.wd_dict[ENG_LABEL] = len(self.wd_list)
        self.wd_list.append(ENG_LABEL)

        self.p_trans = np.zeros((4,4))
        self.p_emission = np.ones((4, len(self.wd_list)))
        self.p_start = np.zeros(4)

        for sent in preprocess.sentence_terms_iter(filename):
            last_label = None
            if sent:
                for term in sent:
                    if preprocess.is_english(term):    # 处理英文, 把英文单词当做S来标记
                        self.p_emission[LABEL_ID['S']][self.wd_dict[ENG_LABEL]] += 1
                        if last_label:
                            self.p_trans[LABEL_ID[last_label]][LABEL_ID['S']] += 1
                        else:
                            self.p_start[LABEL_ID['S']] += 1
                        last_label = 'S'
                    elif len(term) == 1:
                        self.p_emission[LABEL_ID['S']][self.wd_dict[term[0]]] += 1
                        if last_label:
                            self.p_trans[LABEL_ID[last_label]][LABEL_ID['S']] += 1
                        else:
                            self.p_start[LABEL_ID['S']] += 1
                        last_label = 'S'
                    elif len(term) >= 2:
                        self.p_emission[LABEL_ID['B']][self.wd_dict[term[0]]] += 1
                        if last_label:
                            self.p_trans[LABEL_ID[last_label]][LABEL_ID['B']] += 1
                        else:
                            self.p_start[LABEL_ID['B']] += 1
                        last_label = 'B'

                        for i in range(1, len(term)-1):
                            self.p_emission[LABEL_ID['M']][self.wd_dict[term[i]]] += 1
                            self.p_trans[LABEL_ID[last_label]][LABEL_ID['M']] += 1
                            last_label = 'M'
                        
                        self.p_emission[LABEL_ID['E']][self.wd_dict[term[-1]]] += 1
                        self.p_trans[LABEL_ID[last_label]][LABEL_ID['E']] += 1
                        last_label = 'E'

        # normlization
        self.p_start = self.p_start / np.sum(self.p_start)
        self.p_trans = self.p_trans / np.sum(self.p_trans, axis=1)[:, np.newaxis]
        self.p_emission = self.p_emission / np.sum(self.p_emission, axis=1)[:, np.newaxis]
        self.p_emission[:, self.wd_dict[ENG_LABEL]] = [0.0, 0.0, 0.0, 1.0]
#         print self.p_start
#         print self.p_trans
#         print self.p_emission.sum(axis=1)


    def segment_s(self, sentence):
        '''
        segment a sentence
        '''
        if len(sentence) == 1:
            return sentence
        
        # TODO 对未在词典中出现的字的处理
        simu_emission = np.ones_like(self.p_start)

        best_forward = np.zeros((len(self.p_start), len(sentence)))
        if preprocess.is_english(sentence[0]):
            forward_prob = np.array(self.p_start * self.p_emission[:, self.wd_dict[ENG_LABEL]])
        elif sentence[0] in self.wd_list:
            forward_prob = np.array(self.p_start * self.p_emission[:, self.wd_dict[sentence[0]]])
        else:
            forward_prob = np.array(self.p_start * simu_emission)
        
        for wd_ix in range(1, len(sentence)):
            if preprocess.is_english(sentence[wd_ix]):
                tmp_prob = np.dot(np.dot(np.diag(forward_prob), self.p_trans), 
                                  np.diag(self.p_emission[:, self.wd_dict[ENG_LABEL]]))
            elif sentence[wd_ix] in self.wd_dict:
                tmp_prob = np.dot(np.dot(np.diag(forward_prob), self.p_trans), 
                                  np.diag(self.p_emission[:, self.wd_dict[sentence[wd_ix]]]))
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
        pass



if __name__ == "__main__":
    hmm = HiddenMarkovModel()
    print "training..."
    hmm.training("data/pku_training.utf8")
    print "segment..."
#     hmm.segment_f("../../icwb2-data/testing/pku_test.utf8", "pku_result.utf8")

#     print "training..."
#     hmm.training("../../icwb2-data/training/msr_training.utf8")
#     print "segment..."
#     hmm.segment_f("../../icwb2-data/testing/msr_test.utf8", "../msr_result.utf8")

#     hmm.training("training.utf8")
#     hmm.segment_f("test.utf8", "result.utf8")
    print "/".join(hmm.segment_s(list(u'人类社会前进的航船就要驶入') + ['21'] + list(u'世纪的新航程。')))

#     for sent in hmm._split_to_words(u'江泽民'):
#         print sent


