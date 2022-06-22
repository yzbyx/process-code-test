# -*- coding = uft-8 -*-
# @Time : 2022-03-22 20:48
# @Author : yzbyx
# @File : hysteresisCount.py
# @Software : PyCharm
import pickle
import random
from config import *


def openPickle(file: str):
    with open(file, 'rb') as f:
        return pickle.load(f)


def showLoop():
    """统计迟滞环种类数量"""
    hysteresisDataByType = {'strong': [], 'weak': [], 'negligible': [], 'negative': []}
    for laneID in range(1, 9):
        temp = openPickle(os.path.join(pkl_save_path, f'hysteresisDataByType_{str(laneID)}.pkl'))
        hysteresisDataByType['strong'].extend(temp['strong'])
        hysteresisDataByType['weak'].extend(temp['weak'])
        hysteresisDataByType['negligible'].extend(temp['negligible'])
        hysteresisDataByType['negative'].extend(temp['negative'])

    seed = 1
    random.seed(seed)

    strongList = hysteresisDataByType['strong']
    strong = random.choice(strongList)
    weakList = hysteresisDataByType['weak']
    weak = random.choice(weakList)
    negligibleList = hysteresisDataByType['negligible']
    negligible = random.choice(negligibleList)
    negativeList = hysteresisDataByType['negative']
    negative = random.choice(negativeList)

    # ---- 绘制 ---- #


if __name__ == '__main__':
    showLoop()
