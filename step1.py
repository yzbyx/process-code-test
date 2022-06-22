# -*- coding = uft-8 -*-
# @Time : 2022-03-20 18:10
# @Author : yzbyx
# @File : step1.py
# @Software : PyCharm
import pandas as pd
import numpy as np
from config import *


def step1(laneID: int):
    """合并有问题的车辆帧，保存错误对应的帧与车辆ID"""
    # 读取Finder保存的数据
    data_std_lane = pd.read_pickle(os.path.join(pkl_save_path, 'data_std_lane' + '_' + str(laneID)))

    # 读取异常数据的index
    errorListY = np.load(os.path.join(npy_save_path, 'errorListY' + '_' + str(laneID) + '.npy'), allow_pickle=True)
    errorListV = np.load(os.path.join(npy_save_path, 'errorListV' + '_' + str(laneID) + '.npy'), allow_pickle=True)
    errorListAcc = np.load(os.path.join(npy_save_path, 'errorListAcc' + '_' + str(laneID) + '.npy'), allow_pickle=True)

    # 对异常的位置进数据行删除
    errorList = list(set(errorListY) | set(errorListV) | set(errorListAcc))  # 将异常数据合并

    # 将相同车辆的对应异常帧打包
    VehicleListError = []  # 异常车辆ID
    FrameListError = []  # 对应异常帧
    vehicleNow = data_std_lane.at[errorList[0], 'Vehicle_ID']
    for index in errorList:
        vehicleID = data_std_lane.at[index, 'Vehicle_ID']
        frameID = data_std_lane.at[index, 'Frame_ID']
        if vehicleID not in VehicleListError and vehicleID == vehicleNow:
            VehicleListError.append(vehicleID)
            FrameListError.append([frameID])
        elif vehicleID not in VehicleListError and vehicleID != vehicleNow:
            VehicleListError.append(vehicleID)
            FrameListError.append([frameID])
            vehicleNow = vehicleID
        elif vehicleID in VehicleListError and vehicleID != vehicleNow:
            i = VehicleListError.index(vehicleID)
            FrameListError[i].append(frameID)
            vehicleNow = vehicleID
        elif vehicleID in VehicleListError and vehicleID == vehicleNow:
            i = VehicleListError.index(vehicleID)
            FrameListError[i].append(frameID)
    print(f'需要重新计算的帧数量：{len(np.concatenate(FrameListError))}')
    # 保存错误对应的帧与车辆ID
    newList = [VehicleListError, FrameListError]
    np.save(os.path.join(npy_save_path, 'FrameListError' + '_' + str(laneID)), newList, allow_pickle=True)
