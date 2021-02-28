import os
import json
from random import shuffle
import copy
import shutil
savepath = 'E:/hnumedical/4C_心尖心底胸骨旁'
CountAll = {}
picAll = []
ChoosePic = {'心尖四腔心切面标准': [], '心尖四腔心切面基本标准': [], '心尖四腔心切面非标准': [],
             '心底四腔心切面标准': [], '心底四腔心切面基本标准': [], '心底四腔心切面非标准': [],
             '胸骨旁四腔心切面标准': [], '胸骨旁四腔心切面基本标准': [], '胸骨旁四腔心切面非标准': []}
ChoosePath = {}
ChooseJson = {}
for i in ['心底四腔心切面','心尖四腔心切面','胸骨旁四腔心切面']:
    for j in ['标准','非标准']:
        ChooseJson[i+j] = {"annotations":{}}
        for k in ['train','test']:
            os.makedirs(savepath+'/'+i+'/'+j +'/'+k)
            ChoosePath[i+j+k] = savepath+'/'+i+'/'+j +'/'+k
def list_dir(file_dir):
    dir_list = os.listdir(file_dir)
    for cur_file in dir_list:
        path = file_dir + '/' + cur_file
        if os.path.isfile(path) and cur_file == 'annotations.json':
            last = path.split('/')[-2]
            f = open(path, encoding='utf-8')
            frame = json.load(f)
            annotations = frame["annotations"]
            for x in annotations:
                one = ''
                two = ''
                if last in ['心底四腔心切面','心尖四腔心切面','胸骨旁四腔心切面']:
                    one = last
                if not os.path.exists(file_dir + '/' + x):
                    print(file_dir + '/' + x + '不存在')
                    continue
                if one == '' and annotations[x]["bodyPart"] in ['心底四腔心切面','心尖四腔心切面','胸骨旁四腔心切面']:
                    one = annotations[x]["bodyPart"]
                elif one == '' and annotations[x]["bodyPart"] not in ['心底四腔心切面','心尖四腔心切面','胸骨旁四腔心切面']:
                    continue
                if x in picAll:
                    print('已经统计过', x)
                    continue
                else:
                    picAll.append(x)
                two = annotations[x]["standard"]
                twochange = two
                if twochange == '基本标准':
                    twochange = '标准'
                if one not in CountAll:
                    CountAll[one] = {}
                    CountAll[one][two] = 1
                elif one in CountAll and two not in CountAll[one]:
                    CountAll[one][two] = 1
                elif one in CountAll and two in CountAll[one]:
                    CountAll[one][two] = CountAll[one][two] + 1
                if len(annotations[x]['annotations']) == 0:
                    print(x,'未标记')
                    continue
                ChoosePic[one+twochange].append(file_dir + '/' + x)
                ChooseJson[one+twochange]["annotations"][x] = annotations[x]
                ChooseJson[one+twochange]["annotations"][x]["bodyPart"] = one
        if os.path.isdir(path):
            list_dir(path)
list_dir('E:/hnumedical/Data/4C_分类')
list_dir('E:/hnumedical/Data/Pic_Data/3VT_STD_NSTD_WangTeng/3VT_预标注')
list_dir('E:/hnumedical/Data/Pic_Data/dataALL-0626-real')
list_dir('E:/hnumedical/Data/Pic_Data/心底短轴切面_WangTeng')
list_dir('E:/hnumedical/Data/Pic_Data/左室流出道_半自动标注图')
list_dir('E:/hnumedical/Data/Pic_Data/左室流出道切面_nstd')
list_dir('E:/hnumedical/Data/Pic_Data/左室流出道切面_std')
list_dir('E:/hnumedical/Data/Video_Data/merged_video_心底四腔心/标准/心底四腔心1已经标注')
list_dir('E:/hnumedical/Data/Video_Data/merged_video_胸骨旁四腔心/胸骨旁四腔心1已经标注')
list_dir('E:/hnumedical/Data/Video_Data/pb_pic/心底短轴切面/标准_预标注')
list_dir('E:/hnumedical/Data/Video_Data/pb_pic/心底短轴切面/基本标准_预标注')
list_dir('E:/hnumedical/Data/Video_Data/pb_pic/心底短轴切面/非标准_预标注')
for i in CountAll:
    count = 0
    for j in CountAll[i]:
        count = count + CountAll[i][j]
        print(i,j,':',CountAll[i][j])
    print('**************',i,'总数:',count,'**************')
# 随机打乱图片列表
for i in ChoosePic:
    shuffle(ChoosePic[i])
# 按照指定数量进行训练集测试集的划分
for j in ['心底四腔心切面','心尖四腔心切面','胸骨旁四腔心切面']:
    for i in range(0,91):
        shutil.copy(ChoosePic[j+'非标准'][i], ChoosePath[j+'非标准test']+'/'+(ChoosePic[j+'非标准'][i]).split('/')[-1])
    for i in range(91,451):
        shutil.copy(ChoosePic[j+'非标准'][i], ChoosePath[j+'非标准train']+'/'+(ChoosePic[j+'非标准'][i]).split('/')[-1])
    for i in range(0,344):
        shutil.copy(ChoosePic[j+'标准'][i], ChoosePath[j+'标准test']+'/'+(ChoosePic[j+'标准'][i]).split('/')[-1])
    for i in range(344,1719):
        shutil.copy(ChoosePic[j+'标准'][i], ChoosePath[j+'标准train']+'/'+(ChoosePic[j+'标准'][i]).split('/')[-1])
# 写入原先的标注信息json
for j in ['心底四腔心切面','心尖四腔心切面','胸骨旁四腔心切面']:
    for k in ['标准','非标准']:
        for w in ['train','test']:
            with open(ChoosePath[j+k+w]+'/'+ 'annotations.json', "w", encoding='utf-8') as f:
                json.dump(ChooseJson[j+k], f, ensure_ascii=False, sort_keys=True, indent=4)
            f.close()