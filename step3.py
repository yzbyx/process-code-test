# -*- coding = uft-8 -*-
# @Time : 2022-03-20 19:31
# @Author : yzbyx
# @File : step3.py
# @Software : PyCharm
import pywt
import numpy as np
import pandas as pd
from config import *


def step3(laneID: int):
    """
    对非换道车辆计算其平滑后速度波的能量值，保存至[trueList, dataCA, energy]结构的dataCA_T_energy的npy文件

    其中trueList为非换道车辆的ID列表，dataCA为不同缩放值下T(a,b)的二维np数组列表，energy为平均能量值

    文件关系：data_filtered_lane + errorListLossFrame -> dataCA_T_energy
    """
    wavelet = pywt.ContinuousWavelet(name='mexh', dtype=np.float64)

    df = pd.read_pickle(os.path.join(pkl_save_path, 'data_filtered_lane_' + str(laneID)))
    errorList = np.load(os.path.join(pkl_save_path, 'errorListLossFrame_' + str(laneID) + '.npy'),
                        allow_pickle=True)
    changeList = []  # 发生换道的车辆
    for i in errorList:
        if i[0] not in changeList:
            changeList.append(i[0])

    vList = df['Vehicle_ID'].unique()
    dataY = []
    dataX = []
    dataCA = []
    energy = []
    # dataCA_abs = []
    trueList = []
    for v in vList:
        if v not in changeList:
            data = df[df['Vehicle_ID'] == v].sort_values(by=['Frame_ID'])
            tempX = data['Frame_ID'] * 0.1
            tempY = data['v_Vel']
            (cA, cD) = pywt.cwt(tempY, range(1, 65), wavelet)
            dataX.append(tempX)
            dataY.append(tempY)
            dataCA.append(np.array(cA))
            # dataCA_abs.append(np.abs(np.array(cA)))
            energy.append((np.array(cA) ** 2).sum(axis=0) / 64)
            trueList.append(v)
    np.save(os.path.join(npy_save_path, 'dataCA_T_energy_' + str(laneID)),
            np.asanyarray([trueList, dataCA, energy], dtype=object))
