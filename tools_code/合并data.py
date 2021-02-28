#coding=utf-8
import cv2
import re
import codecs
import os
import json
import numpy as np
import shutil
import copy
config_new = {
    "annotations":{}
}
SavePath = "E:/hnumedical/4C_ABP_new/to_train_orgtrain"
save_json = copy.deepcopy(config_new)
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
            shutil.copy(file_dir + '/' + x, SavePath + '/' + x)
            save_json["annotations"][x] = annotations[x]
    if os.path.isdir(path):
        list_dir(path)
list_dir(r'E:/hnumedical/4C_ABP_new/to_train')
list_dir(r'E:/hnumedical/4C_ABP/train')
new1 = SavePath+ '/' +'annotations.json'
with open(new1, "w", encoding='utf-8') as f1:
    json.dump(save_json, f1, ensure_ascii=False, sort_keys=True, indent=4)
f1.close()