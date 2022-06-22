# -*- coding = uft-8 -*-
# @Time : 2022-03-20 19:17
# @Author : yzbyx
# @File : step4.py
# @Software : PyCharm
import pickle
import pandas as pd
import numpy as np
from config import *


def step4(laneID: int):
    """
    提取有效跟驰对数据，保存至{vehicleID: [有效数据1], [有效数据2] ...}结构、名为follow_leader的npy数据

    其中有效数据结构为[currentYList, currentVList, leaderYList, leaderVList, leaderL, indexNum, relatedPos]

    其中indexNum为原始数据中的index索引值列表，relatedPos为当前车辆follow-leader数据中的相对位置列表

    文件关系：data_filtered_lane + dataCA_T_energy(仅获取其中的vehicleID) -> follow_leader
    """
    data_filtered: pd.DataFrame = pd.read_pickle(os.path.join(pkl_save_path, 'data_filtered_lane_' + str(laneID)))
    # errorListTotal = np.load('../data/FrameListError' + '_' + str(laneID_), allow_pickle=True)
    # errorVehicleTotal, errorFrameTotal = errorListTotal
    vehicleList = np.load(os.path.join(npy_save_path, 'dataCA_T_energy_' + str(laneID) + '.npy'), allow_pickle=True)[0]
    indexNum = data_filtered.groupby(['v_Class', 'Vehicle_ID']).count().reset_index()
    vehicle_class_2 = indexNum[indexNum['v_Class'] == 2]['Vehicle_ID'].unique()

    vehicleList = list(set(vehicleList) & set(vehicle_class_2))  # 求交集，得到不换道的汽车列表

    # 车辆速度 > 5 m/s
    minV = 0
    # 纵向距离 < 120 m
    maxGap = 120
    # 最短数据时长 > 30 s
    minFrameL = 30 * 10
    # 净间距 > 0 m
    minGap = 0

    follow_leader = {}  # 储存有效的跟驰对数据
    for v in vehicleList:
        data = data_filtered[data_filtered['Vehicle_ID'] == v].sort_values(by=['Frame_ID'])
        dataTemp = []
        indexNum = []
        relatedPos = []
        currentYList, currentVList, leaderYList, leaderVList = [], [], [], []
        leaderPre = 0
        leaderL = 5
        for i, index in enumerate(data.index):
            # frameNum = 0  # 检测净间距小于61m
            dataByFrame = data.loc[index]
            leader = dataByFrame['Leader']
            if leader == 0:  # 前方无车
                if len(indexNum) >= minFrameL:
                    dataTemp.append([currentYList, currentVList, leaderYList, leaderVList, leaderL, indexNum, relatedPos])
                relatedPos, indexNum, currentYList, currentVList, leaderYList, leaderVList = [], [], [], [], [], []
                leaderPre = leader
                continue
            if leaderPre != leader and i != 0:  # 前车变化
                if len(indexNum) >= minFrameL:
                    dataTemp.append([currentYList, currentVList, leaderYList, leaderVList, leaderL, indexNum, relatedPos])
                relatedPos, indexNum, currentYList, currentVList, leaderYList, leaderVList = [], [], [], [], [], []
            leaderPre = leader

            frameID = dataByFrame['Frame_ID']
            leaderByFrame = data_filtered[(data_filtered['Frame_ID'] == frameID) &
                                          (data_filtered['Vehicle_ID'] == leader)]
            if len(leaderByFrame) == 0:
                if len(indexNum) >= minFrameL:
                    dataTemp.append([currentYList, currentVList, leaderYList, leaderVList, leaderL, indexNum, relatedPos])
                relatedPos, indexNum, currentYList, currentVList, leaderYList, leaderVList = [], [], [], [], [], []
                continue

            currentV = dataByFrame['v_Vel']
            leaderY = np.float64(leaderByFrame['Local_Y'].to_numpy())
            currentY = dataByFrame['Local_Y']
            leaderL = np.float64(leaderByFrame['v_Length'].to_numpy())
            leaderV = np.float64(leaderByFrame['v_Vel'].to_numpy())
            gap = leaderY - leaderL - currentY
            if currentV >= minV and minGap <= gap <= maxGap:
                currentYList.append(currentY)
                currentVList.append(currentV)
                leaderYList.append(leaderY)
                leaderVList.append(leaderV)
                indexNum.append(index)
                relatedPos.append(i)

            if i == len(data.index) - 1:
                if len(indexNum) >= minFrameL:
                    dataTemp.append([currentYList, currentVList, leaderYList, leaderVList, leaderL, indexNum, relatedPos])
                relatedPos, indexNum, currentYList, currentVList, leaderYList, leaderVList = [], [], [], [], [], []

        if len(dataTemp) > 0:
            follow_leader.update({v: dataTemp})
    with open(os.path.join(pkl_save_path, 'follow_leader_' + str(laneID) + '.pkl'), 'wb') as f:
        pickle.dump(follow_leader, f)


if __name__ == '__main__':
    step4(1)
