import os
import json
import copy
orgjson = {
    "annotations":{}
}
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
                # if annotations[x]['standard'] != '标准':
                #     continue
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


list_dir(r'E:/hnumedical/4C_ABP_new/to_train/')