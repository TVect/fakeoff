# -*- coding: utf-8 -*-

'''
Created on 2016-8-18

@author: chin
'''

# 由规则处理的一些特殊符号
numMath = [u'0', u'1', u'2', u'3', u'4', u'5', u'6', u'7', u'8', u'9']
numMath_suffix = [u'.', u'%', u'亿', u'万', u'千', u'百', u'十', u'个']
numCn = [u'一', u'二', u'三', u'四', u'五', u'六', u'七', u'八', u'九', u'十', u'〇', u'零', u'o', u'○']
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
    """ 处理特殊规则 """
    if line[start] in numMath:
        return proc_num_math(line, start)
    elif line[start] in numCn:
        return proc_num_cn(line, start)

def is_rules(word):
    if rules(word, 0) == len(word):
        return True
    return False

if __name__ == "__main__":
    print is_rules(u"12月31日")
