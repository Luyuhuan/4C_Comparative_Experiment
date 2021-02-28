# coding=utf-8
import cv2
import re
import codecs
import os
import json
import numpy as np
import shutil
txtpath = 'picimageid.txt'
jsonpath = 'results.json'
txtsavepath = '/data/lyh/4C_ABP_code/mAP-master/input/detection-results/'
os.makedirs(txtsavepath)

Name = ["LA", "LV", "RA", "RV", "IVS", "RIB", "DA", "SP", "A4C", "P4C", "B4C" ]
imagename = {}
file1 = open(txtpath,'r',encoding="utf-8")
for line in file1:
    name = ((line.strip()).split(',')[0])
    imageid = ((line.strip()).split(',')[1])
    imagename[imageid] = name
file1.close()

res = {}
count = {}
classcount = {}
f = open(jsonpath,encoding='utf-8')
frame = json.load(f)
for i in frame:
    picname = imagename[str(i["image_id"])]
    littlename = Name[i["category_id"]-1]
    prescore = str(i["score"])
    if picname not in res:
        res[picname] = []
        count[picname] = {}
        classcount[picname] = 0
    if littlename not in count[picname]:
        #***********************筛选切面大框
        flag = 1
        if littlename in ["A4C", "P4C", "B4C"] and classcount[picname]==0:
            classcount[picname] =1
        elif littlename in ["A4C", "P4C", "B4C"] and classcount[picname]==1:
            for alllist in res[picname]:
                if alllist[0] in ["A4C", "P4C", "B4C"] and float(alllist[1]) < float(prescore):
                    res[picname].remove(alllist)
                elif alllist[0] in ["A4C", "P4C", "B4C"] and float(alllist[1]) > float(prescore):
                    flag = 0
        if flag==0:
            continue
        #*********************************
        xmin = (str(i["bbox"][0])).split('.')[0]
        ymin = (str(i["bbox"][1])).split('.')[0]
        xmax = (str(i["bbox"][0]+i["bbox"][2])).split('.')[0]
        ymax = (str(i["bbox"][1]+i["bbox"][3])).split('.')[0]
        nowlist = [littlename,prescore,xmin,ymin,xmax,ymax]
        res[picname].append(nowlist)
        count[picname][littlename] = 1
    elif littlename == "RIB" and count[picname][littlename] == 1:
        xmin = (str(i["bbox"][0])).split('.')[0]
        ymin = (str(i["bbox"][1])).split('.')[0]
        xmax = (str(i["bbox"][0]+i["bbox"][2])).split('.')[0]
        ymax = (str(i["bbox"][1]+i["bbox"][3])).split('.')[0]
        nowlist = [littlename,prescore,xmin,ymin,xmax,ymax]
        res[picname].append(nowlist)
        count[picname][littlename] = 2

for image in res:
    fileevery = open(txtsavepath + image[:-4] + '.txt', 'w', encoding="utf-8")
    print(txtsavepath + image[:-4] + '.txt')
    for preres in res[image]:
        print(preres)
        fileevery.writelines(preres[0]+' '+preres[1]+' '+preres[2]+' '+preres[3]+' '+preres[4]+' '+preres[5]+ '\n')
    fileevery.close()