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
    #
    # @classmethod
    # def gen_web(cls, url, enable_one_char=False):
    #     """
    #     Get TF-IDF from url
    #     :param url: str
    #     :rtype: list[list[str, float]]
    #     """
    #     # HTTP GET
    #     response = requests.get(url)
    #
    #     # filter HTTP Tag
    #     soup = BeautifulSoup(response.text, "lxml")
    #     text = soup.title.name + soup.get_text()
    #     return cls.gen(text, enable_one_char=enable_one_char)

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
        k_counter = 0
        goi_dict = defaultdict(int)
        for token in t.tokenize(text):
            if cls.goi_filter(token):
                k_counter += 1
                goi_dict[token.surface] += 1

            if '名詞' not in token.part_of_speech:
                continue
            count += 1

            if '非自立' in token.part_of_speech:
                continue

            if '接尾' in token.part_of_speech:
                continue

            if '数' in token.part_of_speech:
                continue

            if not enable_one_char:
                if len(token.surface) == 1:
                    continue

            goi_counter += 1
            result[token.surface] += 1
            result2[token.surface] = token

        print "語彙力:{} / {}".format(float(len(goi_dict.keys())) / float(k_counter + count), goi_counter)
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
        # jp_chartype_tokenizer = nltk.RegexpTokenizer(r'([ぁ-んー]+|[ァ-ンー]+|[\u4e00-\u9FFF]+|[ぁ-んァ-ンー\u4e00-\u9FFF]+)')
        # print jp_chartype_tokenizer.tokenize("あいうえ hogehoge かきくけこ")
        # print jp_chartype_tokenizer.tokenize("あいうえかきくけ")
        # print ''.join(jp_chartype_tokenizer.tokenize("あいうえかきくけ"))
        # print text
        # print len(text)
        # print len(jp_chartype_tokenizer.tokenize(text))
        # text2 = ''.join(jp_chartype_tokenizer.tokenize(text))

        return text

    @classmethod
    def _get_tokenizer(cls):
        if TFIDF._t is not None:
            return TFIDF._t
        TFIDF._t = Tokenizer()
        return TFIDF._t


def main():
    body_night_of_milky = """
    「さあ、向うの坊ちゃんがた。いかがですか。おとり下さい。」
　ジョバンニは坊ちゃんといわれたのですこししゃくにさわってだまっていましたがカムパネルラは
「ありがとう、」と云いました。すると青年は自分でとって一つずつ二人に送ってよこしましたのでジョバンニも立ってありがとうと云いました。
　燈台看守はやっと両腕があいたのでこんどは自分で一つずつ睡っている姉弟の膝にそっと置きました。
「どうもありがとう。どこでできるのですか。こんな立派な苹果は。」
　青年はつくづく見ながら云いました。
「この辺ではもちろん農業はいたしますけれども大ていひとりでにいいものができるような約束もないし十倍も大きくて匂もいいのです。けれどもあなたがたのいらっしゃる方なら農業はもうありません。苹果だってお菓子だってかすが少しもありませんからみんなそのひとそのひとによってちがったわずかのいいかおりになって毛あなからちらけてしまうのです。」
　にわかに男の子がぱっちり眼をあいて云いました。
「ああぼくいまお母さんの夢や本のあるとこに居てね、ぼくの方を見て手をだしてにこにこにこにこわらったよ。ぼくおっかさん。りんごをひろってきてあげましょうか云ったら眼がさめちゃった。ああここさっきの汽車のなかだねえ。」
「その苹果がそこにあります。このおじさんにいただいたのですよ。」青年が云いました。
「ありがとうおじさん。おや、かおるねえさんまだねてるねえ、ぼくおこしてやろう。ねえさん。ごらん、りんごをもらったよ。おきてごらん。」
　姉はわらって眼をさましまぶしそうに両手を眼にあててそれから苹果を見ました。男の子はまるでパイを喰へ落ちるまでの間にはすうっと、灰いろに光って蒸発してしまうのでした。
　二人はりんごを大切にポケットにしまいました。
    """

    body_night_of_milky_new = """
すぐ男の子がちゃんと眼をあいて云った。 「ああぼくお母さんの夢や本のあるとこに居てね、ぼくの方を見て手をだしてたくさんわらったよ。ぼくおっかさん。りんごをひろってきてあげましょうか云ったら眼がさめちゃった。ああここさっきの汽車のなかだねえ。」「その苹果がそこにあります。このおじさんにいただいたのですよ。」青年が云った。 「ありがとうおじさん。おや、かおるねえさんまだねてるねえ、ぼくおこしてやろう。ねえさん。ごらん、りんごをもらったよ。おきてごらん。」 　姉はわらって眼をさましとりあえず両手を眼にあててそれから苹果を見ました。男の子はまるでパイを喰へ落ちると同時に、灰いろに光って蒸発してしまうのでした。二人はりんごを大切にポケットにしまった。
    """

    print "-----------------"
    print len(body_night_of_milky), "old"
    TFIDF.gen(body_night_of_milky)

    print "-----------------"
    print len(body_night_of_milky_new), "new"
    TFIDF.gen(body_night_of_milky_new)

if __name__ == '__main__':
    main()

