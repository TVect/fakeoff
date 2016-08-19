# -*- coding: utf-8 -*-

'''
Created on 2016-8-19

@author: chin
'''

from optparse import OptionParser
import codecs
from pip._vendor.html5lib.ihatexml import digit

'''
Type:
    ch    中文字
    di    数字
    en    英文
    pu    标点
'''

class WordTypeEnum:
    CHINESE = 0
    DIGIT = 1
    ENGLISH = 2
    PUNCTUATION = 3
    ELSE = 4


numCn = [u'一', u'二', u'三', u'四', u'五', u'六', u'七', u'八', u'九', u'十', u'〇', u'零', u'○']

def judge_type(wd):
    if wd.isdigit() or (wd in numCn):
#         return WordTypeEnum.DIGIT
        return "di"
    elif u'\u4e00' <= wd <= u'\u9fa5':
#         return WordTypeEnum.CHINESE
        return "ch"
    elif wd.isalnum():
#         return WordTypeEnum.ENGLISH
        return "en"
    else:
#         return WordTypeEnum.PUNCTUATION
        return "pu"


def main():  
    usage = "usage: %prog [options] arg"  
    parser = OptionParser(usage)  
    parser.add_option("-i", "--infile", dest="infile", help="read data from FILENAME")  
    parser.add_option("-o", "--outfile", dest="outfile", help="write data to FILENAME")  
    (options, args) = parser.parse_args()

    infile = options.infile
    outfile = options.outfile
    if not infile:
        infile = "../training.utf8"

    with codecs.open(infile, "r", "utf-8") as fr:
        with codecs.open(outfile, "w", "utf-8") as fw:
            for line in fr:
                for wd in line.split():
                    wd = wd.strip()
                    if len(wd) == 1:
                        fw.write("%s %s S\r\n" % (wd[0], judge_type(wd)))
                    elif len(wd) >= 2:
                        fw.write("%s %s B\r\n" % (wd[0], judge_type(wd[0])))
                        for i in range(1, len(wd)-1):
                            fw.write("%s %s M\r\n" % (wd[i], judge_type(wd[i])))
                        fw.write("%s %s E\r\n" % (wd[-1], judge_type(wd[-1])))
                    if wd in u'。，？！、：”》）；':
                        fw.write("\r\n")

if __name__ == "__main__":
    main()
