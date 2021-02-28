import os
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
#from scipy.misc import imread
import cv2

filepath = r'E:/hnumedical/4C_ABP/test'  # 数据集目录
pathDir = os.listdir(filepath)

R_channel = 0
G_channel = 0
B_channel = 0
num = 0
for idx in range(len(pathDir)):
    filename = pathDir[idx]
    if filename[-4:] != '.jpg':
        print(filename,'not pic')
        continue
    img = cv2.imdecode(np.fromfile(os.path.join(filepath, filename), dtype=np.uint8), -1)
    #img = imread(os.path.join(filepath, filename))
    sp = img.shape
    img = img / 255.0
    try:
        R_channel = R_channel + np.sum(img[:, :, 0])
        G_channel = G_channel + np.sum(img[:, :, 1])
        B_channel = B_channel + np.sum(img[:, :, 2])
        # print('R_channel:',np.sum(img[:, :, 0]))
        # print('G_channel:',np.sum(img[:, :, 1]))
        # print('B_channel:',np.sum(img[:, :, 2]))
        # print('sp[0]+sp[1]:',sp[0]+sp[1])
        num = num + sp[0]+sp[1]
    except:
        R_channel = R_channel + 0
        G_channel = G_channel + 0
        B_channel = B_channel + 0


#num = len(pathDir) * 512 * 512  # 这里（512,512）是每幅图片的大小，所有图片尺寸都一样
R_mean = R_channel / num
G_mean = G_channel / num
B_mean = B_channel / num

R_channel = 0
G_channel = 0
B_channel = 0
for idx in range(len(pathDir)):
    filename = pathDir[idx]
    if filename[-4:] != '.jpg':
        print(filename,'not pic')
        continue
    #img = imread(os.path.join(filepath, filename)) / 255.0
    img = cv2.imdecode(np.fromfile(os.path.join(filepath, filename), dtype=np.uint8), -1) / 255.0
    try:
        R_channel = R_channel + np.sum((img[:, :, 0] - R_mean) ** 2)
        G_channel = G_channel + np.sum((img[:, :, 1] - G_mean) ** 2)
        B_channel = B_channel + np.sum((img[:, :, 2] - B_mean) ** 2)
    except:
        R_channel = R_channel + 0
        G_channel = G_channel + 0
        B_channel = B_channel + 0
R_var = np.sqrt(R_channel / num)
G_var = np.sqrt(G_channel / num)
B_var = np.sqrt(B_channel / num)
print("R_mean is %f, G_mean is %f, B_mean is %f" % (R_mean, G_mean, B_mean))
print("R_var is %f, G_var is %f, B_var is %f" % (R_var, G_var, B_var))