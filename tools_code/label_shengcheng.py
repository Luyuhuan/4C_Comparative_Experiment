import xml.etree.ElementTree as ET
import pickle
import os
from os import listdir, getcwd
from os.path import join
from convertvoc import clear_dir,excute_std_datasets,excute_nstd_datasets
sets=['train', 'val']#

# classes = ['xinjian5_heart',
#                '3VT_heart',
#                'right_heart',
#                '4qiang_heart',
#                 'xinjian5_heart_nstd',
#                '3VT_heart_nstd',
#                'right_heart_nstd',
#                '4qiang_heart_nstd',
#            'leigu'classes,'jizhu','jianban'] # 这里是你要处理的数据的类别总数

#一定要注意，这里的class顺序要和.names文件里的顺序保持一致
classes=['leigu','jizhu','jianban','ventricle'
                 ,'interval']
# 这里是将左上角和右下角的坐标转化为中心点和宽高
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

def convert_annotation(image_id):
    in_file = open(wd + '/Annotations/%s.xml'%(image_id))
    out_file = open( wd + '/labels/%s.txt'%(image_id), 'w')
    tree=ET.parse(in_file) # 导入xml数据
    root = tree.getroot() # 得到跟节点
    size = root.find('size') # 找到根节点下面的size节点
    w = int(size.find('width').text) # 得到图片的尺寸
    h = int(size.find('height').text)
    for obj in root.iter('object'): # 对根节点下面的'object’节点进行遍历
        difficult = obj.find('difficult').text
        cls = obj.find('name').text
        if cls not in classes or int(difficult) == 1:
            print(image_id)
            print(cls)
            print(difficult)
            print('跳过')
            continue
        cls_id = classes.index(cls)
        xmlbox = obj.find('bndbox')
        b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text), float(xmlbox.find('ymin').text), float(xmlbox.find('ymax').text))
        bb = convert((w,h), b)
        out_file.write(str(cls_id) + " " + " ".join([str(a) for a in bb]) + '\n')



if __name__=='__main__':
    #第一步,需要实现对文件夹的遍历操作
    clear_dir()
    #测试图片的数量
    train_num = 2000
    test_num= 200
    # path=r'/home/ultrasonic/warelee/am/heart_detect/data'
    path=r'/home/ultrasonic/hnumedical/ImageWare/am_heart/dataALL-2'
    # path_std_nstd=['0504','非标准']
    path_std_nstd = ['std','nstd']
    for i in path_std_nstd:
        data_path=os.path.join(path,i)
        for name in os.listdir(data_path):
            if i!='nstd':
                if name not in ['4qiang_heart']:
                    continue
                json_path = os.path.join(data_path,name)
                if os.path.isdir(json_path):
                    excute_std_datasets(json_path, test_num=test_num,train_num=train_num)
                    print('Complete...')
            else:
                if name not in ['4qiang_heart']:
                    continue
                json_path = os.path.join(data_path, name)
                if os.path.isdir(json_path):
                    excute_nstd_datasets(json_path, test_num=test_num,train_num=train_num)
                    print('Complete...')
    #第二步
    wd = getcwd() # 获取当前文件的路径
    wd = wd.replace('\\', '/')
    for image_set in sets: # image_set是train或者val
        if not os.path.exists(wd + '/labels/'): # 创建一个label文件夹来存放图片对应的类别和坐标
            os.makedirs(wd + '/labels/')
        image_ids = open(wd +'/ImageSets/Main/%s.txt' % image_set).read().strip().split()
        list_file = open('%s.txt' % image_set, 'w')

        for image_id in image_ids:
            list_file.write(wd + '/JPEGImages/%s.jpg\n' % image_id)

            # print(image_id)
            convert_annotation(image_id)
        list_file.close()


