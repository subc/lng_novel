# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import codecs
import re


def main():
    p = ["./data/ao/{}.txt".format(x) for x in range(1, 11)]
    p2 = ["./data/ao2/{}.txt".format(x) for x in range(1, 11)]

    for i in range(0, 10):
        with codecs.open(p2[i], mode='w', encoding='utf8') as fw:
            with codecs.open(p[i], mode='r', encoding='shift_jis') as f:
                for x in f.readlines():
                    x = filter_j(x)
                    fw.write(x)


def filter_j(x):
    print x, type(x)
    x = re.sub(r'［.*］', "", x)
    x = re.sub(r'［＃.*］', "", x)
    x = re.sub(r'《.*》', "", x)
    return x


if __name__ == '__main__':
    main()
