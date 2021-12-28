# 3D photography on your desk

成员及分工
- 林笑 PB18061311
  - 调研，coding，搭建实物系统
- 聂亦潇 PB18061331
  - 测试，debug，编写报告


## 问题描述

在人类的视觉（或者说感知）系统中，感知物体的三维信息物体的能力一定最让科研学者着迷的。因此，3D重建一直是一个非常让人激动而又感兴趣的任务，但大部分方法往往需要非常昂贵的设备（例如，laser，LCD projector）、专业化的实验环境以及专门定制的软件。但科研的道路往往是交错纵横的，既然有追求高精度的重建，那也有追求简单、高性价比的重建。Jean-Yves Bouguety 与 Pietro Perona在1998年IEEE上发表的文章《3D photography on your desk》凭借及其简单的硬件实现的3D重建，能在自己的桌面上实现自己的3D重建系统的效果，一下就吸引了我。毕竟，能真正实现一个系统是让人成就感满满的一件事。

本项目以上述文章为基础，搭建了一个桌面3D重建系统，实现了一种基于weak structured lighting的、简单又经济的物体3D信息提取装置。

- 创意描述 

首先，我们需要准备的硬件有，一张棋盘格、一台PC、一只笔、一根笔直的不透光的棍子、一个平整桌面（最好是纯白色的，可以垫一张白纸实现）、一个可以摄像的设备（我使用的是手机）以及一个光源（最好接近点光源，可以使用台灯，我是做法是向室友又借了一部手机，用手机背后的手电筒作为光源）以及待重建的物体（我的是一个陶瓷碗）。如下所示：


![image](https://github.com/USTC-Computer-Vision-2021/project-cv_lx-nyx/blob/main/img/1.PNG)

最终可以实现的效果是，我们仅需通过让棍子的阴影扫过物体的方式，就可以实现对物体的3D重建

![image](https://github.com/USTC-Computer-Vision-2021/project-cv_lx-nyx/blob/main/img/2.gif)

## 原理分析

- 相机标定

首先，需要对相机参数进行标定。


- 光源估计

- 物体3D扫描

VERSION_1.0 

2021.12.18

作者目前需要准备期末考试和其他任务，一周后完善README

calib文件夹下为相机标定素材，light文件夹下为估计光源位置素材，bowl文件夹下为3D重建的素材（一个碗）

先创建一个新的conda环境，python=3.8，再运行

    pip install -r requirements.txt
    
安装所需要的包

完成后，若希望直接查看效果，运行

    python visualize.py 

若希望从头开始计算物体点云，可按照默认参数运行以下命令，详细参数请查看源代码

    python calib.py
    python light.py
    python desk_scan.py
    
    
在我的笔记本上大致需要10min
