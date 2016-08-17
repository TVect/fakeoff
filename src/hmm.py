# -*- coding: utf-8 -*-

'''
Created on 2016-8-16

@author: chin
'''

import numpy as np
import re
import codecs


LABEL_ID = {'B': 0, 'M':1, 'E':2, 'S':3}

class HiddenMarkovModel(object):
    def __init__(self):
        self.p_trans = None
        self.p_emission = None
        self.p_start = None

        self.wd_dict = {}   # wd -- wd_id
        self.wd_list = []   # wd_id -- wd


    def training(self, filename):
        '''
        从分词的文件中学习到hmm的参数
        '''
        with open(filename) as fr:
            for line in fr:
                for wd in line.decode("utf-8"):
                    if wd not in self.wd_list:
                        self.wd_dict[wd] = len(self.wd_list)
                        self.wd_list.append(wd)

#             self.p_trans = np.zeros((4,4))
#             self.p_emission = np.zeros((4, len(self.wd_list)))
#             self.p_start = np.zeros(4)

            self.p_trans = np.ones((4,4))
            self.p_emission = np.ones((4, len(self.wd_list)))
            self.p_start = np.ones(4)

            fr.seek(0)
            last_label = None
            for line in fr:
                for wd in line.decode("utf-8").split():
                    wd = wd.strip()
                    if len(wd) == 1:
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


    def segment_s(self, sentence):
        '''
        利用hmm进行分词标注
        '''
        if len(sentence) == 1:
            return [sentence, '\t']
        # TODO 对未在词典中出现的字的处理
        simu_emission = np.array([1.0 / len(self.p_start)] * len(self.p_start))
        
        best_forward = np.zeros((len(self.p_start), len(sentence)))
        if sentence[0] in self.wd_dict:
            forward_prob = np.array(self.p_start * self.p_emission[:, self.wd_dict[sentence[0]]])
        else:
            forward_prob = np.array(self.p_start * simu_emission)

        for wd_ix in range(1, len(sentence)):
            if sentence[wd_ix] in self.wd_dict:
                tmp_prob = np.dot(np.dot(np.diag(forward_prob), self.p_trans), np.diag(self.p_emission[:, self.wd_dict[sentence[wd_ix]]]))
            else:
                tmp_prob = np.dot(np.dot(np.diag(forward_prob), self.p_trans), np.diag(simu_emission))

            best_forward[:, wd_ix] = np.argmax(tmp_prob, axis=0)
            forward_prob = np.max(tmp_prob, axis=0)
#         print "best_forward", best_forward
#         print "forward_prob", forward_prob
        label_ids = [np.argmax(forward_prob)]
        for i in range(len(sentence))[:0:-1]:
            label_ids.insert(0, best_forward[:, i][label_ids[0]])

        segmented_sentence = []
        for i in range(len(sentence)):
            segmented_sentence.append(sentence[i])
            if label_ids[i] in [LABEL_ID['E'], LABEL_ID['S']]:
                segmented_sentence.append("\t")
#         if forward_prob == 0:
#             break
        if np.array_equal(forward_prob, np.zeros(4)):
            print "ZERO:", sentence
        return segmented_sentence



#     def segment_f(self, in_filename, out_filename):
#         pattern = re.compile(ur'.+?[？。，！：\s]+')
#         with open(in_filename) as fr:
# #             with open(out_filename, "w") as fw:
#             with codecs.open(out_filename,'w','utf-8') as fw:
#                 for line in fr:
#                     line = line.decode("utf-8").strip()
#                     if not line:
#                         break
#                     seg = pattern.findall(line)
#                     if seg:
#                         for single_line in seg:
#                             fw.write("".join(self.segment_s(single_line.strip())))
#                             fw.write("\t")
#                     else:
#                         fw.write("".join(self.segment_s(line)))
#                         fw.write("\t")
#                     fw.write("\n")


    def segment_f(self, in_filename, out_filename):
        with open(in_filename) as fr:
            with codecs.open(out_filename,'w','utf-8') as fw:
                for line in fr:
                    line = line.decode("utf-8").strip()
                    if not line:
                        break

                    sents = self._split_to_sentence(line)
                    for sent in sents:
                        if len(sent):
                            fw.write("".join(self.segment_s(sent.strip())))
                            fw.write("\t")
                    fw.write("\n")


    def _is_chinese(self, wd):
        return u'\u4e00' <= wd <= u'\u9fa5'

    def _is_punctuation(self, in_char):
        if self._is_chinese(in_char):
            return False
        else:
            if in_char.isdigit() or in_char.isalpha():
                return False
            return True
    
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
            if self._judge_type(line[i]) != self._judge_type(line[i-1]):
                sents.append(line[last_pt:i])
                last_pt = i
        sents.append(line[last_pt:])
        return sents


if __name__ == "__main__":
    hmm = HiddenMarkovModel()
    print "training..."
    hmm.training("../icwb2-data/training/pku_training.utf8")
#     print "segment..."
#     hmm.segment_f("../icwb2-data/testing/pku_test.utf8", "pku_result.utf8")

#     hmm.training("test.utf8")
#     hmm.segment_f("tmp.utf8", "result.utf8")
    print "".join(hmm.segment_s(u'新华社北京12月31日电'))

#     for sent in hmm._split_to_sentence(u"2000年'十二月'三--十一日"):
#         print sent

    
