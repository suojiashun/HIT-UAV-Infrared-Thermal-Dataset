# Datasets

## KITTI IEEE 2012

### 目的：

解决由于缺少benchmark模仿真实环境，使得识别系统能够应用到机器人领域的问题。提出了多种task，如stereo, optical flow, SLAM, 3D object detection。

### 论点：

- 自动驾驶过去大部分依赖GPS, LiDAR, RaDar，缺少基于optical flow的方法。--> optical flow
- Middleburry, Caltech-101数据集是基于controlled environment采集的，过于简单。--> mid-size city 采集， 采用高清黑白及彩色相机，LiDAR，卫星定位信息，基于IMU的纠正信号。

### 主要内容：

- sensor的配置、参数以及位置关系 --> 说明精度高
- 所有sensor的校正的过程
- 说明dataset的各个种类，并绘图，说明数据集的多样性。
- 将其他数据集的高ranking算法在KITTI上进行evaluation，并分析。

### 数据集：

- 超过200K 3D object annotations
- 2D/3D object detection, semantic segmentation

## CARPK

### 目的：

解决基于无人机视角下视频内物体的`计数`问题。提出生成物体数目以及物体位置的网络。提出了一个目前为止`最大的`且`第一个`无人机视角数据集。

### 论点：

- 现有算法忽视了物体位置信息。
- 现有的数据集不够large-scale

### 内容：

- 将数据集在multi scenes, resolution, annotation format, car numbers上比较。
- 算法设计，自己算法与YOLO, Faster RCNN对比，设计metrics表示很好。

### 数据集：

- ~90K cars from 4 parking lots
- 2D object detection

## highD IEEE 2018

### 目的：

提供准确的能反应驾驶员驾驶行为的数据集用于安全验证。

### 内容：

- 与现有最大训练集NGSIM Dataset进行比较

- 提出测量方法的要求，并进行比较：

  - naturalistic behavior: 驾驶员需要不知道被测量

  - static scenario description：车道数，宽度，限速等需要被采集
  - dynamic scenario description：能反映interaction, maneuvers
  - flexibility：覆盖多种交通情况。多地、多时段测量。

- 介绍数据集的情况

### 数据集：

- 110K车辆的轨迹信息，包括汽车、卡车
- 6个不同高速公路采集点
- 60个视频，全长16.5h。每段均拍摄420m的路面。4K，25FPS. DJI Phantom Pro Plus，每个pixel代表了10x10cm²的路面大小。
- sunny, windless，8AM to 5PM
- 通过`算法`获取汽车信息，`人工`标注infrastructure。通过U-Net进行semantic segmentation后生成bbox。模型在人工标注的3000张图进行验证。
- 视频通过OpenCV进行稳定。将背景map到第一帧。第一帧且进行过rotation，将车道线水平。
- object trajectory, detection

## BOXY IEEE 2019

### 目的：

提供一个2D/3D bbox的**benchmark**

### 内容：

- 与其他数据集如KITTI, Cityscapes, BDD100K等进行比较。
- 介绍数据集的具体信息，包括天气，日期，frames等信息。
- 为benchmark设置baseline算法，挑选了SSD, MobileNet V2以及Faster R-CNN和NASNET-A。

### 数据集：

- 200K images
- 1.99M vehicle annotations
- 2464x2056 pixels
- 3d-like and 2d bbox

## DOTA IEEE 2018

### 目的：

提出适用于Earth Vision的可反映实际情况的数据集，包含OBB。

### 论点：

普通数据集由于高空拍摄下物体的大小不一，以及物体的群聚性，不能很好的识别。

### 内容：

- 与其他数据集进行比较。
- 如何image collection, category selection, annotation method
- benchmark设置，分别针对HBB,OBB设置baseline算法。并且发现基于OBB的Faster RCNN 的效果比基于HBB的好很多。54.13vs39.95.

### 数据集：

- 2806 aerial images, 188K instances
- 4000 x 4000 pixels
- 15 categories
- oriented bbox

