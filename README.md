# process-code-test

车辆轨迹处理工具-Alpha-0.1

## 文件说明

**totalProgress.py**

数据一次性处理的快捷入口

**errorFinder.py**

* 读取原始轨迹数据
* 位置异常识别（车头间距小于前车车身长）
* 速度错误提取（车辆速度小于0）
* 加速度错误提取（加速度小于-8m/s^2或大于5m/s^2）
* jerk错误提取（jerk绝对值大于15m/s^3）
* 1s内jerk变号检查（jerk变号多于1次）
* 换道缺帧提取

**step1.py**

合并有问题的车辆帧，保存错误对应的帧与车辆ID

**step2.py**

对非换道车辆的速度进行butterworth滤波信号处理，平滑速度数据

