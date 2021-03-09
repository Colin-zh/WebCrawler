#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.append(sys.path[0]+'/..')
import pandas as pd
import progressbar
import re
from bs4 import BeautifulSoup
from utils.request import get_request

# 验证城市办公楼盘获取有效性
def validation(city_dct):
    # 定义关键字
    msg = '办公楼盘'
    # 初始化有效城市字典
    effective_cities = {}
    # 初始化progressbar
    # 定义进度条的显示样式
    widgets = ['有效验证中 : ', 
            progressbar.Percentage(), 
            " ", 
            progressbar.Bar(), 
            " ", 
            progressbar.ETA()]
    # 创建进度条并开始运行
    pbar = progressbar.ProgressBar(maxval=len(city_dct), 
                                widgets=widgets).start()
    i = 0
    for city,abbr in city_dct.items():
        url = 'https://%s.anjuke.com/'%abbr
        content = get_request(url, anonymous=True)
        i += 1
        pbar.update(i)
        navigation_info = re.search(r'<a(.*?)>%s</a>'%msg, content)
        if navigation_info:
            url = re.search(r'href=(.*?)>', navigation_info.group(0)).group(1)
            effective_cities[city] = {'abbr':abbr, 'url':url}        
    # 结束进度条
    pbar.finish()
    return effective_cities

if __name__ == '__main__':
    # 初始化城市链接页
    url = 'https://www.anjuke.com/sy-city.html'
    # 城市列表
    content = BeautifulSoup(get_request(url,True), features='lxml')
    cities = content.find('div', class_='letter_city').find_all('a')
    # 城市缩写清洗
    city_map = {}
    for city in cities:
        city_name = city.text.strip()
        city_abbr = city.attrs['href'].replace('https://','').replace('.anjuke.com','')
        city_map[city_name] = city_abbr
    # 安居客中会把小城市的缩写归类到附近大城市，例如：临安，富阳归为杭州
    # 因此需要对city_map进行清洗，仅保留大城市的对应关系
    # Step1 统计具有重复缩写城市的名称集合
    # city_df = pd.DataFrame.from_dict(city_map, 
    #                                  orient='index', 
    #                                  columns = ['abbr']).reset_index().rename(columns = {'index':'city'}) # 字典转dataframe
    # tmp = city_df.groupby('abbr')['city'].agg(['count', list]).reset_index() # 统计abbr重复个数及对应城市列表
    # tmp.where(tmp['count'] != 1).dropna() # 仅观测count不为1的城市缩写

    # Step2 观测发现，一下城市冗余
    duplicated_cities = ['巴州', '农安', '阿坝州', '阿坝州', '大邑', '金堂', '铜梁', '丰都', 
                        '长寿', '巢湖', '涪陵', '南川', '永川', '綦江', '黔江', '万州', '江津', 
                        '合川', '宁乡', '普兰店', '肇源', '长乐', '连江', '平潭', '白沙县', 
                        '儋州市', '澄迈县', '定安', '琼中', '屯昌', '文昌市', '淳安', '富阳', 
                        '临安', '桐庐', '肥东', '肥西', '庐江', '长丰', '龙门', '平阴', 
                        '济阳', '商河', '宜良', '文安', '永登', '榆中', '汝阳', '当涂', 
                        '宾阳', '横县', '宁海', '新建', '即墨', '胶南', '晋安', '陵水', 
                        '保亭', '东方市', '上虞', '无极', '辛集', '元氏', '辽中', '新民', 
                        '乐亭', '滦县', '周至', '户县', '蓝田', '丰县', '睢宁', '江都', 
                        '中牟', '巩义']
    # 安居客涵盖的所有城市
    city_dct = {key: city_map[key] for key in city_map.keys() if key not in duplicated_cities}
    # 可直接通过导航栏中的 "办公楼盘" 获取写字楼的城市
    effective_cities = validation(city_dct)
    # 上述字典转DataFrame
    city_df = pd.DataFrame.from_dict(city_dct, 
                                    orient='index', 
                                    columns=['abbr']).reset_index().rename(columns = {'index':'city'}) # 字典转dataframe
    effective_cities_df = pd.DataFrame.from_dict(effective_cities, 
                                             orient='index').reset_index() # 字典转dataframe
    # 输出保存
    city_df.to_csv('%s/../data/01_cities.csv'%sys.path[0], encoding='utf-8', index=False)
    effective_cities_df.to_csv('%s/../data/02_effective_cities.csv'%sys.path[0], encoding='utf-8', index=False)
