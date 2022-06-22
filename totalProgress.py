# -*- coding = uft-8 -*-
# @Time : 2022-03-20 17:36
# @Author : yzbyx
# @File : totalProgress.py
# @Software : PyCharm
import winsound

from errorFinder import errorFinder
from step1 import step1
from step2 import step2
from step3 import step3
from step4 import step4
from step5 import step5
from step6 import step6
from infoMake import infoMake


def main():
    mode = "quick"  # "quick"模式跳过了jerk检查和1s内jerk变号检查
    try:
        for laneID in range(1, 9):
            errorFinder(laneID, mode)
            print(f'lane{laneID}: errorFinder complete')
            step1(laneID)
            print(f'lane{laneID}: step1 complete')
            step2(laneID)
            print(f'lane{laneID}: step2 complete')
            step3(laneID)
            print(f'lane{laneID}: step3 complete')
            step4(laneID)
            print(f'lane{laneID}: step4 complete')
            step5(laneID)
            print(f'lane{laneID}: step5 complete')
            step6(laneID)
            print(f'lane{laneID}: step6 complete')
    except Exception as e:
        print(e)
    infoMake()
    print('infoMake complete')
    winsound.PlaySound("SystemHand", winsound.SND_ALIAS)


if __name__ == '__main__':
    main()
