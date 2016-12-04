# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import requests
import yaml
import codecs

def main():
    print 'start'
    _base_url = 'http://api.syosetu.com/novelapi/api/?length=1000-&allcount=10000&title=1&lim=500&out=yaml&of=t-n-gp-ga&order=hyoka&st={}'
    _base_filepath = './narou_data/{}.yml'

    for x in range(0, 100):
        filepath = _base_filepath.format(x)
        url = _base_url.format(1 + 500 * x)
        r = download(url)
        if r:
            body = r.text
            writer(filepath, body)
            print '[+]download success :{}'.format(x)
        else:
            print '[-]download fail :{}'.format(x)


def download(url):
    count = 0
    while True:
        count += 1
        r = requests.get(url)
        if r.status_code == 200:
            return r
        if count > 5:
            return None


def writer(filepath, body):
    with codecs.open(filepath, mode='w', encoding='utf8') as fw:
        fw.write(body)


if __name__ == '__main__':
    main()
