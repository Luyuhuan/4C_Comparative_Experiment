#coding=utf-8
import cv2
import re
import codecs
import os
import json
import numpy as np
import shutil
import copy
class_mapping_1 = {'左心房':'LA','左心室':'LV','右心房':'RA','右心室':'RV',
                   '室间隔':'IVS','肋骨':'RIB','降主动脉':'DA','脊柱':'SP',
                   '心尖四腔心切面心脏':'A4C','胸骨旁四腔心切面心脏':'P4C','心底四腔心切面心脏':'B4C',
                   '心脏':'heart'}
FlagRib = 0
Get = []
config_new = {
    "annotations":{}
}
SavePath = "E:/hnumedical/4C_tool_code/GetPic/STDpic"
save_json = copy.deepcopy(config_new)
def list_dir(file_dir):
  dir_list = os.listdir(file_dir)
  for cur_file in dir_list:
    path = file_dir+'/'+cur_file
    print("path:",path)
    if os.path.isfile(path) and cur_file == 'annotations.json':
        print("get in *****************************************")
        f = open(path,encoding='utf-8')
        frame = json.load(f)
        annotations = frame["annotations"]
        for x in annotations:
            FlagRib = 0
            Get = []
            if not os.path.exists(file_dir+'/'+x):
                print(file_dir+x+"不存在")
                continue
            for y in annotations[x]["annotations"]:
                if y["alias"] == "肋骨":
                    FlagRib = FlagRib + 1
                elif y["alias"] in class_mapping_1 and y["alias"] not in Get:
                    Get.append(y["alias"])
            print("FlagRib",FlagRib)
            print("len(Get)",len(Get))
            if FlagRib>= 2 and len(Get)==8:
                shutil.copy(file_dir + '/' + x, SavePath + '/' + x)
                save_json["annotations"][x] = annotations[x]
    if os.path.isdir(path):
        list_dir(path)
list_dir(r'E:/hnumedical/4C_ABP_new/to_test')
new1 = SavePath+ '/' +'annotations.json'
with open(new1, "w", encoding='utf-8') as f1:
    json.dump(save_json, f1, ensure_ascii=False, sort_keys=True, indent=4)
f1.close()