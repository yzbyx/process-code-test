# -*- coding = uft-8 -*-
# @Time : 2022-06-21 21:34
# @Author : yzbyx
# @File : config.py
# @Software : PyCharm
import os

# pkl数据保存位置
# 默认值：当前文件所处文件夹
pkl_save_path = os.path.dirname(__file__)
# npy数据保存位置
# 默认值：当前文件所处文件夹
npy_save_path = os.path.dirname(__file__)
# 原始数据文件路径
# 默认值：当前文件所处文件夹 + data.csv
csv_path = os.path.join(os.path.dirname(__file__), 'trajectories-0750am-0805am.csv')
#
