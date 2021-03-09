#!/usr/bin/env python3
# -*- coding: utf-8 -*-
def lbsTransform(df_res, lbs):
    # 循环遍历lbs信息
    # 其实可以不用出入参都有DataFrame，但毕竟临时任务暂不考虑优化
    for i in range(len(df_res)):
        xzl_lbs = df_res.loc[i,'xzl_lbs']
        if re.search(r"%s:'(.*?)'"%lbs,str(xzl_lbs)):
            lbs_t = re.search(r"%s:'(.*?)'"%lbs,str(xzl_lbs)).group(1)
            df_res.loc[i,'xzl_%s'%lbs] = lbs_t
    return df_res