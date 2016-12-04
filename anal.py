# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from collections import defaultdict
from math import sqrt
import re
from janome.tokenizer import Tokenizer
import nltk
import codecs


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
        goi_counter = 0
        goi_dict = defaultdict(int)
        for token in t.tokenize(text):
            if cls.goi_filter(token):
                goi_counter += 1
                goi_dict[token.surface] += 1

            if '名詞' not in token.part_of_speech:
                continue
            count += 1
            goi_counter += 1

            if '非自立' in token.part_of_speech:
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

        print "語彙力:{} / {}".format(float(len(goi_dict.keys())) / float(goi_counter), goi_counter)
        # TF-IDF計算
        result3 = []
        for key in result:
            result3.append([key, result[key]])

        result3.sort(key=lambda x: x[1], reverse=True)
        result4 = []
        for r in result3[:100]:
            # print r[0], float(float(r[1])/float(count)), result2[r[0]]
            result4.append([r[0], float(float(r[1])/float(count))])
        return result4

    @classmethod
    def goi_filter(cls, token):
        """
        形容詞 副詞
        :param token:
        :return:
        """
        for ng in ['名詞', '非自立', '助詞類接続', '助詞']:
            if ng in token.part_of_speech:
                return False

        if '形容詞' in token.part_of_speech:
            return True

        if '副詞' in token.part_of_speech:
            return True
        return False


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

        # 日本語以外の文字を排除(韓国語とか中国語とかヘブライ語とか)
        jp_chartype_tokenizer = nltk.RegexpTokenizer(r'([ぁ-んー]+|[ァ-ンー]+|[\u4e00-\u9FFF]+|[ぁ-んァ-ンー\u4e00-\u9FFF]+)')
        text = ''.join(jp_chartype_tokenizer.tokenize(text))
        return text

    @classmethod
    def _get_tokenizer(cls):
        if TFIDF._t is not None:
            return TFIDF._t
        TFIDF._t = Tokenizer()
        return TFIDF._t


def main():
    novel_keys = [
        'N6316BN.txt',
        'N9669BK.txt',
        'N8802BQ.txt',
        'N7975CR.txt',
        'N6768BF.txt',
        'N7031BS.txt',
        'N3726BT.txt',
    ]
    novels_path = ["./narou_data/novel/{}".format(x) for x in novel_keys]

    for i in range(0, len(novel_keys)):
        with codecs.open(novels_path[i], mode='r', encoding='utf8') as f:
            print "-----------------"
            body = b''
            for x in f.readlines():
                body += x
            print len(body), novels_path[i]
            tfidf = TFIDF.gen(body)

if __name__ == '__main__':
    main()
