# -*- coding = uft-8 -*-
# @Time : 2022-04-11 16:47
# @Author : yzbyx
# @File : infoMake.py
# @Software : PyCharm
import os.path
import pickle
import pandas as pd
from config import *


def openPickle(file: str):
    with open(file, 'rb') as f:
        return pickle.load(f)


def infoMake():
    """结果汇总"""
    data2pd = {'Vehicle_ID': [], 'Hysteresis_Type': [], 'Dec_Or_Acc': [], 'Q_Delta': [], 'Gap_Delta': [], 'Min_V': [],
               'Max_V': [], 'Acc_Time': [], 'Dec_Time': [], 'Time': [],
               'vAvg': [], 'gapAvg': [], 'vMaxDelta': [], 'gapMaxDelta': []}
    for laneID in range(1, 9):
        infoByType: dict = openPickle(os.path.join(pkl_save_path, f'hysteresisDataByType_{str(laneID)}.pkl'))
        for t in list(infoByType.keys()):
            data = infoByType[t]
            for d in data:
                # currentY, currentV, leaderY, leaderV, posRange, decOrAccJudge, c, rangeIndex,
                # v, strength, leaderL
                _, _, _, _, posRange, decOrAccJudge, c, rangeIndex, v, strength, leaderL = d
                data2pd['Vehicle_ID'].append(v)
                data2pd['Hysteresis_Type'].append(t)
                data2pd['Q_Delta'].append(strength[1])
                data2pd['Gap_Delta'].append(strength[0])
                if decOrAccJudge == -1:
                    data2pd['Acc_Time'].append((posRange[2] - posRange[1]) / 10)
                    data2pd['Dec_Time'].append((posRange[1] - posRange[0]) / 10)
                else:
                    data2pd['Acc_Time'].append((posRange[1] - posRange[0]) / 10)
                    data2pd['Dec_Time'].append((posRange[2] - posRange[1]) / 10)
                data2pd['Dec_Or_Acc'].append(decOrAccJudge)
                data2pd['Time'].append((posRange[2] - posRange[0]) / 10)
                data2pd['Min_V'].append(strength[2])
                data2pd['Max_V'].append(strength[3])
                # gAvg, qAvg, minV, maxV, vAvg, gapAvg, vMaxDelta, gapMaxDelta
                data2pd['vAvg'].append(strength[4])
                data2pd['gapAvg'].append(strength[5])
                data2pd['vMaxDelta'].append(strength[6])
                data2pd['gapMaxDelta'].append(strength[7])

    df = pd.DataFrame(data=data2pd)
    df.to_pickle(os.path.join(pkl_save_path, 'df_hysteresis_data'))


if __name__ == '__main__':
    infoMake()
