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

首先，我们需要准备的硬件有，一张棋盘格、一台PC、一只笔、一根笔直的不透光的杆子、一个平整桌面（最好是纯白色的，可以垫一张白纸实现）、一个可以摄像的设备（我使用的是手机）以及一个光源（最好接近点光源，可以使用台灯，我是做法是向室友又借了一部手机，用手机背后的手电筒作为光源）以及待重建的物体。下面是论文作者给出的硬件设备实例：


![image](https://github.com/USTC-Computer-Vision-2021/project-cv_lx-nyx/blob/main/img/hardware.png)

最终可以实现的效果是，我们仅需通过让棍子的阴影扫过物体的方式，就可以实现对物体的3D重建

![image](https://github.com/USTC-Computer-Vision-2021/project-cv_lx-nyx/blob/main/img/scan.gif)

## 原理分析

整个过程大致可以分为三步：相机标定、光源估计以及物体3D扫描。

- 相机标定

首先，需要对相机参数进行标定。我们采用的是和opencv-python官方demo中一样的标定流程，首先需要用相机从不同的角度拍摄棋盘格，并将图片保存在./calib/目录下。如下图例子所示：

![image](https://github.com/USTC-Computer-Vision-2021/project-cv_lx-nyx/blob/main/img/calib.jpg)

程序会计算出相机的内参、畸变系数以及各个外参。（标定过程中，世界坐标z=0平面实际上是桌面，这意味着我们得到了桌面的平面方程）

- 光源估计

接下来需要估计光源所在位置。我们需要将笔立在桌面上，利用笔尖的影子以及笔的底座的位置计算出光源的位置，下面给出一个摆放的例子：

![image](https://github.com/USTC-Computer-Vision-2021/project-cv_lx-nyx/blob/main/img/light_demo.jpg)

利用光心与笔尖的影子的连线与桌面的交点、光心与笔底座与桌面的交点，我们可以计算出笔的底座与笔尖的影子在世界坐标系下的位置。同时我们可以测量出笔的高度，就得到了笔尖在世界坐标系下的位置，于是光心就在笔尖与笔尖的影子二者的连线上。重复上述过程，找到多条这样的直线，它们的交点就是光源的位置，原理示意图如下：

![image](https://github.com/USTC-Computer-Vision-2021/project-cv_lx-nyx/blob/main/img/light.PNG)

实际操作中，由于误差的存在，这些直线几乎不可能交在一个点（甚至任意两条相交都是不可能的），所以我们求最小二乘解。

- 物体3D扫描

在完成光源位置估计后就可以进行物体的3D重建了。首先，我们需要确定杆的阴影在桌面上的位置（实际上只要确定阴影上两个点的位置），这可以用和上面估计光源位置时确定笔的阴影和笔的底座的位置同样的方法。确定了阴影直线和光源的位置后，就得到了一个平面，我们称之为阴影平面。而物体真实的世界坐标就是光心与像素组成的直线与阴影平面的交点，原理如下所示：

![image](https://github.com/USTC-Computer-Vision-2021/project-cv_lx-nyx/blob/main/img/desk_scan.PNG)


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
