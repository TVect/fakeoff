# -*- coding: utf-8 -*-


import codecs
import string
import re


# 由规则处理的一些特殊符号
numMath = [u'0', u'1', u'2', u'3', u'4', u'5', u'6', u'7', u'8', u'9']
numMath_suffix = [u'.', u'%', u'亿', u'万', u'千', u'百', u'十', u'个']
numCn = [u'一', u'二', u'三', u'四', u'五', u'六', u'七', u'八', u'九', u'十', u'〇', u'零', u'○']
numCn_suffix_date = [u'年', u'月', u'日']
numCn_suffix_unit = [u'亿', u'万', u'千', u'百', u'十', u'个']
special_char = [u'(', u')']


def proc_num_math(line, start):
    """ 处理句子中出现的数学符号 """
    oldstart = start
    line_size = len(line)
    while line[start] in numMath or line[start] in numMath_suffix:
        start = start + 1
        if start >= line_size:
            break
    else:
        if line[start] in numCn_suffix_date:
            start = start + 1
    return start - oldstart


def proc_num_cn(line, start):
    """ 处理句子中出现的中文数字 """
    oldstart = start
    line_size = len(line)
    while line[start] in numCn or line[start] in numCn_suffix_unit:
        start = start + 1
        if start >= line_size:
            break
    else:
        if line[start] in numCn_suffix_date:
            start = start + 1
    return start - oldstart


def rules(line, start):
    """正向匹配特殊规则"""
    if line[start] in numMath:
        return proc_num_math(line, start)
    elif line[start] in numCn:
        return proc_num_cn(line, start)
    elif line[start] in string.letters:
        i = start
        while (i < len(line)) and (line[i] in string.letters): 
            i += 1
        return i-start
    return 0


def back_rules(line, end):
    cnt = 0
    for i in range(end-1, -1, -1):
        if rules(line[:end+1], i) == 0:
            return rules(line[:end+1], i+1)
    return end+1


pattern = re.compile(r"^\w+$")
def is_english(term):
    if pattern.match(term):
        return True
    return False




PUNC = u'。，？！、：“”《》（）；'
BEGIN_PUNC = u'“《（'
END_PUNC = u'。，？！、：”》）；'


def sentence_terms_iter(filename):
    '''
    @return: iter to return ['t1t2', 't3t4' ...]
    '''
    with codecs.open(filename, "r", encoding="utf-8") as fr:
        for line in fr:
            line = line.strip()
            sent = []
            i_pos = 0
            for i in xrange(len(line)):
                if line[i] in END_PUNC: 
                    sent = line[i_pos:i+1]
                    i_pos = i+1
                    if sent: yield sent.split()
                    sent = []
            if i_pos < len(line): 
                sent = line[i_pos:]
            if sent: yield sent.split()


def sentence_words_iter(filename):
    '''
    @return: iter to return ['word1', 'word2' ...]
    '''
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

            if i_pos < len(line): 
                sent.append(line[i_pos:])
            if sent: yield sent
            yield "\n"



if __name__ == "__main__":
    x = u"一九九九年中国Hello你好一九九九年年123年"
    print back_rules(x, 0)
    print is_english("123")



