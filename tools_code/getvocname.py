import csv
import os
import cv2
import numpy as np
# 读取csv至字典
csvFile1 = open("E:/hnumedical/Compare_code/keras-retinanet-master/keras-retinanet-master/keras_retinanet/CSV/test_annotations.csv", "r",encoding='utf-8')
reader = csv.reader(csvFile1)
# 写入数据
csvFile2 = open("E:/hnumedical/Compare_code/keras-retinanet-master/keras-retinanet-master/keras_retinanet/CSV/test_annotations1.csv", "w",encoding='utf-8',newline ='')
writer = csv.writer(csvFile2)
picpath = 'E:/hnumedical/Compare_data/test_4C_3VT_RVOT_LVOT_SA_LR_heart_pic/'
for item in reader:
    if not os.path.exists(picpath+item[0]):
        print(picpath+item[0],'不存在')
        continue
    xmin=int(float(item[1])-1)
    ymin=int(float(item[2])-1)
    xmax=int(float(item[3])+1)
    ymax=int(float(item[4])+1)
    print(item[0])
    #img = cv2.imread(picpath+item[0])
    img = cv2.imdecode(np.fromfile(picpath+item[0], dtype=np.uint8), -1)
    print(type(img))
    sp = img.shape
    xmin=max(xmin,0)
    ymin=max(ymin,0)
    xmax=min(xmax,sp[1])
    ymax=min(ymax,sp[0])
    writer.writerow([picpath+item[0],xmin,ymin,xmax,ymax,class_mapping[item[5]]])
csvFile1.close()
csvFile2.close()
