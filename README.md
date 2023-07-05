# 3D photography on your desk

## 问题描述

在人类的视觉（或者说感知）系统中，感知物体的三维信息物体的能力一定最让科研学者着迷的。因此，3D重建一直是一个非常让人激动而又感兴趣的任务，但大部分方法往往需要非常昂贵的设备（例如，laser，LCD projector）、专业化的实验环境以及专门定制的软件。但科研的道路往往是交错纵横的，既然有追求高精度的重建，那也有追求简单、高性价比的重建。Jean-Yves Bouguety 与 Pietro Perona在1998年发表的文章《3D photography on your desk》凭借及其简单的硬件实现的3D重建，能在自己的桌面上实现自己的3D重建系统的效果.

本仓库以上述文章为基础，搭建了一个桌面3D重建系统，实现了一种基于weak structured lighting的、简单又经济的物体3D信息提取装置。

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

实际操作中，由于误差的存在，使用求最小二乘解。

- 物体3D扫描

在完成光源位置估计后就可以进行物体的3D重建了。首先，我们需要确定杆的阴影在桌面上的位置（实际上只要确定阴影上两个点的位置），这可以用和上面估计光源位置时确定笔的阴影和笔的底座的位置同样的方法。确定了阴影直线和光源的位置后，就得到了一个平面，我们称之为阴影平面。而物体真实的世界坐标就是光心与像素组成的直线与阴影平面的交点，原理如下所示：

![image](https://github.com/USTC-Computer-Vision-2021/project-cv_lx-nyx/blob/main/img/desk_scan.PNG)

## 效果展示

首先，使用阴影对物体进行扫描

![image](https://github.com/USTC-Computer-Vision-2021/project-cv_lx-nyx/blob/main/img/scan.gif)

借助open3d，展示生成的结果

![image](https://github.com/USTC-Computer-Vision-2021/project-cv_lx-nyx/blob/main/img/bowl.gif)

## 工程结构

```text
.
├── src
│   ├── calib.py
│   ├── light.py
│   ├── desk_scan.py
│   ├── screen_shot.py
│   ├── visualize.py
├── img //一些显示在报告中的图片
│   ├── ...
├── calib //放置标定用的素材
│   ├── calib_1.jpg
│   ├── calib_2.jpg
│   ├── ...
├── light //放置光源估计用的素材
│   ├── light_1.jpg
│   ├── light_2.jpg
│   ├── ...
├── bowl //放置碗的素材
│   ├── bowl_00.jpg
│   ├── bowl_01.jpg
│   ├── ...
├── run //放置运行中产生的数据，默认是作者运行的结果
│   ├── calib
│       ├── camera_params.txt
│   ├── light
│       ├── light_source.npy
│   ├── desk_scan
│       ├── point.csv
├── 3dphotography.pdf //原作文章
└── requirements.txt
```
## 运行说明

- 复现我们的结果

先创建一个新的conda环境，python版本为3.8，

    conda create -n env_name python=3.8
    
接着运行如下指令，安装所需要的package，

    pip install -r requirements.txt
    
完成后，若希望直接查看效果可以在下面的链接下载我们计算得到的点云数据point.csv，并置于./run/desk_scan/目录下

[point.csv](http://home.ustc.edu.cn/~llinxiao/point.csv)

接着运行可视化程序即可

    python ./src/visualize.py 

若希望从头开始计算物体点云，可在工程目录下，按照默认参数依次运行以下命令即可

    python ./src/calib.py
    python ./src/light.py
    python ./src/desk_scan.py
    

我们提供的素材都是1920*1080，

运行可能会耗费一一些时间，在我的笔记本上大约10min。
    
- 实现你自己的3D重建

创建环境与安装依赖的过程与上相同。

首先，将用相机拍摄的棋盘格。由于后续需要固定相机的外参，所以在移动相机拍摄棋盘格的过程中，请将后续使用的那个相机位姿所拍摄的棋盘格图片命名为最小，例如，calib_1.jpg，拍摄的所有图片置于./calib/目录下。注意，这一步对光源没有要求，尽量照亮桌面即可。

标定好之后，相机位置在接下来不能发生改变。

接下来，在桌面上的不同位置竖直放置笔，拍摄图片，并且测量笔的长度（单位：mm）。将拍摄的图片置于./light/目录下，同时，人工标注笔尖阴影与笔底座在各个图像中的像素位置，修改light.py中的对应内容。

最后，拍摄阴影扫过物体的图片序列，将它们存放在./bowl/目录下（你也可以起你喜欢的名字，但需要修改文件的默认参数）。

运行

    python ./src/calib.py --pattern_width pattern_width --pattern_height pattern_height --pattern_size pattern_size
    python ./src/light.py --pencil_height pencil_height
    python ./src/desk_scan.py --row_top row_top --row_bottom row_bottom
    
其中，pattern_width与pattern_height对应棋盘格中内角点的数目，如果您不理解这两个参数的意思，可以查看我们上面拍摄的棋盘格图像，那张图像中，pattern_width=9，pattern_height=6。pattern_size是每个正方形格子对应的真实边长（单位：mm），pencil_height为笔的高度（单位：mm）。row_top和row_bottom为上下参考线的y坐标。

几分钟后，您就可以得到重建结果了。

## 参数说明

- calib.py

```text
  --calib   相机标定图像所在文件夹，默认为 ./calib
  --pattern_width   棋盘格中内角点在x方向上的个数，默认为 9
  --pattern_height    棋盘格中内角点在x方向上的个数，默认为 6
  --pattern_size    棋盘格正方形边长（单位：mm），默认为28
  --saving    标定结果的保存目录，默认为 ./run/calib
```

- light.py

```text
  --light   光源估计素材图像所在文件夹，默认为 ./light
  --camera_params  相机参数所在位置，默认为./run/calib/camera_params.txt
  --pencil_height    笔的高度（单位：mm），默认为132.8
  --saving    光源估计结果的保存目录，默认为 ./run/light
```

- desk_scan.py

```text
  --image   物体扫描素材所在文件夹，默认为 ./bowl
  --camera_params  相机参数所在位置，默认为 ./run/calib/camera_params.txt
  --light_source 光源估计结果，默认为 ./run/light/light_source.npy
  --row_top 上参考线对应像素y坐标，默认为 200
  --row_bottom 下参考线对应像素y坐标，默认为 1000
  --threshold    前面提到的阈值，默认为 50
  --postprocess    是否进行后处理，默认为 True
  --saving    物体点云保存目录，默认为 ./run/desk_scan
```
- visualize.py
```text
  --point 点云数据文件，默认为 ./run/desk_scan/point.csv
```



    
