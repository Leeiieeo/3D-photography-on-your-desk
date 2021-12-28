import pickle as pkl
import numpy as np
import cv2
import os
from tqdm import tqdm
import argparse
from open3d import*
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

    def get_shadowplane(self,p1,p2,light_source):
        p1c = self.pixel2world(p1)
        p2c = self.pixel2world(p2)
        p1w = find_intersection_point_lp(self.camera_center, p1c , 0,0,1,0)
        p2w = find_intersection_point_lp(self.camera_center, p2c , 0, 0, 1, 0)
        a,b,c,d = point2plane(p1w,p2w,light_source)
        return a,b,c,d

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

def find_intersection_point_lp(p1,p2,a,b,c,d): #查找经过p1,p2的直线与参数为a,b,c,d的平面的交点
    #全是数学推导
    plane_normal = np.array([a, b, c])
    n = - (np.vdot(p1,plane_normal) + d) / np.vdot((p2-p1),plane_normal)
    return p1 + n*(p2-p1)
def point2plane(p1,p2,p3):
    a = p1[1]*(p2[2] - p3[2]) + p2[1]*(p3[2] - p1[2]) + p3[1]*(p1[2] - p2[2])
    b = p1[2]*(p2[0] - p3[0]) + p2[2]*(p3[0] - p1[0]) + p3[2]*(p1[0] - p2[0])
    c = p1[0]*(p2[1] - p3[1]) + p2[0]*(p3[1] - p1[1]) + p3[0]*(p1[1] - p2[1])
    d = -p1[0]*(p2[1]*p3[2] - p3[1]*p2[2]) - p2[0]*(p3[1]*p1[2] - p1[1]*p3[2]) - p3[0]*(p1[1]*p2[2] - p2[1]*p1[2])
    return a,b,c,d

parser = argparse.ArgumentParser()
parser.add_argument("--image",type=str,default="./bowl")
parser.add_argument("--camera_params",type = str, default="./run/calib/camera_params.txt")
parser.add_argument("--light_source",type=str,default="./run/light/light_source.npy")
parser.add_argument("--row_top",type=int,default=200)
parser.add_argument("--row_bottom",type=int,default=1000)
parser.add_argument("--threshold",type=int,default=50)
parser.add_argument("--postprocess",type=bool,default=True)
parser.add_argument("--saving",type=str,default="./run/desk_scan")
args = parser.parse_args()

image_path = args.image
print("loading images...")
imageset = Imageset(image_path)
print("done")
frame_width = imageset.frame_width
frame_height = imageset.frame_height
total_frame = imageset.frame_lenth
print(f"frame_width: {frame_width}")
print(f"frame_height: {frame_height}")
print(f"total_frame: {total_frame}")

file_calib = args.camera_params
with open(file_calib,"rb+") as f:
    params = pkl.load(f)

ret = params["ret"]
mtx = params["mtx"]
dist = params["dist"]
rvece = params["rvece"]
tvecs = params["tvecs"]
newcameramtx = params["newcameramtx"]
camera_intrinsics = params["mtx"]
# camera_intrinsics = newcameramtx
camera_distort = params["dist"]
camera_extrinsics_R,_ = cv2.Rodrigues(params["rvece"][0])
camera_extrinsics_T = params["tvecs"][0]

camera = Camera(camera_intrinsics,camera_extrinsics_R,camera_extrinsics_T,camera_distort)

file_light = args.light_source
light_source = np.load(file_light)

row_top = args.row_top
row_down = args.row_bottom
threshold = args.threshold

# 记录每一帧时，阴影在上与下参考直线的位置，大小为(帧数,2)
spatial_shadow = np.zeros((total_frame,2),dtype=np.float64) #左边沿当作阴影

I_max = np.zeros((frame_height,frame_width))
I_min = np.full((frame_height, frame_width), 255)
I_contrast = np.zeros((frame_height,frame_width))
I_shadow = np.zeros((frame_height,frame_width),dtype=np.float64)

# 记录阴影到达每一个像素时的当前帧数，大小为(图像高，图像宽)
temporal_shadow = np.zeros((frame_height, frame_width), dtype=np.float64)

pre_gray = imageset[0]  #上一帧的灰度图像
gray = imageset[0]      #当前帧的灰度图像

print("processing images...")
for frame_index in tqdm(range(total_frame)):
    pre_gray = gray

    gray = imageset[frame_index]

    # print(np.min(gray[row_top,:]))
    # print(np.min(gray[row_down,:]))
    t_t = (np.max(gray[row_top,:]) + np.min(gray[row_top,:])) / 2
    t_d = (np.max(gray[row_down,:]) + np.min(gray[row_down,:])) / 2
    # print(t_t,t_d)


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

    #待优化
    for row in range(frame_height):
        for col in range(frame_width):
            if I_contrast[row,col] >= threshold and \
                pre_gray[row,col] <= I_shadow[row,col] and gray[row,col] > I_shadow[row,col]:
                temporal_shadow[row,col] = frame_index - (gray[row,col] - I_shadow[row,col]) / \
                                           (gray[row,col] - pre_gray[row,col])

print("calculating point cloud data...")
point = []
for row in tqdm(range(frame_height)): # 0-1079
    for col in range(frame_width):  # 0-1919
        if not (temporal_shadow[row,col]==0):
            floor = int(np.floor(temporal_shadow[row,col]))  #阴影扫过该像素的帧序号
            ceil = int(np.ceil(temporal_shadow[row,col]))   #计算ceil平面和floor平面
            top_floor = spatial_shadow[floor,0]
            down_floor = spatial_shadow[floor,1]

            top_ceil = spatial_shadow[ceil,0]
            down_ceil = spatial_shadow[ceil, 1]

            a1, b1, c1, d1 = camera.get_shadowplane([top_floor,row_top],[down_floor,row_down],light_source)#floor平面
            a2, b2, c2, d2 = camera.get_shadowplane([top_ceil,row_top], [down_ceil,row_down], light_source)#ceil平面

            # shadow plane，由线性内插得到
            a = a1 * (ceil - temporal_shadow[row,col]) + a2 * (temporal_shadow[row,col] - floor)
            b = b1 * (ceil - temporal_shadow[row,col]) + b2 * (temporal_shadow[row,col] - floor)
            c = c1 * (ceil - temporal_shadow[row,col]) + c2 * (temporal_shadow[row,col] - floor)
            d = d1 * (ceil - temporal_shadow[row,col]) + d2 * (temporal_shadow[row,col] - floor)

            current = camera.pixel2world([col,row])
            g = find_intersection_point_lp(current, camera.camera_center, a, b, c, d)
            point.append(g)

point = np.array(point)
point = np.squeeze(point)
if args.postprocess:
    index = point[:, 2] > 30
    point = np.delete(point, index, axis=0)
    index = point[:, 2] < -60
    point = np.delete(point, index, axis=0)
    point[:, 2] = -point[:, 2]



np.savetxt(args.saving + "/point.csv", point, delimiter=',')


point_cloud = open3d.geometry.PointCloud()
point_cloud.points = open3d.utility.Vector3dVector(point)
open3d.visualization.draw_geometries([point_cloud])

