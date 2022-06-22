# -*- coding = uft-8 -*-
# @Time : 2022-03-20 23:41
# @Author : yzbyx
# @File : step5.py
# @Software : PyCharm
import pickle
import numpy as np
from config import *


def step5(laneID: int):
    """
    提取减速->加速交通波动车辆轨迹，保存至dataPeak的pickle文件

    其中dataPeak结构为：{vehicleID: [[dataE_peak_location, accOrDec], [...] ...]}

    其中dataE_peak_location、accOrDec分别为能量波峰在follow-leader有效数据中的相对位置列表、对应加减速变化点属性

    文件关系：dataCA_T_energy + follow_leader -> dataPeak
    """
    vehicleList, dataT, dataE = np.load(os.path.join(npy_save_path, 'dataCA_T_energy_' + str(laneID) + '.npy'),
                                        allow_pickle=True)
    with open(os.path.join(pkl_save_path, 'follow_leader_' + str(laneID) + '.pkl'), 'rb') as f:
        follow_leader: dict = pickle.load(f)

    dataPeak = {}  # 存储变化点

    validVehicleList = follow_leader.keys()
    vehicleList = list(vehicleList)
    for v in validVehicleList:
        dataTotal = follow_leader[v]
        temp = []
        for data in dataTotal:
            # 获取速度加减速变化点
            index = vehicleList.index(v)
            currentYList, currentVList, leaderYList, leaderVList, leaderL, indexNum, relatedPos = data
            dataT_v: np.ndarray = dataT[index][:, relatedPos[0]: relatedPos[-1] + 1]
            dataTAvg = dataT_v.copy().sum(axis=0) / 64
            dataE_v: np.ndarray = dataE[index][relatedPos[0]: relatedPos[-1] + 1]

            # 获取能量峰值位置
            dataE_01 = dataE_v[1:] - dataE_v[:-1]
            num = dataE_01[0]
            np.insert(dataE_01, 0, num)
            dataE_01 = np.int64(dataE_01 > 0)
            dataE_01 = dataE_01[1:] - dataE_01[:-1]
            num = dataE_01[0]
            np.insert(dataE_01, 0, num)
            location_all = np.where(np.abs(dataE_01) > 0)[0]
            location_peak = np.where(dataE_01 < 0)[0]

            # 对邻近的起伏较小的波峰进行合并
            defaultA = 50  # 默认幅值
            tempLoc = location_peak[0]
            dataE_peak_location = [tempLoc]
            tempPeak = tempLoc
            preIsMerge = True  # 上一个峰值是否并入peak_location
            for loc in location_all[1:]:
                if loc in location_peak:
                    tempPeak = loc
                if abs(dataE_v[loc] - dataE_v[tempLoc]) <= defaultA:  # 小于默认波动值
                    if loc in location_peak:
                        preIsMerge = False
                elif loc in location_peak:  # 有大于默认波动值的情况
                    dataE_peak_location.append(loc)
                    preIsMerge = True
                elif preIsMerge is False:
                    dataE_peak_location.append(tempPeak)
                tempLoc = loc

            # 获取加减速状态值
            accOrDec = []
            for loc in dataE_peak_location:
                accOrDec.append(-1 if dataTAvg[loc] > 0 else 1)

            # 修正加减速状态值
            if len(accOrDec) > 1:
                peakMaxLoc = dataE_peak_location[0]
                for loc in dataE_peak_location:
                    if dataE_v[peakMaxLoc] <= dataE_v[loc]:
                        peakMaxLoc = loc
                index = dataE_peak_location.index(peakMaxLoc)
                for i in range(len(accOrDec)):
                    if i == 0:
                        continue
                    targetIndex_1 = index - 2 * i
                    targetIndex_2 = index - 2 * i + 1
                    targetIndex_3 = index + 2 * i
                    targetIndex_4 = index + 2 * i - 1
                    if targetIndex_1 >= 0:
                        accOrDec[targetIndex_1] = accOrDec[index]
                    if targetIndex_2 >= 0:
                        accOrDec[targetIndex_2] = - accOrDec[index]
                    if targetIndex_3 < len(accOrDec):
                        accOrDec[targetIndex_3] = accOrDec[index]
                    if targetIndex_4 < len(accOrDec):
                        accOrDec[targetIndex_4] = - accOrDec[index]
                    if targetIndex_1 < 0 and targetIndex_2 < 0 and\
                            targetIndex_3 >= len(accOrDec) and targetIndex_4 >= len(accOrDec):
                        break

            temp.append([dataE_peak_location, accOrDec])

        dataPeak.update({v: temp})
    with open(os.path.join(pkl_save_path, f'dataPeak_{str(laneID)}.pkl'), 'wb') as f:
        pickle.dump(dataPeak, f)


if __name__ == '__main__':
    step5(laneID=1)
