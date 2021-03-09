#!/usr/bin/env python
#-*- encoding:utf-8 -*-
import sys
import requests
import pandas as pd
import json
import time
import random
from bs4 import BeautifulSoup

# 刷新ip白名单
def ipWhitelist(order):
    # 获取当前ip
    cur_ip = requests.get("http://soft.goubanjia.com/wl/myip/%s.html"%order).test.strip()
    # 将当前ip更新至白名单
    requests.get("http://soft.goubanjia.com/wl/setip/{}.html?ips={}&clear=".format(order,cur_ip))


# 使用高匿ip代理，使用全国代理 http://www.goubanjia.com/user/index.html
def get_request(url, anonymous = True):
    # user_agent列表
    user_agent_list = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER",
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 SE 2.X MetaSr 1.0",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/4.4.3.4000 Chrome/30.0.1599.101 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 UBrowser/4.0.3214.0 Safari/537.36"
    ]
    # header
    header = {"User-Agent": random.choice(user_agent_list)}
    # 是否需要高匿ip代理，默认为True
    if anonymous:
        # 填写个人orderID
        order = "请输入您个人的orderID号"
        # 动态api
        apiUrl = "http://dynamic.goubanjia.com/dynamic/get/" + order + ".html"
        # api调用无所谓headers
        ip = requests.get(apiUrl).text.strip()
        requests.get("http://soft.goubanjia.com/wl/setip/{}.html?ips=&clear=".format(order))
        # 检查当前ip是否在白名单中
        try:
            int(ip.split(":")[-1])
        except Exception as e:
            # 添加当前ip至白名单
            requests.get("http://soft.goubanjia.com/wl/setip/{}.html?ips=&clear=".format(order))
        # 设置代理
        proxies = {"http":"http://"+ip, "https":"https://"+ip}
        # 尝试访问
        try:
            r = requests.get(url, proxies=proxies, headers=header, timeout=(5,10), allow_redirects=True)
            content = BeautifulSoup(r.text, features="lxml").text
            if r.status_code == 200 and "手机验证" in content:
                return r.text
            elif r.status_code == 200 and "验证" not in content:
                return r.text
            elif r.status_code == 404:
                print("【WARN】：返回404，页面丢失")
                return False
            elif r.status_code == 407:
                print("【WARN】：返回407，ip刷新")
                requests.get("http://soft.goubanjia.com/wl/setip/{}.html?ips=&clear=".format(order))
                return get_request(url, anonymous = True)
            else:
                print("【验证】：触发访问验证，返回值为{}，url为{}，重新申请访问".format(r.status_code,url))
                return get_request(url, anonymous = True)
        except Exception as _:
            print("【警告】：当前ip访问超时，ip为{}，url为{}".format(ip,url))
            # 超时原因一般为ip响应过慢，重新调用代理api替换ip尝试即可
            return get_request(url, anonymous = True)
    else:
        try:
            r = requests.get(url, headers=header, timeout=(5,10), allow_redirects=True)
            content = BeautifulSoup(r.text, features="lxml").text
            if r.status_code == 200 and "验证" not in content:
                return r.text
            else:
                print("【验证】：触发访问验证，返回值为{}，url为{}，重新申请访问".format(r.status_code,url))
                return get_request(url, anonymous = False)
        except Exception as e:
            print("【警告】：当前ip访问超时，ip为{}，url为{}".format(ip,url))
            # 超时原因一般为ip响应过慢，重新调用代理api替换ip尝试即可
            return get_request(url, anonymous = False)



