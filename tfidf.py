# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from collections import defaultdict
from math import sqrt
import re
from janome.tokenizer import Tokenizer
import nltk
import codecs
from subprocess import PIPE, Popen
import yaml


class TFIDF(object):
    _t = None

    @classmethod
    def gen(cls, text, enable_one_char=False):
        """
        Get TF-IDF
        :param text: str
        :rtype :list[list[str, float]]
        """
        _text = cls.filter(text)
        return cls.analysis(_text, enable_one_char=enable_one_char)

    @classmethod
    def similarity(cls, tfidf1, tfidf2):
        """
        Get TF-IDF and Cosine Similarity
        cosθ = A・B/|A||B|
        :param tfidf1: list[list[str, float]]
        :param tfidf2: list[list[str, float]]
        :rtype : float
        """
        tfidf2_dict = {key: value for key, value in tfidf2}

        ab = 0  # A・B
        for key, value in tfidf1:
            value2 = tfidf2_dict.get(key)
            if value2:
                ab += float(value * value2)

        # |A| and |B|
        a = sqrt(sum([v ** 2 for k, v in tfidf1]))
        b = sqrt(sum([v ** 2 for k, v in tfidf2]))

        return float(ab / (a * b))

    @classmethod
    def some_similarity(cls, base_url, data):
        """
        :param base_url: str
        :param data: list[lost[str, str]]
        :rtype : list[lost[str, str, float]]
        """
        base_tfidf = cls.gen_web(base_url)
        return [[title, url, cls.similarity(base_tfidf, cls.gen_web(url))] for title, url in data]

    @classmethod
    def analysis(cls, text, enable_one_char):
        """
        Calc TF-IDF
        textを形態素解析して名詞の数を返却(Morphological Analysis)
        :param text: str
        :rtype : dict{str: int}
        """
        result = defaultdict(int)
        result2 = {}
        count = 0
        t = cls._get_tokenizer()

        # 形態素解析
        for token in t.tokenize(text):
            if '名詞' not in token.part_of_speech:
                continue
            count += 1

            if '非自立' in token.part_of_speech:
                continue

            if '代名詞' in token.part_of_speech:
                continue

            if '接尾' in token.part_of_speech:
                continue

            if '数' in token.part_of_speech:
                continue

            if not enable_one_char:
                if len(token.surface) == 1:
                    continue

            result[token.surface] += 1
            result2[token.surface] = token

        # TF-IDF計算
        result3 = []
        for key in result:
            result3.append([key, result[key]])

        result3.sort(key=lambda x: x[1], reverse=True)
        result4 = []
        for r in result3[:100]:
            result4.append([r[0], float(float(r[1])/float(count))])
        return result4

    @classmethod
    def filter(cls, text):
        """
        textをフィルターしてノイズを排除する
        :param text: str
        :rtype : str
        """
        # アルファベットと半角英数と改行とタブを排除
        text = re.sub(r'[a-zA-Z0-9¥"¥.¥,¥@]+', b'', text)
        text = re.sub(r'[!"“#$%&()\*\+\-\.,\/:;<=>?@\[\\\]^_`{|}~]', b'', text)
        text = re.sub(r'[\n|\r|\t|年|月|日]', b'', text)
        return text

    @classmethod
    def _get_tokenizer(cls):
        if TFIDF._t is not None:
            return TFIDF._t
        TFIDF._t = Tokenizer()
        return TFIDF._t


def cmdline(command):
    """
    コマンドを実行する。shell=Trueの場合シェル経由で実行する。
    :param command: str
    :return: Popen
    """
    return Popen(
        args=command,
        stdout=PIPE,
        stderr=PIPE,
        shell=True
    )


def file_read(filepath):
    with codecs.open(filepath, mode='r', encoding='utf8') as f:
        body = b''
        for x in f.readlines():
            body += x
    return body


def file_writer(filepath, body):
    with codecs.open(filepath, mode='a', encoding='utf8') as fw:
        fw.write(body)


def main():
    path_output = './tfidf.txt'
    _next = 'N2335DE.txt'

    # 銀河鉄道の夜
    if not _next:
        path_night_of_milky_way_train = './data/ao2/3.txt'
        body_night_of_milky_way_train = file_read(path_night_of_milky_way_train)
        tfidf_night_of_milky_way_train = TFIDF.gen(body_night_of_milky_way_train)
        file_writer(path_output, yaml.dump({str('ginga'): tfidf_night_of_milky_way_train}))

    # novels read
    novels = cmdline('ls -1 ./narou_data/novel/').stdout.readlines()
    _exec = False
    for i, novel_filename in enumerate(novels):
        novel_filename = novel_filename.replace('\r\n', '').replace('\n', '')
        if _exec is False:
            print novel_filename, _next, novel_filename == _next
            if novel_filename == _next:
                _exec = True
            continue

        novel_path = './narou_data/novel/' + novel_filename
        novel_body = file_read(novel_path)
        novel_tfidf = TFIDF.gen(novel_body)
        file_writer(path_output, yaml.dump({str(novel_filename): novel_tfidf}))
        print "[+]success {}: {}".format(str(i), novel_filename)

if __name__ == '__main__':
    main()

