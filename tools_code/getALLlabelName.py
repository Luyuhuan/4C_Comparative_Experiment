#coding=utf-8
import cv2
import re
import codecs
import os
import json
import numpy as np
import shutil
savepathlabels = '/data/lyh/4C_ABP_code/GetPic/STDpic_label/'
os.makedirs(savepathlabels)
class_mapping_1 = {'左心房':'LA','左心室':'LV','右心房':'RA','右心室':'RV',
                   '室间隔':'IVS','肋骨':'RIB','降主动脉':'DA','脊柱':'SP',
                   '心尖四腔心切面心脏':'A4C','胸骨旁四腔心切面心脏':'P4C','心底四腔心切面心脏':'B4C'}
classes=['LA','LV','RA','RV','IVS','RIB','DA','SP','A4C','P4C','B4C']
realpic = 'STD_list.txt'
realpictxt = open(realpic,'w', encoding="utf-8")
def list_dir(file_dir):
  dir_list = os.listdir(file_dir)
  for cur_file in dir_list:
    path = file_dir+'/'+cur_file
    if os.path.isfile(path) and cur_file == 'annotations.json':
        f = open(path,encoding='utf-8')
        frame = json.load(f)
        annotations = frame["annotations"]
        for x in annotations:
            if not os.path.exists(file_dir+'/'+x):
                print(file_dir+x+"不存在")
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
            realpictxt.writelines(file_dir+'/'+x + '\n')
            labeltxt=savepathlabels+x[:-4]+'.txt'
            writetxtlabeltxt = open(labeltxt,'w', encoding="utf-8")
            image=cv2.imdecode(np.fromfile(file_dir+'/' + str(x),dtype=np.uint8),-1)
            sp = image.shape
            height = sp[0]
            width = sp[1]
            picsize = (width,height)
            for i in range(len(classname)):
                if classname[i] in class_mapping_1:
                    xmin=(locationstart[i].split(',')[0])
                    ymin=(locationstart[i].split(',')[1])
                    xmax=(locationend[i].split(',')[0])
                    ymax=(locationend[i].split(',')[1])
                    bb = (xmin,ymin,xmax,ymax)
                    writetxtlabeltxt.writelines(str(class_mapping_1[classname[i]])+ " " + " ".join([str(a) for a in bb]) + '\n')
    if os.path.isdir(path):
        list_dir(path)
list_dir(r'/data/lyh/4C_ABP_code/GetPic/STDpic')