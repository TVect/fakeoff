# -*- coding: utf-8 -*-


import sys
import string
import preprocess
import codecs

forward_dict = {}
backward_dict = {}


def genDict(path):
    """ 获取词典 """
    f = codecs.open(path,'r','utf-8')
    contents = f.read()
    contents = contents.replace(u'\r', u'')
    contents = contents.replace(u'\n', u'')
    # 将文件内容按空格分开
    mydict = contents.split(u' ')
    # 去除词典List中的重复
    newdict = list(set(mydict) - set([u'']))
#     newdict.remove(u'')

    # 建立词典
    # key为词首字，value为以此字开始的词构成的List
#     truedict = {}
    global forward_dict
    # key为词尾字，value为以此字结尾的词构成的List
#     back_truedict = {}
    global backward_dict
    
    for item in newdict:
        if len(item)>0 and item[0] in forward_dict:
            forward_dict[item[0]].append(item)
        else:
            forward_dict[item[0]] = [item]
        
        if len(item) > 0 and item[-1] in backward_dict:
            backward_dict[item[-1]].append(item)
        else:
            backward_dict[item[-1]] = [item]



def forward_divideWords(sentence):
    """
    根据词典对句子进行分词,
    使用正向匹配的算法，从左到右扫描，遇到最长的词，
    就将它切下来，直到句子被分割完闭
    """
    result = []
    start = 0
    sentence = "".join(sentence)
    senlen = len(sentence)
    global forward_dict
    while start < senlen:
        curword = sentence[start]
        maxlen = 1
        # 首先查看是否可以匹配特殊规则
        if (curword in preprocess.numCn) or \
            (curword in preprocess.numMath) or \
            (curword in string.letters):
            maxlen = preprocess.rules(sentence, start)
        # 寻找以当前字开头的最长词
        if curword in forward_dict:
            words = forward_dict[curword]
            for item in words:
                itemlen = len(item)
                if sentence[start:start+itemlen] == item and itemlen > maxlen:
                    maxlen = itemlen
        result.append("".join(sentence[start:start+maxlen]))
        start = start + maxlen
    return result


def backward_divideWords(sentence):
    result = []
    sentence = "".join(sentence)
    senlen = len(sentence)
    end = senlen-1
    global backward_dict
    while end >= 0:
        curword = sentence[end]
        maxlen = 1
        # 首先查看是否可以匹配特殊规则
        if (curword in preprocess.numCn) or (curword in preprocess.numMath) or \
            (curword in preprocess.numMath_suffix) or (curword in preprocess.numCn_suffix_date) or \
            (curword in preprocess.numCn_suffix_unit) or \
            (curword in string.letters):
            rule_max = preprocess.back_rules(sentence, end) 
            if rule_max > maxlen:
                maxlen = rule_max
        # 寻找以当前字结尾的最长词
        if curword in backward_dict:
            if curword == '2':
                break
            words = backward_dict[curword]
            for item in words:
                itemlen = len(item)
                if sentence[end-itemlen+1:end+1] == item and itemlen > maxlen:
                    maxlen = itemlen
        result.insert(0, "".join(sentence[end-maxlen+1:end+1]))
        end = end - maxlen
    return result



def main():
    dict_path = "./data/pku_training.utf8"
    test_path = "./data/test.utf8"
    result_path = "./data/result.utf8"

    genDict(dict_path)

    for sent in preprocess.sentence_words_iter(test_path):
        print "".join(sent)
        forward_list = forward_divideWords(sent)
        backward_list = backward_divideWords(sent)
        if forward_list != backward_list:
            print "/".join(forward_list)
            print "/".join(backward_list)


if __name__ == "__main__":
    main()

#     dict_path = "./data/pku_training.utf8"
#     forward_dicts, backward_dicts = genDict(dict_path)
#     backward_list = back_divideWords(backward_dicts, u"2001年新年钟声即将敲响。")
#     forward_list = divideWords(forward_dicts, u"2001年新年钟声即将敲响。")
#     print forward_list == backward_list
