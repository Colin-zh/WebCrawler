#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.append(sys.path[0]+'/..')
import pandas as pd
import re
from bs4 import BeautifulSoup
from utils.request import get_request
from utils.digital_decryption import get_keymap,keymap_replace
from utils.lbs_transfrom import lbsTransform

def getInfo(effective_cities_dct):
    # 初始化结果列表与字典长度
    res = []
    cities_len = len(effective_cities_dct)
    # 循环遍历字典爬虫
    for index,row in effective_cities_dct.items():
        # 初始化页数与记录城市数
        pageIndex = 1
        cityIndex = index + 1
        # 初始化城市及链接信息
        city = row['index']
        abbr = row['abbr']
        url = row['url']
        # 初始化停止抓取信息
        msg = '暂无匹配的楼盘'
        content_text = '-1'
        while msg not in content_text:
            print("【INFO】：正在获取{}第{}页，进度为{}/{}".format(city,pageIndex,cityIndex,cities_len))
            # 初始化url
            url = re.search(r'https://.*?/loupan/',url).group(0) + 'p%s/'%pageIndex
            # 获取网页信息，更新content_text
            html = get_request(url,True)
            content = BeautifulSoup(html, features='lxml')
            content_text = content.find('div', class_='main-body').text
            # 提前结束
            if msg in content_text:
                break
            # 获取密钥
            keys = get_keymap(html)
            # 写字楼列表
            xzl_list = content.find_all('div', class_='list-item')
            # 写字楼细节
            for xzl in xzl_list:
                xzl_name = xzl.find('p', class_='list-item-content-title').text
                xzl_url = xzl.find('a', class_='for-track').attrs['href']
                print("【INFO】：正在获取{}第{}页，当前楼盘为{}，URL为{}".format(city,pageIndex,xzl_name,xzl_url))
                xzl_address = xzl.find('p', class_='list-item-content-address').text.replace(' ','').replace('"','').replace('·','|').replace('\n','')
                xzl_price_encrypted = xzl.find('div', class_='list-item-content-price').find('p').text
                if xzl_price_encrypted != "暂无参考价格":
                    xzl_price = keymap_replace(xzl_price_encrypted,keys)
                    print("【INFO】：正在获取{}第{}页，当前楼盘为{}，URL为{}".format(city,pageIndex,xzl_name,xzl_url))
                else:
                    xzl_price = xzl_price_encrypted
                    print("【WARN】：正在获取{}第{}页，当前楼盘为{}，URL为{}，该楼盘无价格信息".format(city,pageIndex,xzl_name,xzl_url))
                xzl_html = get_request(xzl_url, anonymous=True)
                print("【INFO】：正在进入楼盘详情页，获取{}第{}页楼盘为{}，URL为{}，".format(city,pageIndex,xzl_name,xzl_url))
                xzl_lbs = re.search(r'var map = (.*?);', xzl_html, flags=re.M|re.S)
                if xzl_lbs:
                    xzl_lbs = xzl_lbs.group(1).replace('\n','').replace(' ','')
                else:
                    xzl_lbs = ''
                res. append([city,abbr,url,xzl_name,xzl_address,xzl_price,xzl_url,xzl_lbs])
                print("【DONE】：当前楼盘获取完毕，已完成{}第{}页楼盘为{}，URL为{}，".format(city,pageIndex,xzl_name,xzl_url))
            #更新页数
            pageIndex += 1
        print("【DONE】：获取{}完毕，共{}页，进度为{}/{}".format(city,pageIndex,cityIndex,cities_len))
    return res


if __name__ == 'main':
    # 读取可直接通过导航栏中 "办公楼盘" 的城市数据
    effective_cities_df = pd.read_csv('%s/../data/02_effective_cities.csv'%sys.path[0])
    # 转字典，便于操作
    effective_cities_dct = effective_cities_df.to_dict(orient='index')
    # 执行遍历爬虫
    res = getInfo(effective_cities_dct)
    # 列表转DataFrame
    df_res = pd.DataFrame(res,columns=['city','abbr','city_url','xzl_name','xzl_addr','xzl_price','xzl_url','xzl_lbs'])
    # 按城市，名字，地址去重
    df_res = df_res.drop_duplicates(['city','xzl_name','xzl_addr'])
    # 经纬度清洗
    df_res = lbsTransform(df_res, lbs = 'lng')
    df_res = lbsTransform(df_res, lbs = 'lat')
    # 输出保存
    df_res.to_csv('%s/../data/03_effective_cities_xzl.csv'%sys.path[0], encoding='utf-8', index=False)
    
