import pandas as pd
from sklearn.model_selection import train_test_split
import os
import cv2
import json
import numpy as np
import csv
def convert(csv_path, json_file):
    """
    csv file convert to json file of coco dataset
    :param csv_path: path
    :param json_file: path
    :return: none
    """
    start_bbox_id = 1
    # categories = {"0": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10, "11": 11,
    #               "12": 12, "13": 13, "14": 14, "15": 15, "16": 16, "17": 17, "18": 18, "19": 19, "20": 20}
    categories = {'LV':0, 'LA':1, 'RV':2, 'RA':3,
                  'IVS':4, 'RIB':5, 'DA':6, 'SP':7,
                  'RC':8,'4C':9}
    json_dict = {"images": [], "type": "instances", "annotations": [], "categories": []}
    bnd_id = start_bbox_id
    csv_file = open(csv_path,encoding='utf-8')  # 打开csv文件
    csv_reader_lines = csv.reader(csv_file)
    image_id=0
    for one_line in csv_reader_lines:
        image_id = image_id + 1
        img_name = one_line[0].split("/")[-1]
        print(one_line[0])
        img = cv2.imdecode(np.fromfile(one_line[0], dtype=np.uint8), -1)
        height, width = (img.shape)[0], (img.shape)[1]
        image = {"file_name": img_name, "height": height, "width": width, "id": image_id}
        json_dict["images"].append(image)

        category = str(one_line[5])
        category_id = categories[category]

        xmin = int(one_line[1])
        ymin = int(one_line[2])
        xmax = int(one_line[3])
        ymax = int(one_line[4])

        o_width = abs(xmax - xmin)
        o_height = abs(ymax - ymin)
        area = o_height * o_width
        anno = {"area": area, "iscrowd": 0, "image_id": image_id, "bbox": [xmin, ymin, o_width, o_height],
                "category_id": category_id, "id": bnd_id, "ignore": 0, "segmentation": []}
        json_dict["annotations"].append(anno)
        bnd_id += 1

        cat = {"supercategory": "none", "id": category_id, "name": category}
        json_dict["categories"].append(cat)

    json_fp = open(json_file, "w",encoding='utf-8')
    json_str = json.dumps(json_dict, indent=4)
    json_fp.write(json_str)
    json_fp.close()
    print("Done!")


if __name__ == "__main__":
    files_path = "E:/hnumedical/Compare_4CHeartData/train4C.csv"
    json_file = "E:/hnumedical/Compare_4CHeartData/train4C.json"
    convert(files_path, json_file)