# -*- coding: utf-8 -*-
# ###################################################
# 作者：    Larry Zhang
# 版本：    v0.01   2020-11-19
# 功能：    爬取图片
# ###################################################
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
print(f'The page has {len(nodes)} tempNode(s)')   # nodes是各子网站的原列表

retry = 3
node_i = -1
nodei_valid = -1
nodes_len = len(nodes)
runinds = list(range(nodes_len - 1, -1, -1))    # 用 [...,2,1,0] 指向 nodes列表， 若nodes_len=0则此list也空。
ddnodes_succ = dict()        # blank dict to store nodes which successfully crawled over.  e.g. [0:1, 3:1]
ddnodes_fail = dict()        # blank dict to store failed times. +1 per each failure.  e.g. [0:3, 3:2]
# nodes = nodes.reverse()     # 反向
while runinds:
    node_i += 1
    runind = runinds.pop()       # pop最后一个。注：pop(0)是第一个
    nd = nodes[runind]
    # print(nd)
    ndd = json.loads(nd)  # loaded string with dict format to dict ndd
    # print(f"Title is 【{ndd['title']}】, URL is 【{ndd['url']}】, Date is 【{ndd['date']}】")
    # print(ndd)
    if '北辰区' in ndd['title'] and '控制性' in ndd['title'] and '详细规划' in ndd['title'] and '公布' in ndd['title']:
        nodei_valid += 1
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

        try:
            request2 = urllib.request.Request(url=prjurl, headers=headers)
            url_dir = posixpath.dirname(prjurl)
            res2 = urllib.request.urlopen(request2)
            res2.encoding = 'utf-8'
            soup2 = BeautifulSoup(res2, 'html.parser')
            ddnodes_succ[runind] = [1, 0, 0, '000']       # 第1位1表示取子网页成功；第2段0：表示里面的img待处理，1：成功，9失败；
            #                                               # 第3段表示img失败次数；第4段表示处理过的img序号（最后一个）
        except Exception as ex:               # 读取子网页失败，重试
            print(ex)
            if runind in ddnodes_fail:
                ddnodes_fail[runind] += 1
            else:
                ddnodes_fail[runind] = 1
            if retry > 0:
                runinds.append(runind)         # 读取失败，加回到run列表后边。
                retry -= 1
                time.sleep(0.7)
            else:
                if ddnodes_fail[runind] <= 3 * 2:
                    runinds.insert(0, runind)         # 3次失败，加到run列表最前边，即最后再试。
                else:
                    pass                                # else:超过两轮失败，放弃，直接写log吧。zzz

                retry = 3
            continue                            # 发生Exception后跳过后面循环下一个。

        imglst = soup2.find_all('img')   # 获取"详细"网页中所有图片链接

        path_title = normalize_as_path(ndd['title'])
        change_output_dir(path_title)
        saveHtml(path_title + '.html', soup2.prettify('utf-8'))  # res2.read() 已读不到东西了

        retryImg = 3
        i = 0
        while imglst:
            img = imglst.pop()
            dct = img.attrs
            if "src" in dct and not(dct['src'].startswith('..')):
                i += 1
                ddnodes_succ[runind][3] = f"{i:03d}"
                urlimg = dct['src']
                print(f'url of img = 【{urlimg}】')
                urlimg_http = urllib.parse.urljoin(url_dir + '/', urlimg)
                try:
                    urllib.request.urlretrieve(urlimg_http, f"{path_title}_{i:03d}.jpg")
                    ddnodes_succ[runind][1] = 1    # 表示img下载成功。
                except Exception as ex:
                    print(ex)
                    ddnodes_succ[runind][2] += 1
                    if retryImg > 0:
                        imglst.append(img)
                        retryImg -= 1
                        time.sleep(0.7)
                    else:
                        ddnodes_succ[runind][1] = 9  # 表示img失败。
                        retryImg = 3
                    continue
                print(runind, ': ', ddnodes_succ[runind])
    time.sleep(0.1)
