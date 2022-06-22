# -*- coding = uft-8 -*-
# @Time : 2022-03-20 18:25
# @Author : yzbyx
# @File : step2.py
# @Software : PyCharm
from scipy.signal import *
import numpy as np
import pandas as pd
from config import *


# Butterworth一阶过滤器
def lowPassButterworthDigital(sig):
    srate = 10  # sample rate
    Nyquist = srate / 2  # Nyquist frequency
    lpf = 1  # low-pass frequency
    order = 1  # filter order

    firstValue = sig['v_Vel'].iat[0]
    output = sig.copy()
    output['v_Vel'] -= firstValue

    b, a = butter(order, lpf / Nyquist)

    filtered_data = lfilter(b, a, output['v_Vel'].to_numpy())

    output['v_Vel'] = filtered_data
    output['v_Vel'] += firstValue
    return output


def step2(laneID: int):
    """
    由于车辆换道前后行为会影响真实的跟驰状态，仅对非换道车辆的速度进行butterworth滤波信号处理，平滑速度数据

    数据保存至data_filtered_lane的pandas数据

    文件关系：data_std_lane + errorListLossFrame -> data_filtered_lane
    """
    data: pd.DataFrame = pd.read_pickle(os.path.join(pkl_save_path, 'data_std_lane' + '_' + str(laneID)))
    # 只对发生换道的车辆进行去除
    errorLossFrame = np.load(os.path.join(npy_save_path, 'errorListLossFrame' + '_' + str(laneID) + '.npy'),
                             allow_pickle=True)
    errorList = []  # 发生换道的车辆
    for i in errorLossFrame:
        if i[0] not in errorList:
            errorList.append(i[0])

    vehicleList = data['Vehicle_ID'].unique()
    dataFiltered = data.copy()
    for vehicleID in vehicleList:
        if vehicleID not in errorList:
            signalArray = (data[data['Vehicle_ID'] == vehicleID])
            signalOutput = lowPassButterworthDigital(signalArray)
            dataFiltered.loc[signalOutput.index] = signalOutput
    dataFiltered.to_pickle(os.path.join(pkl_save_path, 'data_filtered_lane' + '_' + str(laneID)))


if __name__ == '__main__':
    step2(1)
