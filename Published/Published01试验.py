# 试验版本。
# -*- coding: utf-8 -*-
import re
import json
from bs4 import BeautifulSoup
import urllib.request
from urllib import parse
import posixpath   # from posixpath import dirname, basename
from os import makedirs, path, chdir
import sys
import time

sys.path.append(path.abspath('../'))  # 工作目录 Spiders
from _shared.path_dealing import normalize_as_path  # 从 _share 目录里导入normalize_as_path() 函数

# specify the url
url1 = 'http://ghhzrzy.tj.gov.cn/ywpd/cxgh_43015/ghgb/'
output_path = r'C:/tmp/SpiderGongBu1/'

# 解决403： Forbidden 报错, 增加下面的req来替换 page = urllib.request.urlopen(urlpage) 中的urlpage:
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'}


def saveHtml(file_name, file_content):
    with open(normalize_as_path(file_name), 'wb') as f:
        f.write(file_content)


def change_output_dir(path_title):
    output_this = path.join(output_path, path_title)
    if not path.exists(output_this):
        makedirs(output_this)
    chdir(output_this)


request1 = urllib.request.Request(url=url1, headers=headers)
res = urllib.request.urlopen(request1)  # 加重试几次。。。。。。。。。。。。。。。zzz
res.encoding = 'utf-8'
soup = BeautifulSoup(res, 'html.parser')
# urls = soup.find_all("table", "dl_newslist")  # .findAll('a', href=re.compile('^((?!//)(?!:).)*$'))

# 用<script。。。里关键字tempNode搜寻：
# pattern = re.compile(r"tempNode = {(.*)};$", re.MULTILINE | re.DOTALL)  # {(.*)};$匹配整个script，即贪婪模式；{(.*?)};$只匹配一个分号结束的语句。
pattern = re.compile(r"(?<=tempNode = )(\{.*?\})", re.MULTILINE | re.DOTALL)  # {(.*)};$匹配整个script，即贪婪模式；{(.*?)};$只匹配一个分号结束的语句。
scrpt = soup.find("script", text=pattern)  # s = soup.find( text=pattern)
# print(pattern.search(script.string).group(1))  # group(n)   Python2.x: script.text
nodes = pattern.findall(scrpt.string)  # pattern.findall(s) 返回list
print(f'The page has {len(nodes)} tempNode(s)')
for nd in nodes:
    # print(nd)
    ndd = json.loads(nd)  # loaded string with dict format to dict ndd
    # print(f"Title is 【{ndd['title']}】, URL is 【{ndd['url']}】, Date is 【{ndd['date']}】")
    # print(ndd)
    if '北辰区' in ndd['title'] and '控制性' in ndd['title'] and '详细规划' in ndd['title'] and '公布' in ndd['title']:
        print( f"要求的标题【{ndd['title']}】" )
        # print(nd)
        print(f"Title is 【{ndd['title']}】, URL is 【{ndd['url']}】, Date is 【{ndd['date']}】")
        if ndd['url'].startswith(r'./') or \
           ndd['url'].startswith(r'/') and not(ndd['url'].startswith(r'//')):
            prjurl = parse.urljoin(url1, ndd['url'])
        elif ndd['url'].startswith(r'http'):
            prjurl = ndd['url']
        else:
            continue

        request2 = urllib.request.Request(url=prjurl, headers=headers)
        url_dir = posixpath.dirname(prjurl)
        res2 = urllib.request.urlopen(request2)
        res2.encoding = 'utf-8'
        soup2 = BeautifulSoup(res2, 'html.parser')
        imglst = soup2.find_all('img')   # 获取"详细"网页中所有图片链接

        path_title = normalize_as_path(ndd['title'])
        change_output_dir(path_title)
        saveHtml(path_title + '.html', soup2.prettify('utf-8'))  # res2.read() 已读不到东西了

        i = 0
        for img in imglst:
            dct = img.attrs
            if "src" in dct and not(dct['src'].startswith('..')):
                urlimg = dct['src']
                print(f'url of img = 【{urlimg}】')
                urlimg_http = urllib.parse.urljoin(url_dir + '/', urlimg)
                i += 1
                urllib.request.urlretrieve(urlimg_http, f"{path_title}_{i:03d}.jpg")
    time.sleep(0.1)
