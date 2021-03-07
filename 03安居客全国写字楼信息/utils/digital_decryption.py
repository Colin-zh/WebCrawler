#!/usr/bin/env python
#-*- encoding:utf-8 -*-import requests
import base64
import re
from io import BytesIO
from fontTools.ttLib import TTFont 
from bs4 import BeautifulSoup as bs

def get_keymap(html):
    """
        对base64加密的页面内容进行解密
    """
    #获取密码
    keys_map = re.search(r'<script>!function\(w,d\)(.*?)<\/script>',html).group(1)
    #对密码解密转为map映射
    base64_str = re.search(r';base64,(.*?)\'\)', keys_map).group(1)
    font_content = base64.b64decode(base64_str)
    font = TTFont(BytesIO(font_content))
    keys = font.getBestCmap()
    keys = {'\\u' + hex(k)[2:] : str(int(v[-2:]) - 1) for k, v in keys.items()}
    return keys

def keymap_replace(price,keys):
    price = price.encode('unicode-escape').decode('utf-8')
    for k, v in keys.items():
        price = price.replace(k, v)
    return price.encode('utf-8').decode('unicode-escape')
