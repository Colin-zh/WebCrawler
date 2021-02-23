#!/usr/bin/env python
#-*- encoding:utf-8 -*-
import sys
import json
import pandas as pd
import random
import requests
import progressbar
from bs4 import BeautifulSoup

def get_details_wdj(bf,key_word,res):
    try:
        # 获取所有列表APP信息
        applist = bf.find_all('li', class_='search-item search-searchitems')
        # 遍历app_list清洗出App信息同时更新进度条状态
        for app in applist:
            res[0].append(key_word)
            res[1].append(app.find('a', class_ = 'name').text.strip())
            res[2].append(app.find_all('a')[-1].attrs['data-app-pname'])
            res[3].append(app.find_all('span')[-1].text.strip())
            res[4].append(app.find('div', class_ = 'comment').text.strip())

        return res
    except Exception as e:
        return False

def get_info_wdj(key_word):

    # user_agent列表
    user_agent_list = [
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER',
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)',
        'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 SE 2.X MetaSr 1.0',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/4.4.3.4000 Chrome/30.0.1599.101 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 UBrowser/4.0.3214.0 Safari/537.36'
    ]

    # referer列表（图片防盗链）
    #referer_list = [
    #    'https://www.wandoujia.com/'
    #]

    # 初始化header
    header = {'User-Agent': random.choice(user_agent_list)}
    #header = {'User-Agent': random.choice(user_agent_list), 'Referer': random.choice(referer_list)}

    # 初始化分页索引
    pageIndex = 1

    # 初始化页面返回首页
    content = '-1'

    # 初始化返回列表，不可使用 [[]]*5
    res = [[],[],[],[],[]]

    # 返回为空信息
    #msg = '''{"state":{"code":2000000,"msg":"Ok","tips":""},"data":{"currPage":0,"totalPage":0,"content":""}}'''

    # 获取第一页信息同时获取总页数
    url = 'https://www.wandoujia.com/wdjweb/api/search/more?page={}&key={}'.format(pageIndex,key_word)
    html = requests.get(url = url, headers = header).text

    # 转化为bs4
    content = json.loads(html)['data']['content']
    bf = BeautifulSoup(content,features="lxml")

    totalPage = json.loads(html)['data']['totalPage']

    # 初始化progressbar
    # 定义进度条的显示样式
    widgets = [key_word + ' : ', progressbar.Percentage(), " ", progressbar.Bar(), " ", progressbar.ETA()]

    # 创建进度条并开始运行
    pbar = progressbar.ProgressBar(maxval=totalPage, widgets=widgets).start()

    res = get_details_wdj(bf,key_word,res)
    if res:
        pbar.update(pageIndex)
    else:
        print('" ' + key_word + ' " ' + '爬取第%s'%pageIndex + '页时出错')

    # 循环获取剩余页数网页app信息
    while pageIndex < totalPage:

        # 更新url及html内容
        pageIndex += 1
        url = 'https://www.wandoujia.com/wdjweb/api/search/more?page={}&key={}'.format(pageIndex,key_word)
        html = requests.get(url = url, headers = header).text

        # 转化为bs4
        content = json.loads(html)['data']['content']
        bf = BeautifulSoup(content,features="lxml")

        res = get_details_wdj(bf,key_word,res)
        if res:
            pbar.update(pageIndex)
        else:
            print('" ' + key_word + ' " ' + '爬取第%s'%pageIndex + '页时出错')
    
    # 结束进度条
    pbar.finish()

    return pd.DataFrame(zip(*res),columns = ['key_word','app_name','pkg_name','download_cnt','description'])

if __name__ == '__main__':

    # 读取json配置
    with open('%s/config.json'%sys.path[0],'r',encoding='utf8')as fp:
        json_data = json.load(fp)
    key_words = json_data['key_words']
    output_tag = json_data['output_tag']

    # 创建空dataframe存储app信息
    df  = pd.DataFrame(columns = ['key_word','app_name','pkg_name','download_cnt','description'])

    # 遍历获取各关键字对应app列表
    for key_word in key_words:
        tmp = get_info_wdj(key_word)
        # dataframe添加相关信息
        df = df.append(tmp, ignore_index = True)

    # 数据整合
    # 去重，按key_words顺序保留不重复值
    df = df.drop_duplicates(['pkg_name'])

    # 指定路径生成xlsx文件
    df.to_excel(sys.path[0] + '/../result/' + output_tag + '.xlsx')
    
