import pickle as pkl
import numpy as np
import cv2
import argparse

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
def find_intersection_point_lp(p1,p2,a,b,c,d): #查找经过p1,p2的直线与参数为a,b,c,d的平面的交点
    #全是数学推导
    plane_normal = np.array([a, b, c])
    n = - (np.vdot(p1,plane_normal) + d) / np.vdot((p2-p1),plane_normal)
    return p1 + n*(p2-p1)
def find_intersection_ll(a,b,c,d): #查找a,b c,d组成的直线的交点的最优解
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

parser = argparse.ArgumentParser()
parser.add_argument("--light",type=str,default="./light")
parser.add_argument("--camera_params",type = str, default="./run/calib/camera_params_2.txt")
parser.add_argument("--pencil_height",type = float, default = 132.8)
parser.add_argument("--saving",type=str,default="./run/light")
args = parser.parse_args()

file_calib = args.camera_params
with open(file_calib,"rb+") as f:
    params = pkl.load(f)

ret = params["ret"]
mtx = params["mtx"]
dist = params["dist"]
rvece = params["rvece"]
tvecs = params["tvecs"]
newcameramtx = params["newcameramtx"]
pencil_height = args.pencil_height


camera_intrinsics = params["mtx"]
# camera_intrinsics = newcameramtx
camera_distort = params["dist"]
camera_extrinsics_R,_ = cv2.Rodrigues(params["rvece"][0])
camera_extrinsics_T = params["tvecs"][0]

# print(camera_intrinsics)
# print(camera_distort)
# print(camera_extrinsics_R)
# print(camera_extrinsics_T.shape)
camera = Camera(camera_intrinsics,camera_extrinsics_R,camera_extrinsics_T,camera_distort)
# 计算相机中心在世界坐标系下的位置
# print(camera.camera_center)

tip = np.array([[656,32],[267,671],[1142,381],[1522,624],[1538,41],[1779,130],[1026,45],[1761,807],[1337,650],[465,440],[154,31],[79,589]],dtype=np.float64)
base = np.array([[604,471],[326,936],[960,720],[1234,894],[1247,480],[1424,535],[882,482],[1418,1025],[1107,907],[472,767],[247,474],[190,868]],dtype=np.float64)

tip_in_camera = np.zeros((tip.shape[0],3),dtype=np.float64)
base_in_camera = np.zeros((tip.shape[0],3),dtype=np.float64)
# print(tip.shape)
# print(base.shape)
# print(camera.pixel2world(tip[0,:]))
for i in range(tip.shape[0]):
    tip_in_camera[i,:] = camera.pixel2world(tip[i,:]).reshape(3)
    base_in_camera[i,:] = camera.pixel2world(base[i,:]).reshape(3)

# print(tip_in_camera)
# print(base_in_camera)

tip_in_world = np.zeros((tip.shape[0],3),dtype=np.float64)
base_in_world = np.zeros((tip.shape[0],3),dtype=np.float64)

for i in range(tip_in_camera.shape[0]):
    tip_in_world[i,:] = find_intersection_point_lp(camera.camera_center.reshape(3),tip_in_camera[i,:],0,0,1,0)
    base_in_world[i, :] = find_intersection_point_lp(camera.camera_center.reshape(3), base_in_camera[i, :], 0, 0, 1, 0)
# print(tip_in_world)
tip_pencil = base_in_world
tip_pencil[:,2] = -pencil_height
# print(tip_pencil)
intersection = np.zeros((int(tip_pencil.shape[0]*(tip_pencil.shape[0]-1)/2),3),dtype=np.float64)
count = 0
for i in range(tip_pencil.shape[0]):
    for j in range(i+1,tip_pencil.shape[0]):
        intersection[count,:]=(find_intersection_ll(tip_pencil[i,:],tip_in_world[i,:],tip_pencil[j,:],tip_in_world[j,:]))
        count+=1
print("coordinate of light source:")
print(intersection)
light_source_estimate = np.mean(intersection,0)
print(f"light_source_estimate: {light_source_estimate}")
light_file = args.saving + "/light_source_2.npy"


np.save(light_file,light_source_estimate)
print(f"saving: "+ light_file)
