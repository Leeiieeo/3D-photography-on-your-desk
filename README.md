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

## 代码实现

整体来说，代码是基于numpy和opencv实现的。

- calib.py 

调用的opencv-python中的
```python
ret, mtx, dist, rvecs, tvecs = \
    cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
```
进行相机标定。值得一提的是，我们在后面所有的计算中都忽略了镜头畸变，原因是手机相机本身畸变就不明显，而且由于棋盘格的纸摆放不是完全平整的，所以会使得结果中畸变系数被放大，实际上是几乎没有畸变的，如果您的镜头畸变较大，可以取消源代码中下面这行的注释，进行畸变校正:

```python
mtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (u, v), 0, (u, v))
```
- light.py 

该部分进行光源估计。首先，我们需要定义相机类进行各个坐标系的转换
```python
class Camera():
    def __init__(self,intrinsics,extrinsics_R,extrinsics_T,distort):
        self.intrinsics = intrinsics
        self.extrinsics_R = extrinsics_R
        self.extrinsics_T = extrinsics_T
        self.distort = distort
        self.camera_center = np.dot(np.linalg.inv(camera_extrinsics_R),-camera_extrinsics_T)

    def camera2world(self,camera):
        return np.dot(np.linalg.inv(self.extrinsics_R), (camera - self.extrinsics_T))
    
    def pixel2camera(self,pixel):
        p = np.array([pixel[0],pixel[1],1]).reshape(3,1)
        return np.dot(np.linalg.inv(self.intrinsics),p)
    
    def pixel2world(self,pixel): #pixel[0]像素x坐标，pixel[1]像素y坐标
        camera = self.pixel2camera(pixel)
        return self.camera2world(camera)
    
    def world2camera(self,world):
        w = np.array([world[0],world[1],world[2]]).reshape(3,1)
        camera = np.dot(self.extrinsics_R,w) + self.extrinsics_T
        return camera
    
    def camera2pixel(self,camera):
        p = np.dot(self.intrinsics,camera) / camera[2]
        return p[:2]
    
    def world2pixel(self,world):
        camera = self.world2camera(world)
        return self.camera2pixel(camera)
```
接下来，我们需要定义一些与立体几何有关的函数，用于计算直线与直线，直线与平面的交点
```python
def find_intersection_point_lp(p1,p2,a,b,c,d): #查找经过p1,p2的直线与参数为a,b,c,d的平面的交点
    #全是数学推导
    plane_normal = np.array([a, b, c])
    n = - (np.vdot(p1,plane_normal) + d) / np.vdot((p2-p1),plane_normal)
    return p1 + n*(p2-p1)
    
def find_intersection_ll(a,b,c,d): #查找a,b组成的直线和c,d组成的直线的交点的最小二乘解
    #全是数学推导
    n = np.cross((b-a),(d-c))
    m1 = (d[1]-c[1])/(b[1]-a[1]) - (d[0] - c[0])/(b[0] - a[0])
    m2 = n[1]/(b[1]-a[1]) - n[0] / (b[0]-a[0])
    p1 = (d[2] - c[2]) / (b[2] - a[2]) - (d[0] - c[0]) / (b[0] - a[0])
    p2 = n[2] / (b[2] - a[2]) - n[0] / (b[0] - a[0])
    d1 = (c[0] - a[0])/(b[0] - a[0]) - (c[1] - a[1])/(b[1] - a[1])
    d2 = (c[0] - a[0])/(b[0] - a[0]) - (c[2] - a[2])/(b[2] - a[2])
    k1 = (d1*p2 - d2*m2) / (m1 * p2 - p1*m2)
    k2 = (m1*d2 - d1*p1) / (m1*p2 - m2*p1)
    return c + k1 * (d - c) + 0.5*k2*n
```
在光源估计的过程中，我们需要找到每幅图像中笔尖的影子、笔的底座的像素位置，实际上这对于图像处理来说这不是一个简单的任务（至少对我们来说不简单），在上面给出的例子中对应是下图中两个红色的点，

![image](https://github.com/USTC-Computer-Vision-2021/project-cv_lx-nyx/blob/main/img/tip_base.PNG)

我们采用的是人工标注的方法，在代码中加入这些图像对应两个点的位置，所以说如果您想对新拍的照片进行复现的话，需要修改代码中下面这两个数组
```python
# 人工标注的数据
tip = np.array([[656,32],[267,671],[1142,381],[1522,624],[1538,41],
                [1779,130],[1026,45],[1761,807],[1337,650],[465,440],[154,31],[79,589]],dtype=np.float64)
base = np.array([[604,471],[326,936],[960,720],[1234,894],[1247,480],
                 [1424,535],[882,482],[1418,1025],[1107,907],[472,767],[247,474],[190,868]],dtype=np.float64)
```
- desk_scan.py 

该部分进行物体3D扫描。需要先定义读取图片序列的类
```python
class Imageset():
    def __init__(self,path):
        self.image = []
        for root, dirs, files in os.walk(path):
            for file in files:
                img = cv2.imread(root +"/"+ file)
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float64)
                self.image.append(gray)

        self.image = np.array(self.image)
        self.frame_lenth = self.image.shape[0]
        self.frame_height = self.image.shape[1]
        self.frame_width = self.image.shape[2]

    def __getitem__(self, item):
        return self.image[item]
```

代码实现的关键在于，维护两个数组，第一个记录阴影的空间信息，即每一帧时，阴影在上与下参考直线的位置，大小为(帧数,2)；第二个记录阴影到达时间的信息，即阴影到达每一个像素时的当前帧数，大小为(图像高，图像宽)。

```python
# 记录每一帧时，阴影在上与下参考直线的位置，大小为(帧数,2)
spatial_shadow = np.zeros((total_frame,2),dtype=np.float64) 
# 记录阴影到达每一个像素时的当前帧数，大小为(图像高，图像宽)
temporal_shadow = np.zeros((frame_height, frame_width), dtype=np.float64)
```
对于spatial_shadow，我们计算每帧图像上，参考线上的灰度曲线，得到其最大值与最小值的中间点，计算灰度曲线与该点的交点作为此帧下的阴影位置。

对于temporal_shadow，对于一个固定的像素点，我们计算该像素点在整个视频中的灰度变化曲线，同样取其与最大最小值中点的交点作为阴影到达该像素的时间。

下图给出了解释：

![image](https://github.com/USTC-Computer-Vision-2021/project-cv_lx-nyx/blob/main/img/cross.PNG)

对于spatial_shadow，在每帧时遍历上下参考线上的像素即可。

对于temporal_shadow，我们采用的动态维护图像的最大值、最小值、它们的差以及它们的中点，以巧妙的方法只需遍历一次数据就可以得到结果。

```python
I_max = np.zeros((frame_height,frame_width))        # 遍历图片序列时，记录每个像素的最大值
I_min = np.full((frame_height, frame_width), 255)   # 遍历图片序列时，记录每个像素的最小值
I_contrast = np.zeros((frame_height,frame_width))   # 记录当前最大最小值的差
I_shadow = np.zeros((frame_height,frame_width),dtype=np.float64) # 记录当前最大最小值的中点

for frame_index in tqdm(range(total_frame)):
    pre_gray = gray

    gray = imageset[frame_index]

    t_t = (np.max(gray[row_top,:]) + np.min(gray[row_top,:])) / 2
    t_d = (np.max(gray[row_down,:]) + np.min(gray[row_down,:])) / 2
    # 计算spatial_shadow
    # 目标：找到row_top,row_down的第一个zero-crossing,对应阴影左侧的边界
    for i in range(frame_width):
        if gray[row_top,i] >= t_t and gray[row_top,i+1] < t_t:
            spatial_shadow[frame_index,0] = i + (gray[row_top,i] - t_t) / (gray[row_top,i] - gray[row_top,i+1])
            break
    for i in range(frame_width):
        if gray[row_down,i] >= t_d and gray[row_down,i+1] < t_d:
            spatial_shadow[frame_index,1] = i + (gray[row_down,i] - t_t) / (gray[row_down,i] - gray[row_down,i+1])
            break

    I_max = (np.max(np.concatenate((I_max[np.newaxis, :], gray[np.newaxis, :]), 0), 0))
    I_min = (np.min(np.concatenate((I_min[np.newaxis, :], gray[np.newaxis, :]), 0), 0))
    I_contrast = I_max - I_min
    I_shadow = (I_max + I_min) / 2

    # 计算temporal_shadow
    # 循环效率低下，待优化
    for row in range(frame_height):
        for col in range(frame_width):
            if I_contrast[row,col] >= threshold and \
                pre_gray[row,col] <= I_shadow[row,col] and gray[row,col] > I_shadow[row,col]:
                temporal_shadow[row,col] = frame_index - (gray[row,col] - I_shadow[row,col]) / \
                                           (gray[row,col] - pre_gray[row,col])
```

如果在spatial_shadow计算中选择了左交点，temporal_shadow就必须选择右交点（您可以想想这是为什么）

我们在上述两个数组的计算中采样了亚像素精度(subpixel accuracy)，使用线性内插得到最终结果。

有了这两个数据后，就可以对每一个像素，得到阴影到达该像素的时间，同时得到此时阴影的位置，就可以按照上述原理计算这个3D点的世界坐标了。

在整个过程中，如果一个像素点最大灰度与最小灰度小于某个阈值，意味着这个像素本来就位于物体的阴影之中，在这个方法下无法提供深度信息，所以会被抛弃。

我们还对生成的点云数据进行了后处理，删去了其中偏差较大的点。

最后，我们借助open3d对点云进行可视化

```python
point_cloud = open3d.geometry.PointCloud()
point_cloud.points = open3d.utility.Vector3dVector(point)
open3d.visualization.draw_geometries([point_cloud])
```

更多细节请查看源代码。

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
    
完成后，若希望直接查看效果，运行

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



    
