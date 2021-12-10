## OVERVIEW

3D photography on your desk 

VERSION_1.0

作者目前需要准备期末考试和其他任务，1-2周后完善README

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
