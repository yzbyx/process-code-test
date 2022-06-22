# -*- coding = uft-8 -*-
# @Time : 2022-03-22 9:17
# @Author : yzbyx
# @File : step6.py
# @Software : PyCharm
import pickle
import numpy as np
from typing import List
from config import *


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


def _getAreaByVector(points: List[Point]):
    area = 0
    if len(points) < 3:
        raise RuntimeError('点的数量需要大于等于3！')
    for i in range(len(points) - 1):
        p1 = points[i]
        p2 = points[i + 1]
        try:
            triArea = (p1.x * p2.y - p2.x * p1.y) / 2
            area += triArea
        except TypeError as e:
            print(e)
            print(f'Type: {type(p1.x)}\tValue: {p1.x}')
            print(f'Type: {type(p1.y)}\tValue: {p1.y}')
            print(f'Type: {type(p2.x)}\tValue: {p2.x}')
            print(f'Type: {type(p2.y)}\tValue: {p2.y}')
    return area


def getAreaByOrderedPoints(x, y):
    """逆时针数据为正，顺时针为负"""
    if len(x) != len(y):
        raise RuntimeError(f'x的长度{len(x)}!=y的长度{len(y)}')
    if len(x) < 3:
        raise RuntimeError(f'数据长度小于3！')
    points = []
    for i in range(len(x)):
        points.append(Point(x[i], y[i]))
    points.append(points[0])

    area = _getAreaByVector(points)
    return area


def hysteresisJudge_revise(decData, accData, dec2acc: bool, errorJudge=True):
    """DecData -> 减速部分gap-speed数据；AccData -> 加速部分gap-speed数据"""
    if (len(decData[1]) < 10 or len(accData[1]) < 10) and errorJudge:  # 数据截取过短
        return -4, [], []

    minV = max(min(decData[1]), min(accData[1]))
    maxV = min(max(decData[1]), max(accData[1]))
    if maxV <= minV and errorJudge:  # 加速和减速数据未重叠，主要由于数据过短
        return -3, [], []
    if maxV - minV < 10 and errorJudge:  # 速度差不足
        return -6, [], []

    decIndex = np.where((decData[1] >= minV) & (decData[1] <= maxV))[0]
    accIndex = np.where((accData[1] >= minV) & (accData[1] <= maxV))[0]
    if (len(decIndex) < 10 or len(accIndex) < 10) and errorJudge:  # 有效数据过短
        return -5, [], []

    vDec = []
    gapDec = []
    qDec = []
    vAcc = []
    gapAcc = []
    qAcc = []

    # if len(np.where(decData[0] > 120)[0]) != 0 or len(np.where(accData[0] > 120)[0]) != 0:
    #     raise ValueError('存在大于120m')

    for i in decIndex:
        vDec.append(decData[1][i])
        gapDec.append(decData[0][i])
        qDec.append(3600 * vDec[-1] / (gapDec[-1] + 5))
    for i in accIndex:
        vAcc.append(accData[1][i])
        gapAcc.append(accData[0][i])
        qAcc.append(3600 * vAcc[-1] / (gapAcc[-1] + 5))
    if dec2acc:
        vDec.extend(vAcc)
        gapDec.extend(gapAcc)
        qDec.extend(qAcc)
        gAvg = - getAreaByOrderedPoints(vDec, gapDec) / (maxV - minV)
        qAvg = - getAreaByOrderedPoints(vDec, qDec) / (maxV - minV)
        vAvg = np.average(vDec)
        gapAvg = np.average(gapDec)
        vMaxDelta = maxV - minV
        gapMaxDelta = max(gapDec) - min(gapDec)
    else:
        vAcc.extend(vDec)
        gapAcc.extend(gapDec)
        qAcc.extend(qDec)
        gAvg = - getAreaByOrderedPoints(vAcc, gapAcc) / (maxV - minV)
        qAvg = - getAreaByOrderedPoints(vAcc, qAcc) / (maxV - minV)
        vAvg = np.average(vAcc)
        gapAvg = np.average(gapAcc)
        vMaxDelta = maxV - minV
        gapMaxDelta = max(gapAcc) - min(gapAcc)

    # 减速面积计算
    areaDec = 0
    areaDecQ = 0
    preIndex = decIndex[0]
    for index in decIndex[1:]:
        if index - 1 == preIndex:  # 判断数据点是否连续，其实不连续是有问题的
            areaDec += ((decData[0][preIndex] + decData[0][index]) / 2) * \
                       (decData[1][index] - decData[1][preIndex])
        preIndex = index
    # 加速面积计算
    areaAcc = 0
    preIndex = accIndex[0]
    for index in accIndex[1:]:
        if index - 1 == preIndex:  # 判断数据点是否连续
            areaAcc += ((accData[0][preIndex] + accData[0][index]) / 2) * \
                       (accData[1][index] - accData[1][preIndex])
        preIndex = index

    if (areaAcc < 0 or areaDec > 0) and errorJudge:  # 数据过于奇怪，主要由于能量波峰识别精度有限，且通常由于数据较短导致的问题
        return -2, [], []

    acc_dec_index = [accIndex, decIndex]
    other_data = [gAvg, qAvg, minV, maxV, vAvg, gapAvg, vMaxDelta, gapMaxDelta]

    if qAvg > 0:
        return -1, acc_dec_index, other_data  # 反迟滞
    elif qAvg < -300:
        return 2, acc_dec_index, other_data  # strong level
    elif qAvg < -50:
        return 1, acc_dec_index, other_data  # weak level
    elif qAvg <= 0:
        return 0, acc_dec_index, other_data  # negligible level


def openPickle(file: str):
    with open(file, 'rb') as f:
        return pickle.load(f)


def step6(laneID: int):
    """
    依照dataPeak数据进行加减速过程的单个拆分成段，
    调用hysteresisJudge函数判断拆分段的数据是否满足要求，
    并对符合要求的数据段进行正负迟滞及迟滞强度，保存hysteresisDataByType和ByVehicle的数据

    ByType结构为{'strong': [数据1, 数据2...], 'weak': [...], 'negligible': [...], 'negative': [...]}

    其中”数据“结构为[currentY, currentV, leaderY, leaderV, posRange, decOrAccJudge, c, rangeIndex, v, strength, leaderL]

    ByVehicle结构为{vehicleID: [数据1, 数据2...]}

    其中”数据“结构为[tempPositive_strong, tempPositive_weak, tempPositive_negligible, tempNegative]，

    其元素与ByType中的”数据“结构相同

    文件关系：follow_leader + dataPeak -> hysteresisDataByVehicle/ByType
    """
    follow_leader: dict = openPickle(os.path.join(pkl_save_path, f'follow_leader_{str(laneID)}.pkl'))
    dataPeak: dict = openPickle(os.path.join(pkl_save_path, f'dataPeak_{str(laneID)}.pkl'))
    hysteresisDataByVehicle = {}
    vehicleList = dataPeak.keys()
    positive_strong_num = 0
    positive_weak_num = 0
    positive_negligible_num = 0
    negative_num = 0

    hysteresisDataByType = {'strong': [], 'weak': [], 'negligible': [], 'negative': []}
    for v in vehicleList:
        dataList = dataPeak[v]
        trajectoryDataList = follow_leader[v]
        temp = []
        for j, data in enumerate(dataList):
            peakLocation, accOrDec = data
            currentYList, currentVList, leaderYList, leaderVList, leaderL, indexNum, relatedPos = trajectoryDataList[j]
            tempPositive_strong = []
            tempPositive_weak = []
            tempPositive_negligible = []
            tempNegative = []
            if len(accOrDec) > 2:
                for index in range(len(accOrDec)):
                    if index + 2 < len(accOrDec):
                        initState = accOrDec[index]

                        locStart = peakLocation[index]
                        locChange = peakLocation[index + 1]
                        locEnd = peakLocation[index + 2]

                        # print(locStart, locChange, locEnd)

                        leaderY = np.array(leaderYList[locStart:locEnd])
                        currentY = np.array(currentYList[locStart:locEnd])
                        leaderV = np.array(leaderVList[locStart:locEnd])
                        currentV = np.array(currentVList[locStart:locEnd])

                        leaderY_first = np.array(leaderYList[locStart:locChange])
                        currentY_first = np.array(currentYList[locStart:locChange])
                        currentV_first = np.array(currentVList[locStart:locChange])

                        leaderY_second = np.array(leaderYList[locChange:locEnd])
                        currentY_second = np.array(currentYList[locChange:locEnd])
                        currentV_second = np.array(currentVList[locChange:locEnd])

                        if initState < 0:  # 减速-加速过程
                            decOrAccJudge = -1
                            decGap = leaderY_first - currentY_first - leaderL
                            accGap = leaderY_second - currentY_second - leaderL
                            c, rangeIndex, strength =\
                                hysteresisJudge_revise([decGap, currentV_first], [accGap, currentV_second],
                                                       dec2acc=True)
                        else:  # 加速-减速过程
                            decOrAccJudge = 1
                            accGap = leaderY_first - currentY_first - leaderL
                            decGap = leaderY_second - currentY_second - leaderL
                            c, rangeIndex, strength =\
                                hysteresisJudge_revise([decGap, currentV_second], [accGap, currentV_first],
                                                       dec2acc=False)
                        #
                        # posRange需要保证[locStart->locEnd]之间的数据连续
                        posRange = [locStart, locChange, locEnd]
                        d = [currentY, currentV, leaderY, leaderV, posRange, decOrAccJudge, c, rangeIndex,
                             v, strength, leaderL]

                        if c == 2:
                            tempPositive_strong.append(d)
                            hysteresisDataByType['strong'].append(d)
                        elif c == 1:
                            tempPositive_weak.append(d)
                            hysteresisDataByType['weak'].append(d)
                        elif c == 0:
                            tempPositive_negligible.append(d)
                            hysteresisDataByType['negligible'].append(d)
                        elif c == -1:
                            tempNegative.append(d)
                            hysteresisDataByType['negative'].append(d)
                temp.append([tempPositive_strong, tempPositive_weak, tempPositive_negligible, tempNegative])
                positive_strong_num += len(tempPositive_strong)
                positive_weak_num += len(tempPositive_weak)
                positive_negligible_num += len(tempPositive_negligible)
                negative_num += len(tempNegative)
        if positive_negligible_num + positive_weak_num + positive_negligible_num + negative_num > 0:
            hysteresisDataByVehicle.update({v: temp})
    with open(os.path.join(pkl_save_path, f'hysteresisDataByVehicle_{str(laneID)}.pkl'), 'wb') as f:
        pickle.dump(hysteresisDataByVehicle, f)
    with open(os.path.join(pkl_save_path, f'hysteresisDataByType_{str(laneID)}.pkl'), 'wb') as f:
        pickle.dump(hysteresisDataByType, f)
    print(f'{str(laneID)}: {positive_strong_num}, {positive_weak_num}, {positive_negligible_num}, {negative_num}')


if __name__ == '__main__':
    step6(1)
