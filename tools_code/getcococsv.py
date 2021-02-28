#coding=utf-8
import cv2
import re
import codecs
import os
import json
import numpy as np
import shutil
import csv
class_mapping_1 = {'左心房':'LA','左心室':'LV','右心房':'RA','右心室':'RV',
                   '室间隔':'IVS','肋骨':'RIB','降主动脉':'DA','脊柱':'SP',
                   '心尖四腔心切面心脏':'A4C','胸骨旁四腔心切面心脏':'P4C','心底四腔心切面心脏':'B4C'}
classes=['LA','LV','RA','RV','IVS','RIB','DA','SP','A4C','P4C','B4C']
testpic = 'C:/Users/wh/Desktop/ChoosePic/NeedTest/Choose_All/all_coco.csv'
testpictxtcsv = open(testpic,'w', encoding="utf-8",newline ='')
writer = csv.writer(testpictxtcsv)
title = ["filename","x1","y1","x2","y2","bodypart"]
writer.writerow(title)
def list_dir(file_dir):
  dir_list = os.listdir(file_dir)
  for cur_file in dir_list:
    path = file_dir+'/'+cur_file
    if os.path.isfile(path) and cur_file == 'annotations.json':
        f = open(path,encoding='utf-8')
        frame = json.load(f)
        annotations = frame["annotations"]
        for x in annotations:
            if not os.path.exists(file_dir + '/' + x):
                continue
            classname = []
            locationstart = []
            locationend = []
            flag =0
            classany = annotations[x]['bodyPart']
            for y in annotations[x]['annotations'] :
                flag = 1
                if y['name'] == '心脏' :
                    classname.append(classany + y['name'])
                else:
                    classname.append(y['name'])
                locationstart.append(y['start'])
                locationend.append(y['end'])
            if flag == 0:
                print(file_dir+'/'+x,'没有标注')
                continue
            image = cv2.imdecode(np.fromfile(file_dir + '/' + str(x), dtype=np.uint8), -1)
            sp = image.shape
            height = sp[0]
            width = sp[1]
            writelist = []
            writelist.append(str(x))
            for i in range(len(classname)):
                if classname[i] in class_mapping_1:
                    xmin = (locationstart[i].split(',')[0])
                    ymin = (locationstart[i].split(',')[1])
                    xmax = (locationend[i].split(',')[0])
                    ymax = (locationend[i].split(',')[1])
                    xmin = max(int(float(xmin)-1),0)
                    ymin = max(int(float(ymin)-1),0)
                    xmax = min(int(float(xmax)+1),width)
                    ymax = min(int(float(ymax)+1),height)
                    writelist.append(str(xmin))
                    writelist.append(str(ymin))
                    writelist.append(str(xmax))
                    writelist.append(str(ymax))
                    writelist.append(class_mapping_1[classname[i]])
            writer.writerow(writelist)
    if os.path.isdir(path):
        list_dir(path)
list_dir('C:/Users/wh/Desktop/ChoosePic/NeedTest/Choose_All')