# -*- coding: utf-8 -*-

'''
Created on 2016-8-19

@author: chin
'''

import codecs

def main():
    filename = "../training.utf8"
    with codecs.open(filename, "r", encoding="utf-8") as fr:
        for line in fr:
            line = line.strip()
            for wd in line.split():
                if len(wd) == 1:
                    print("%s %s S\n" % (wd[0], judge_type(wd)))
                elif len(wd) == 2:
                    print("%s %s B\n" % (wd[0], judge_type(wd)))
                    for i in range(1, -1):
                        print("%s %s M\n" % (wd[i], judge_type(wd)))
                    print("%s %s E\n" % (wd[-1], judge_type(wd)))
                

if __name__ == "__main__":
    main()
 