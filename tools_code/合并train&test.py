import os
import json
from random import shuffle
import copy
import shutil
Allpath = {'train':'E:/hnumedical/4C_心尖心底胸骨旁_合并/train',
           'test':'E:/hnumedical/4C_心尖心底胸骨旁_合并/test'}
AllJson = {'train':{"annotations":{}},'test':{"annotations":{}}}
def list_dir(file_dir):
  dir_list = os.listdir(file_dir)
  for cur_file in dir_list:
    path = file_dir+'/'+cur_file
    if os.path.isfile(path) and cur_file == 'annotations.json':
        typepic = path.split('/')[-2]
        f = open(path, encoding='utf-8')
        frame = json.load(f)
        annotations = frame["annotations"]
        for x in annotations:
            if not os.path.exists(file_dir + '/' + x):
                continue
            AllJson[typepic]["annotations"][x] = annotations[x]
            shutil.copy(file_dir+'/'+x,Allpath[typepic]+'/'+x)
    if os.path.isdir(path):
        list_dir(path)
list_dir('E:/hnumedical/4C_心尖心底胸骨旁')
for i in AllJson:
    with open(Allpath[i]+ '/' + 'annotations.json', "w", encoding='utf-8') as f:
        json.dump(AllJson[i], f, ensure_ascii=False, sort_keys=True, indent=4)
    f.close()