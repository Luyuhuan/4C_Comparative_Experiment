#coding=utf-8
import cv2
import re
import codecs
import os
import json
import numpy as np
import shutil
import csv
savetrainpathlabels = 'E:/hnumedical/Compare_4CHeartData/train_4C_label'
savetrainpathpic = 'E:/hnumedical/Compare_4CHeartData/train_4C_pic'
savevalpathlabels = 'E:/hnumedical/Compare_4CHeartData/val_4C_label'
savevalpathpic = 'E:/hnumedical/Compare_4CHeartData/val_4C_pic'
savetestpathlabels = 'E:/hnumedical/Compare_4CHeartData/test_4C_label'
savetestpathpic = 'E:/hnumedical/Compare_4CHeartData/test_4C_pic'
os.makedirs(savetrainpathlabels)
os.makedirs(savetrainpathpic)
os.makedirs(savevalpathlabels)
os.makedirs(savevalpathpic)
os.makedirs(savetestpathlabels)
os.makedirs(savetestpathpic)
# PIC = '/home/ultrasonic/hnumedical/ImageWare/am_heart/dataALL-0626-real'
# 四腔心水平横切面：
# 左心房、左心室、右心房、右心室、房室间隔十字交叉、室间隔、降主动脉、脊柱、肋骨
# 右室流出道切面:
# 右心室、右室流出道及主肺动脉、主动脉弓、升主动脉、降主动脉、上腔静脉、脊柱
# 3VT切面：
# 主动脉弓、主肺动脉及动脉导管、气管、上腔静脉、降主动脉、脊柱
# 左室流出道切面
# 左心室、右心室、室间隔、左室流出道及主动脉、脊柱
# 心底短轴切面   Short-axis
# 右心室、右心房、主肺动脉及动脉导管、升主动脉、降主动脉、脊柱、右肺动脉
class_mapping_1={'左心室':'LV','左心房':'LA','右心室':'RV','右心房':'RA',
                 '室间隔':'IVS','肋骨':'RIB','降主动脉':'DA','脊柱':'SP',
                 '房室间隔十字交叉':'RC','主肺动脉及动脉导管':'MPA','主动脉弓':'AOA','上腔静脉':'SVC',
                 '气管':'TC','升主动脉':'ASA','右室流出道及主肺动脉':'MPA','左室流出道及主动脉':'LMPA',
                 '右肺动脉':'RPA',
                 '3VT切面心脏':'3VT','四腔心水平横切面心脏':'4C','右室流出道切面心脏':'RVOT','左室流出道切面心脏':'LVOT','心底短轴切面心脏':'SA'}
QieMian = { '四腔心水平横切面':'四腔心水平横切面', '心底四腔心切面':'四腔心水平横切面',
            '胸骨旁四腔心切面':'四腔心水平横切面', '心尖四腔心切面':'四腔心水平横切面'}
CountQieMian = {'四腔心水平横切面':0}
CountQieMianALL = {'四腔心水平横切面':0}
classes=['LV', 'LA', 'RV', 'RA', 'IVS', 'RIB', 'DA', 'SP', 'RC','4C']

trainpic = 'E:/hnumedical/Compare_4CHeartData/train_4C.txt'
trainpictxt = open(trainpic,'w', encoding="utf-8")
valpic = 'E:/hnumedical/Compare_4CHeartData/val_4C.txt'
valpictxt = open(valpic,'w', encoding="utf-8")
testpic = 'E:/hnumedical/Compare_4CHeartData/test_4C.txt'
testpictxt = open(testpic,'w', encoding="utf-8")
trainpiccsv = 'E:/hnumedical/Compare_4CHeartData/train4C.csv'
trainpictxtcsv = open(trainpiccsv,'w', encoding="utf-8",newline ='')
valpiccsv = 'E:/hnumedical/Compare_4CHeartData/val4C.csv'
valpictxtcsv = open(valpiccsv,'w', encoding="utf-8",newline ='')
testpiccsv = 'E:/hnumedical/Compare_4CHeartData/test4C.csv'
testpictxtcsv = open(testpiccsv,'w', encoding="utf-8",newline ='')
allpic = []
def convert(size, box):
    dw = 1./size[0]
    dh = 1./size[1]
    x = (box[0] + box[1])/2.0
    y = (box[2] + box[3])/2.0
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x*dw
    w = w*dw
    y = y*dh
    h = h*dh
    return (x,y,w,h)
def list_dir(file_dir):
  dir_list = os.listdir(file_dir)
  print(file_dir)
  for cur_file in dir_list:
    # 获取文件的绝对路径
    path = file_dir+'/'+cur_file
    #print(path)
    STD_NSTD = path.split('/')[-3]
    QieMianName = path.split('/')[-2]
    if os.path.isfile(path) and cur_file == 'annotations.json':
        #reallabel = path.split('/')[-2]
        f = open(path,encoding='utf-8')
        frame = json.load(f)
        annotations = frame["annotations"]
        for x in annotations:
            #if not os.path.exists(PIC + '/'+ STD_NSTD + '/'+QieMianName +'/'+x):
            if not os.path.exists(file_dir + '/' + x):
                continue
            if annotations[x]['bodyPart'] not in QieMian:
                continue
            if x in allpic:
                print(x,'已经存在')
                continue
            allpic.append(x)
            classname = []
            locationstart = []
            locationend = []
            flag =0
            for y in annotations[x]['annotations'] :
                flag = 1
                if y['name'] == '心脏':
                    classname.append(QieMian[annotations[x]['bodyPart']]+y['name'])
                else:
                    classname.append(y['name'])
                locationstart.append(y['start'])
                locationend.append(y['end'])
            if flag == 0:
                continue
                print(x)
            writer = csv.writer(trainpictxtcsv)
            PicQieMianName =QieMian[annotations[x]['bodyPart']]
            CountQieMianALL[PicQieMianName] = CountQieMianALL[PicQieMianName] +1
            if CountQieMian[PicQieMianName] <1000 and annotations[x]['standard'] == "标准":
                shutil.copy(file_dir + '/' + x,savetestpathpic+'/' + str(x))
                labeltxt=savetestpathlabels+'/'+x[:-4]+'.txt'
                testpictxt.writelines(savetestpathpic+'/' + str(x)+ '\n')
                image=cv2.imdecode(np.fromfile(savetestpathpic+'/' + x,dtype=np.uint8),-1)
                writer = csv.writer(testpictxtcsv)
                CountQieMian[PicQieMianName] = CountQieMian[PicQieMianName] +1
            elif CountQieMian[PicQieMianName] >=1000 and CountQieMian[PicQieMianName] <2000 and annotations[x]['standard'] == "标准":
                shutil.copy(file_dir + '/' + x,savevalpathpic+'/' + str(x))
                labeltxt=savevalpathlabels+'/'+x[:-4]+'.txt'
                valpictxt.writelines(savevalpathpic+'/' + str(x)+ '\n')
                image=cv2.imdecode(np.fromfile(savevalpathpic+'/' + x,dtype=np.uint8),-1)
                writer = csv.writer(valpictxtcsv)
                CountQieMian[PicQieMianName] = CountQieMian[PicQieMianName] +1
            else:
                shutil.copy(file_dir + '/' + x,savetrainpathpic+'/' + str(x))
                labeltxt=savetrainpathlabels+'/'+x[:-4]+'.txt'
                trainpictxt.writelines(savetrainpathpic+'/' + str(x) + '\n')
                image=cv2.imdecode(np.fromfile(savetrainpathpic+'/' + x,dtype=np.uint8),-1)
                writer = csv.writer(trainpictxtcsv)
            writetxtlabeltxt = open(labeltxt,'w', encoding="utf-8")
            #print(file_dir+'/' + x)
            #print(image)
            sp = image.shape
            height = sp[0]
            width = sp[1]
            picsize = (width,height)
            #print(height,width)
            for i in range(len(classname)):
                #print(classname[i])
                if classname[i] in class_mapping_1:
                    xmin=(locationstart[i].split(',')[0])
                    if float(xmin) < 0:
                        xmin = '0.0'
                    ymin=(locationstart[i].split(',')[1])
                    if float(ymin) < 0:
                        ymin = '0.0'
                    xmax=(locationend[i].split(',')[0])
                    if float(xmax) > width:
                        xmax = str(width)
                    ymax=(locationend[i].split(',')[1])
                    if float(ymax) > height:
                        ymax = str(height)
                    boxxxyy = (float(xmin),float(xmax),float(ymin),float(ymax))
                    bb = convert(picsize, boxxxyy)
                    writetxtlabeltxt.writelines(str(classes.index(class_mapping_1[classname[i]]))+ " " + " ".join([str(a) for a in bb]) + '\n')
                    if int(float(xmin)-1) <0:
                        xmin = 0
                    else:
                        xmin = int(float(xmin)-1)
                    if int(float(ymin)-1) < 0:
                        ymin = 0
                    else:
                        ymin = int(float(ymin)-1)
                    if int(float(xmax)+1) > width:
                        xmax = width
                    else:
                        xmax = int(float(xmax)+1)
                    if int(float(ymax)+1) > height:
                        ymax = height
                    else:
                        ymax = int(float(ymax)+1)
                    writer.writerow(['path/'+str(x),xmin,ymin,xmax,ymax,class_mapping_1[classname[i]]])
    if os.path.isdir(path):
        list_dir(path) # 递归子目录
list_dir(r'E:/hnumedical/Data/Pic_Data/3VT_STD_NSTD_WangTeng/3VT_预标注')
list_dir(r'E:/hnumedical/Data/Pic_Data/dataALL-0626-real')
list_dir(r'E:/hnumedical/Data/Pic_Data/心底短轴切面_WangTeng')
list_dir(r'E:/hnumedical/Data/Pic_Data/左室流出道_半自动标注图')
list_dir(r'E:/hnumedical/Data/Pic_Data/左室流出道切面_nstd')
list_dir(r'E:/hnumedical/Data/Pic_Data/左室流出道切面_std')
list_dir('E:/hnumedical/Data/Video_Data/merged_video_心底四腔心/标准/心底四腔心1已经标注')
list_dir(r'E:/hnumedical/Data/Video_Data/merged_video_胸骨旁四腔心/胸骨旁四腔心1已经标注')
list_dir(r'E:/hnumedical/Data/Video_Data/pb_pic/心底短轴切面/标准_预标注')
list_dir(r'E:/hnumedical/Data/Video_Data/pb_pic/心底短轴切面/基本标准_预标注')
list_dir(r'E:/hnumedical/Data/Video_Data/pb_pic/心底短轴切面/非标准_预标注')
for i in CountQieMian:
    print(i,CountQieMian[i])
for i in CountQieMianALL:
    print(i,CountQieMianALL[i])