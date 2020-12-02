# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import urllib.request
import os

# specify the url
url = 'http://www.qiushibaike.com/'

# 解决403： Forbidden 报错, 增加下面的req来替换 page = urllib.request.urlopen(urlpage) 中的urlpage:
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'}
request1 = urllib.request.Request(url=url, headers=headers)


if __name__ == '__main__':
    res = urllib.request.urlopen(request1)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res, 'html.parser')
    imgs = soup.find_all("img")

    _path = os.getcwd()
    new_path = os.path.join(_path, 'picturesTmp')
    if not os.path.isdir(new_path):
        os.mkdir(new_path)
    new_path += r'\ '

    try:
        x = 1
        if imgs == []:
            print("Done!")
        for img in imgs:
            link = img.get('src')
            if 'pictures' in link:
                if '//' == link[:2]:
                    linkh = "http:" + link
                else:
                    linkh = link
                print(f"It's downloading {x}th's piture")
                urllib.request.urlretrieve(linkh, new_path + f'{x}.jpg')
                x += 1

    except Exception as e:
        print(e)
    else:
        pass
    finally:
        if x:
            print("It's Done!!!")
