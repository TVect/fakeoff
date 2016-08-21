# -*- coding:utf-8 -*-

import codecs

import preprocess
import dw2
import dw_hmm

dict_path = "./data/as_training.utf8"
test_path = "./data/as_test.utf8"
result_path = "./data/as_result.utf8"

dw2.genDict(dict_path)

hmm_method = dw_hmm.HiddenMarkovModel()
print "hmm_method training..."
hmm_method.training(dict_path)

with codecs.open(result_path, "w", "utf-8") as fw:
    for sent in preprocess.sentence_words_iter(test_path):
    #     print "".join(sent)
        forward_list = dw2.forward_divideWords(sent)
    #     print "/".join(forward_list)
        backward_list = dw2.backward_divideWords(sent)
    #     print "/".join(backward_list)    
        if forward_list != backward_list:
            seg = hmm_method.segment_s(sent)
#             print "/".join(seg)
            fw.write("    ".join(seg))
        else:
            fw.write("    ".join(forward_list))
        fw.write("    ")
#         print "------------------------------------"
