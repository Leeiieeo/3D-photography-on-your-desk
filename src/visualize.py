import numpy as np
from open3d import*
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--point",type=str,default='./run/desk_scan/point.csv')
args = parser.parse_args()


print("loading point cloud...")
point = np.loadtxt(args.point,dtype = np.float64,delimiter=',')
print("done")


point_cloud = open3d.geometry.PointCloud()
point_cloud.points = open3d.utility.Vector3dVector(point)
open3d.visualization.draw_geometries([point_cloud])



