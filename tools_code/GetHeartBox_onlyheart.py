import os
import json
import copy
orgjson = {
    "annotations":{}
}
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
def list_dir(file_dir):
    dir_list = os.listdir(file_dir)
    for cur_file in dir_list:
        path = file_dir + '/' + cur_file
        if os.path.isfile(path) and cur_file == 'annotations.json':
            os.rename(file_dir + '/' +'annotations.json', file_dir+'/'+'organnotations_heart.json')
            f = open(file_dir+'/'+'organnotations_heart.json',encoding='utf-8')
            frame = json.load(f)
            annotations = frame["annotations"]
            savejson = copy.deepcopy(orgjson)
            for x in annotations:
                print(x)
                if not os.path.exists(file_dir+'/'+x):
                    print(file_dir+'/'+x+'不存在')
                    continue
                HeartFlag = 0
                GetBoxFlag = 0
                Xmin=[]
                Ymin=[]
                Xmax=[]
                Ymax=[]
                #print(x)
                savejson["annotations"][x] = annotations[x]
                #print(savejson["annotations"][x])
                for y in savejson["annotations"][x]['annotations']:
                    if y['name'] == '心脏':
                        savejson["annotations"][x]['annotations'].remove(y)
                if annotations[x]['standard'] != '标准':
                    continue
                for y in savejson["annotations"][x]['annotations']:
                    if y['name'] == '脊柱' or y['name'] == '肋骨':
                        continue
                    GetBoxFlag = 1
                    #print(y['name'])
                    Xmin.append(float((y['start']).split(',')[0]))
                    Ymin.append(float((y['start']).split(',')[1]))
                    Xmax.append(float((y['end']).split(',')[0]))
                    Ymax.append(float((y['end']).split(',')[1]))
                if GetBoxFlag == 1:
                    X1 = min(Xmin) - 10
                    Y1 = min(Ymin) - 10
                    X2 = max(Xmax) + 10
                    Y2 = max(Ymax) + 10
                    heartbox = {"type": 2, "name": "心脏", "alias": "心脏", "color": "0,1,0",
                                "start": str(X1)+','+ str(Y1), "end":str(X2)+','+str(Y2),
                                "zDepth": 0, "class": 10, "rotation": 0}
                    savejson["annotations"][x]['annotations'].append(heartbox)
            with open(file_dir + '/' +'annotations.json',"w",encoding='utf-8') as f:
                json.dump(savejson,f,ensure_ascii=False,sort_keys=True,indent=4)
            f.close()
        if os.path.isdir(path):
            list_dir(path)


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