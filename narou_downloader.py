# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import requests
import yaml
import codecs
from bs4 import BeautifulSoup
from subprocess import PIPE, Popen
import re
import sys
import time


def main(start, finish):
    print 'start'

    # read yaml
    _base_yml = './narou_data/{}.yml'
    counter = 0
    for x in range(0, 4):
        yml_path = _base_yml.format(x)
        with open(yml_path) as f:
            data = yaml.load(f)
            for record in data:
                counter += 1
                if start <= counter <= finish:
                    if 'ncode' in record:
                        novel = Novel(record)
                        novel.download('./narou_data')
                        print '[+]downloaded: {} : {}'.format(counter, novel.title)


    # _url = 'http://ncode.syosetu.com/{}/{}/'


class Novel(object):
    _data = None
    base_path = None

    def __init__(self, data):
        assert(type(data) == dict)
        self._data = data

    @property
    def title(self):
        return self._data['title'].replace('\r\n', '').replace('\n', '')

    @property
    def ncode(self):
        return self._data['ncode']

    @property
    def general_all_no(self):
        return int(self._data['general_all_no'])

    @property
    def global_point(self):
        return int(self._data['global_point'])

    @property
    def filepath(self):
        return "./narou_data/novel/{}.txt".format(self.ncode)

    def get_url(self, num):
        return 'http://ncode.syosetu.com/{}/{}/'.format(self.ncode.lower(), num)

    def download(self, base_path):
        self.base_path = base_path
        c = [self.title]
        # download 30話くらい
        for x in range(2, min(self.general_all_no, 20)):
            url = self.get_url(x)
            body = download(url)
            soup = BeautifulSoup(body, 'lxml')
            contents = soup.find_all("div", attrs={"id": "novel_honbun"})
            if contents:
                contents = contents[0]
            else:
                print "[-]Error No Contents {}:{}".format(str(x), self.title)
                continue
            c.append(contents.get_text())
            time.sleep(0.3)
        writer(self.filepath, b''.join(c))


def download(url):
    _base_cmd = "curl '{url}' -H 'Accept-Encoding: gzip, deflate, sdch' -H 'Accept-Language: ja,en-US;q=0.8,en;q=0.6' -H 'Upgrade-Insecure-Requests: 1' -H 'User-Agent: Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.76 Mobile Safari/537.36' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8' -H 'Referer: http://ncode.syosetu.com/n6450bt/7/' -H 'Cookie: bs.test.cen; OX_plg=swf|shk|pm; ses=zGDy5JNfPzq8DnAAzWbP90; lineheight=0; fontsize=0; novellayout=0; fix_menu_bar=1; _gat=1; _td=5294520f-2d0c-44de-ae14-325b427cfb63; nlist1=9s5x.8-hwgx.3-karn.5-k9dh.5-kb0s.5-k1bv.5-kd19.0-8hrp.b; ks2=e42qgwt7n3sw; sasieno=0; smplineheight=0; smpfontsize=0; smpnovellayout=0; _ga=GA1.2.678180494.1480608954' -H 'Connection: keep-alive' -H 'Cache-Control: max-age=0' --compressed"
    c = _base_cmd.format(url=url)
    output = cmdline(c).stdout.readlines()
    output_str = b''.join(output)
    return output_str


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


def writer(filepath, body):
    with codecs.open(filepath, mode='w', encoding='utf8') as fw:
        fw.write(body)

if __name__ == '__main__':
    argvs = sys.argv  # コマンドライン引数を格納したリストの取得
    assert len(argvs) == 3, argvs

    start_index = int(argvs[1])
    limit = int(argvs[2])
    main(start_index + 1, start_index + limit)
