#coding=utf-8
import os 
import json
import csv
import shutil
QieMian = {}
JieGou = {}
ChongFupic = 'E:/hnumedical/Data/Video_Data/pb_pic/心底短轴切面/非标准_预标注_结构重复'
def makedirs(path):
    try:
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise
def list_dir(file_dir):
  dir_list = os.listdir(file_dir)
  for cur_file in dir_list:
    path = file_dir+'/'+cur_file
    if os.path.isfile(path) and cur_file == 'annotations.json':
        f = open(path,encoding='utf-8')
        frame = json.load(f)
        annotations = frame["annotations"]
        for x in annotations:
            if not os.path.exists(file_dir+'/'  + x):
                print(file_dir+'/'  + x + '不存在')
                continue
            #**********************筛选某个切面数据****************************
            # if annotations[x]['bodyPart'] != '心底短轴切面':
            #     continue
            #****************************************************************
            #**********************统计各个切面图片总数************************
            #qiemian = annotations[x]['bodyPart'] + annotations[x]['standard']
            qiemian = annotations[x]['bodyPart']
            if qiemian not in QieMian:
                QieMian[qiemian] = 1
            else :
                QieMian[qiemian] = QieMian[qiemian] + 1
            #****************************************************************
            #**********************统计各小结构总数***************************
            for y in annotations[x]['annotations'] :
                if y['name'] not in JieGou:
                    JieGou[y['name']] = 1
                else:
                    JieGou[y['name']] = JieGou[y['name']] + 1
            #****************************************************************
            #**********************筛选结构重复图片***************************
            everypic = {}
            for y in annotations[x]['annotations'] :
                #******************合并某些名称不同的相同结构******************
                # SameJieGou = ['主肺动脉和动脉导管','主肺动脉合并动脉导管',
                # '肺动脉及肺动脉导管','右室流出道及主肺动脉']
                # if y['name'] in SameJieGou:
                #     y['name'] = '主肺动脉及动脉导管'
                #***********************************************************
                if y['name'] not in everypic:
                    everypic[y['name']] = 1
                else:
                    everypic[y['name']] = everypic[y['name']] + 1
            for i in everypic:
                if everypic[i] > 1 and i != '肋骨' and i != '左肺' and os.path.exists(file_dir+'/'  + x):
                    print(file_dir+'/'  + x ,'存在',everypic[i],'个',i)
                    #******************移出具有重复结构的图片******************
                    shutil.move(file_dir+'/' + x,ChongFupic + '/'+ x)
                    #********************************************************
            #****************************************************************
    if os.path.isdir(path):
        list_dir(path)
list_dir('E:/hnumedical/Data/Video_Data/pb_pic/心底短轴切面/非标准_预标注')

#*****输出各个切面图片总数******
print('\n','*****输出各个切面图片总数*****')
for i in QieMian:
    print(i,':',QieMian[i])
#*****************************
#*****输出各小结构总数**********
print('\n','*****输出各小结构总数*****')
for i in JieGou:
    print(i,':',JieGou[i])
#*****************************