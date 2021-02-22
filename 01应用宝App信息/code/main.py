#!/usr/bin/env python
#-*- encoding:utf-8 -*-
import sys
import json
import pandas as pd
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def chrome_init():
    options = webdriver.ChromeOptions()
    # 不加载图片,加快访问速度
    options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
    # 此步骤很重要，设置为开发者模式，防止被各大网站识别出来使用了Selenium
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    return webdriver.Chrome(options=options)

def get_pkg_details_yyb(key_word,url):

    # 开启浏览器及对应链接
    driver = chrome_init()
    driver.get(url)

    # 设置滚动限定条件
    content = driver.page_source
    target = '<a href="javascript:void(0);">加载更多<i class="load-more-icon"></i></a>'

    # 执行滚动至对应css组件消失，记录html文件
    # 设定滚动间隔为2s
    time_start = time.time()
    while target in content and time.time()-time_start <= 60:
        driver.find_element_by_class_name('load-more').click() 
        content = driver.page_source
        time.sleep(2)
    driver.close()

    # 转化为bs4
    bf = BeautifulSoup(content,features="lxml")

    # 抓取html5中关键信息
    app_info = bf.find_all('a', class_ = 'appName', target='_blank')
    app_name = list(map(lambda x: x.text, app_info))
    pkg_name = list(map(lambda x: x.attrs['href'].replace('../myapp/detail.htm?apkName=',''), app_info))
    cnt = list(map(lambda x: x.text.replace('人下载','') ,bf.find_all('div', class_='down-line')))
    desc = list(map(lambda x: x.text,bf.find_all('div', class_='recommend-hidden-box')))
    key_word = [key_word] * len(app_name)

    # 返回app相关信息
    return pd.DataFrame(list(zip(key_word,app_name,pkg_name,cnt,desc)),columns = ['key_word','app_name','pkg_name','download_cnt','description'])

if __name__ == '__main__':

    # 读取json配置
    with open('%s/config.json'%sys.path[0],'r',encoding='utf8')as fp:
        json_data = json.load(fp)
    key_words = json_data['key_words']
    output_tag = json_data['output_tag']

    # 创建空dataframe存储app信息
    df  = pd.DataFrame(columns = ['key_word','app_name','pkg_name','download_cnt','description'])

    # 执行应用宝抓取
    # 根据关键字获取所有app的url
    urls = list(map(lambda key_word: 'https://sj.qq.com/myapp/search.htm?kw={}'.format(key_word), key_words))
    dict_yyb = dict(zip(key_words,urls))

    # dataframe添加相关信息
    for key_word,url in dict_yyb.items():
        df = df.append(get_pkg_details_yyb(key_word,url), ignore_index=True)

    # 数据整合
    # 去重，按key_words顺序保留不重复值
    df.pkg_name = df.pkg_name.apply(lambda x : x.split('&info=')[0])
    df = df.drop_duplicates(['pkg_name'])

    # 指定路径生成xlsx文件
    df.to_excel(sys.path[0] + '/../result/' + output_tag + '.xlsx')
