# -*- coding = uft-8 -*-
# @Time : 2022-03-20 17:44
# @Author : yzbyx
# @File : errorFinder.py
# @Software : PyCharm
import os

import pandas as pd
import numpy as np
from config import *


def errorFinder(laneID: int, mode: str):
    data = pd.read_csv(csv_path,
                       usecols=['Vehicle_ID', 'Frame_ID', 'Lane_ID', 'Local_Y', 'v_Vel', 'v_Acc', 'v_Length', 'v_Class',
                                'Following', 'Preceeding'])
    data.rename(columns={'Preceeding': 'Leader', 'Following': 'Follower'}, inplace=True)

    data_std = data
    data_std[['Local_Y', 'v_Vel', 'v_Acc', 'v_Length']] = data_std[['Local_Y', 'v_Vel', 'v_Acc', 'v_Length']].apply(
        lambda x: x * 0.3048).round(decimals=5)
    data_std_lane = data_std[data_std['Lane_ID'] == laneID]
    data_std_lane.to_pickle(os.path.join(pkl_save_path, 'data_std_lane' + '_' + str(laneID)))

    # 一、位置异常识别
    # 车头间距小于前车车身长
    FrameList = data_std_lane['Frame_ID'].unique()
    errorListY = []
    errorListGap = []
    errorListHeadGap = []
    for frameID in FrameList:
        data_by_frame = data_std_lane[data_std_lane['Frame_ID'] == frameID]
        for index in data_by_frame.index:
            temp = data_by_frame.loc[index]
            if temp['Leader'] == 0:
                continue
            temp_Leader = (data_by_frame[data_by_frame['Vehicle_ID'] == temp['Leader']])
            if len(temp_Leader) == 0:
                continue
            gap = temp_Leader['Local_Y'].iat[0] - temp['Local_Y'] - temp_Leader['v_Length'].iat[0]
            headGap = temp_Leader['Local_Y'].iat[0] - temp['Local_Y']
            if gap < 0:
                errorListY.append(index)
                errorListGap.append(gap)
                errorListHeadGap.append(headGap)

    arr1 = np.array(errorListGap)
    arr2 = np.array(errorListHeadGap)
    if len(arr1) != 0 and len(arr2) != 0:
        print(f'最小间距(m)：{np.min(arr1)}')
        print(f'最小车头间距(m)：{np.min(arr2)}')
    print(f'位置异常数量：{len(errorListY)}')
    print(f'位置异常比例：{len(errorListY) / len(data_std_lane)}')
    np.save(os.path.join(npy_save_path, 'errorListY' + '_' + str(laneID)), errorListY)

    # 二、速度错误提取
    errorListV = []
    errorSpeed = []
    for frameID in FrameList:
        data_by_frame = data_std_lane[data_std_lane['Frame_ID'] == frameID]
        for index in data_by_frame.index:
            speed = data_by_frame.at[index, 'v_Vel']
            if speed < 0:
                errorListV.append(index)
                errorSpeed.append(speed)

    arr = np.array(errorSpeed)
    print(f'限速值(m/s)：{55 * 1609.344 / 3600}')
    if len(arr) != 0:
        print(f'最小异常速度(m/s)：{np.min(arr)}')
        print(f'最大异常速度(m/s)：{np.max(arr)}')
    print(f'速度异常数量：{len(errorListV)}')
    print(f'速度异常比例：{len(errorListV) / len(data_std_lane)}')
    np.save(os.path.join(npy_save_path, 'errorListV' + '_' + str(laneID)), errorListV)

    # 三、加速度错误提取
    errorListAcc = []
    errorAcc = []
    for index in data_std_lane.index:
        if -8 <= data_std_lane.at[index, 'v_Acc'] <= 5:
            continue
        errorListAcc.append(index)
        errorAcc.append(data_std_lane.at[index, 'v_Acc'])
    arr = np.array(errorAcc)
    if len(arr) != 0:
        print(f'最小异常加速度(m/s^2)：{np.min(arr)}')
        print(f'最大异常加速度(m/s^2)：{np.max(arr)}')
    print(f'加速度异常数量：{len(errorListAcc)}')
    print(f'加速度异常比例：{len(errorListAcc) / len(data_std_lane)}')
    np.save(os.path.join(npy_save_path, 'errorListAcc' + '_' + str(laneID)), errorListAcc)

    VehicleList = data_std_lane['Vehicle_ID'].unique()
    if mode != 'quick':
        # 四、加速度变化率错误提取
        # jerk计算
        data_std_lane['v_Jerk'] = np.NAN
        errorListJerk = []
        errorJerk = []
        for vehicleID in VehicleList:
            data_by_vehicle = data_std_lane[data_std_lane['Vehicle_ID'] == vehicleID]
            for index in data_by_vehicle.index:
                frameID = data_by_vehicle.at[index, 'Frame_ID']
                accNow = data_by_vehicle.at[index, 'v_Acc']
                temp = data_by_vehicle[data_by_vehicle['Frame_ID'] == (frameID - 1)]
                if len(temp) == 0:
                    continue
                accPer = temp['v_Acc'].iat[0]
                jerk = (accNow - accPer) / 0.1
                data_std_lane.at[index, 'v_Jerk'] = jerk
                if abs(jerk) > 15:
                    errorListJerk.append(index)
                    errorJerk.append(jerk)
        arr = np.array(errorJerk)
        if len(arr) != 0:
            print(f'最小异常加速度变化率(m/s^3)：{np.min(arr)}')
            print(f'最大异常加速度变化率(m/s^3)：{np.max(arr)}')
        print(f'加速度变化率异常数量：{len(errorListJerk)}')
        print(f'加速度变化率异常比例：{len(errorListJerk) / len(data_std_lane)}')
        np.save(os.path.join(npy_save_path, 'errorListJerk' + '_' + str(laneID)), errorListJerk)

        # 五、加速度变化率1s内变号1次以上
        errorListJerkSwitch = []
        errorJerkSwitch = []
        data_std_lane['is_change'] = np.NAN
        for vehicleID in VehicleList:
            data_by_vehicle = data_std_lane[data_std_lane['Vehicle_ID'] == vehicleID]
            for index in data_by_vehicle.index:
                frameID = data_by_vehicle.at[index, 'Frame_ID']
                jerkNow = data_by_vehicle.at[index, 'v_Jerk']
                temp = data_by_vehicle[data_by_vehicle['Frame_ID'] == (frameID - 1)]
                if len(temp) == 0:
                    continue
                jerkPer = temp['v_Jerk'].iat[0]
                data_by_vehicle.at[index, 'is_change'] = 1 if jerkNow * jerkPer < 0 else 0

            for index in data_by_vehicle.index:
                frameID = data_by_vehicle.at[index, 'Frame_ID']
                lowerFrame = frameID - 5
                upperFrame = frameID + 5
                temp = data_by_vehicle[(data_by_vehicle['Frame_ID'] >= lowerFrame) &
                                       (data_by_vehicle['Frame_ID'] < upperFrame)]
                if temp['is_change'].sum() > 1:
                    errorListJerkSwitch.append(index)
                    errorJerkSwitch.append(temp['is_change'].sum())
            data_std_lane.loc[data_by_vehicle.index, 'is_change'] = data_by_vehicle['is_change']
        arr = np.array(errorJerkSwitch)
        if len(arr) != 0:
            print(f'最大异常加速度变化率1s变号次数：{np.max(arr)}')
        print(f'加速度变化率1s变化异常数量：{len(errorJerkSwitch)}')
        print(f'加速度变化率1s变化异常比例：{len(errorJerkSwitch) / len(data_std_lane)}')
        np.save(os.path.join(npy_save_path, 'errorListJerkSwitch' + '_' + str(laneID)), errorListJerkSwitch)

    # 六、换道缺帧提取
    # 尽量避免换道车辆的影响
    errorListLossFrame = []
    for vehicleID in VehicleList:
        data_by_vehicle = data_std_lane[data_std_lane['Vehicle_ID'] == vehicleID]
        data_by_vehicle = data_by_vehicle.sort_values(by=['Frame_ID'])
        if data_by_vehicle['Frame_ID'].max() - data_by_vehicle['Frame_ID'].min() + 1 != len(data_by_vehicle):
            # print(f'Find!{vehicleID}')
            for indexOrd, index in enumerate(data_by_vehicle.index):
                if indexOrd != len(data_by_vehicle) - 1:
                    framePer = data_by_vehicle['Frame_ID'].iat[indexOrd]
                    currentframe = data_by_vehicle['Frame_ID'].iat[indexOrd + 1]
                    if framePer + 1 != currentframe:
                        temp = [vehicleID, framePer, currentframe]
                        errorListLossFrame.append(temp)
    print(f'换道返回次数：{len(errorListLossFrame)}')
    print(f'换道返回车辆比例：{len(errorListLossFrame) / len(data_std_lane)}')
    np.save(os.path.join(npy_save_path, 'errorListLossFrame' + '_' + str(laneID)), errorListLossFrame, allow_pickle=True)
