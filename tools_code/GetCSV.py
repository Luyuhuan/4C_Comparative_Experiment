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
testpiccsv = r'C:\Users\wh\Desktop\ChoosePic\NeedTest\Choose_All\Choose_retinanet.csv'
testpictxtcsv = open(testpiccsv,'w', encoding="utf-8",newline ='')
writer = csv.writer(testpictxtcsv)
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
                    writer.writerow([file_dir + '/' +str(x),xmin,ymin,xmax,ymax,class_mapping_1[classname[i]]])
    if os.path.isdir(path):
        list_dir(path)
list_dir(r'C:\Users\wh\Desktop\ChoosePic\NeedTest\Choose_All')