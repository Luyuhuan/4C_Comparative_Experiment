import os
from random import shuffle
import json
import shutil

savediffpathpic = "E:/hnumedical/4C_ABP_new/test_class"
diffpicjson = {}
nn = 1/2
savetestpathpic1 = "E:/hnumedical/4C_ABP_new/to_test"
savetestpathpic2 = "E:/hnumedical/4C_ABP_new/to_train"

savejson1 = {"annotations":{}}
savejson2 = {"annotations":{}}
def diff_dir(file_dir):
    dir_list = os.listdir(file_dir)
    for cur_file in dir_list:
        if cur_file == "annotations.json":
            path = file_dir + '/' + cur_file
            f = open(path, encoding='utf-8')
            frame = json.load(f)
            annotations = frame["annotations"]
            for x in annotations:
                if not os.path.exists(file_dir + '/' + x):
                    print(file_dir + x + "不存在")
                    continue
                picpath = savediffpathpic+"/"+annotations[x]["bodyPart"]+"/"+annotations[x]["standard"]
                if not os.path.isdir(picpath):
                    os.makedirs(picpath)
                    diffpicjson[picpath] = {"annotations":{}}
                shutil.copy(file_dir + '/' + x, picpath + '/' + str(x))
                diffpicjson[picpath]["annotations"][x] = annotations[x]
diff_dir("E:/hnumedical/4C_ABP/test")
for i in diffpicjson:
    with open(i + '/' + 'annotations.json', "w", encoding='utf-8') as f:
        json.dump(diffpicjson[i], f, ensure_ascii=False, sort_keys=True, indent=4)
    f.close()
diffpicjson = {}
savediffpathpic = "E:/hnumedical/4C_ABP_new/test_class_new"
diff_dir("E:/hnumedical/4C_ABP/A4C_B4C_P4C_预标注/A4C_B4C_P4C_ALL")
for i in diffpicjson:
    with open(i + '/' + 'annotations.json', "w", encoding='utf-8') as f:
        json.dump(diffpicjson[i], f, ensure_ascii=False, sort_keys=True, indent=4)
    f.close()
for i in diffpicjson:
    with open(i + '/' + 'annotations.json', "w", encoding='utf-8') as f:
        json.dump(diffpicjson[i], f, ensure_ascii=False, sort_keys=True, indent=4)
    f.close()


def list_dir(file_dir):
    print("file_dir:",file_dir)
    dir_list = os.listdir(file_dir)
    shuffle(dir_list)
    AllCount = 0
    for cur_file in dir_list:
        if cur_file[-4:] == ".jpg":
            AllCount = AllCount + 1
    NeedCount = int(AllCount*nn)
    print("AllCount:",AllCount)
    print("NeedCount:",NeedCount)
    for cur_file in dir_list:
        if cur_file == "annotations.json":
            path = file_dir+'/'+cur_file
            print("path:",path)
            f = open(path, encoding='utf-8')
            frame = json.load(f)
            annotations = frame["annotations"]
            for x in annotations:
                if not os.path.exists(file_dir + '/' + x):
                    print(file_dir + x + "不存在")
                    continue
                if NeedCount > 0:
                    shutil.copy(file_dir + '/' + x, savetestpathpic1 + '/' + str(x))
                    NeedCount = NeedCount -1
                    savejson1["annotations"][x] = annotations[x]
                    print("annotations[x][bodyPart]:",annotations[x]["bodyPart"])
                if NeedCount <= 0:
                    shutil.copy(file_dir + '/' + x, savetestpathpic2 + '/' + str(x))
                    NeedCount = NeedCount -1
                    savejson2["annotations"][x] = annotations[x]

file_dir1 ="E:/hnumedical/4C_ABP_new/test_class_new"
dir_list1 = os.listdir(file_dir1)
for cur_file in dir_list1:
    path = file_dir1 + '/' + cur_file
    dir_list3 = os.listdir(path)
    for picpath in dir_list3:
        list_dir(path+"/"+picpath)

file_dir2 ="E:/hnumedical/4C_ABP_new/test_class"
dir_list2 = os.listdir(file_dir2)
for cur_file in dir_list2:
    path = file_dir2 + '/' + cur_file
    dir_list4 = os.listdir(path)
    for picpath in dir_list4:
        list_dir(path+"/"+picpath)
with open(savetestpathpic1 + '/' + 'annotations.json', "w", encoding='utf-8') as f:
    json.dump(savejson1, f, ensure_ascii=False, sort_keys=True, indent=4)
f.close()
with open(savetestpathpic2 + '/' + 'annotations.json', "w", encoding='utf-8') as f:
    json.dump(savejson2, f, ensure_ascii=False, sort_keys=True, indent=4)
f.close()