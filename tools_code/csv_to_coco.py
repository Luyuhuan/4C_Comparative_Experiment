import os
import json
import cv2
import numpy as np
import datetime
import copy

np.random.seed(121)


class CsvFilesReader(object):
    def __init__(self, csvs, class2id_map, splits=(0.8, 0.1, 0.1), img_root=None, comment=True):
        assert isinstance(csvs, (str, list, tuple))
        assert isinstance(class2id_map, (str, dict))
        if isinstance(csvs, str):
            csvs = [csvs]
        self.csvs = csvs
        self.img_root = img_root
        self.splits = splits
        self.class2id_map = class2id_map
        self.comment = comment
        if isinstance(self.class2id_map, str):
            with open(self.class2id_map, encoding='utf-8') as f:
                self.class2id_map = json.loads(f.read())

        self._examples = self._load_examples()
        train_counts = int(len(self._examples) * splits[0])
        test_counts = int(len(self._examples) * splits[1])
        val_counts = int(len(self._examples) * splits[2])
        self._train_examples = self._examples[0:train_counts]
        self._test_examples = self._examples[train_counts:train_counts + test_counts]
        self._val_examples = self._examples[train_counts + test_counts:] if val_counts > 0 else []

    def load_split(self, mode='train'):
        assert mode in ('train', 'test', 'val', 'validation')
        if mode == 'train':
            return self._train_examples
        elif mode == 'test':
            return self._test_examples
        else:
            return self._val_examples

    def parse_csv_line(self, line):
        imgname, *insts = line.strip().split(',')
        if self.img_root:
            img_path = os.path.join(self.img_root, imgname)
        else:
            img_path = imgname
        if len(insts) <= 4:
            print('no instance {} .. skipping ...'.format(os.path.basename(img_path, )))
            return None
        if not os.path.exists(img_path):
            print('not exists {} .. skipping ...'.format(os.path.basename(img_path, )))
            return None

        bboxes = []
        if self.class2id_map:
            for i in range(0, len(insts), 5):
                box = [int(it) for it in insts[i:i + 4]]
                clsid = self.class2id_map[insts[i + 4]]
                box.append(clsid)
                bboxes.append(box)
        return img_path, np.array(bboxes, np.int32)

    def _load_examples(self, shuffle=True):
        examples = []
        for csv in self.csvs:
            with open(csv, encoding='utf-8') as f:
                lines = f.readlines()
                if self.comment:
                    lines = lines[1:]
                for line in lines:
                    example = self.parse_csv_line(line)
                    if example:
                        examples.append(example)
        if shuffle:
            np.random.shuffle(examples)
        return examples


class ExamplesTOCoco(object):
    def __init__(self,CATEGORIES=None):
        self.INFO = {
            "description": "Planes Dataset",
            "url": "",
            "version": "0.1.0",
            "year": 2020,
            "contributor": "",
            "date_created": datetime.datetime.utcnow().isoformat(' ')
        }

        self.LICENSES = [
            {
                "id": 1,
                "name": "Attribution-NonCommercial-ShareAlike License",
                "url": "http://creativecommons.org/licenses/by-nc-sa/2.0/"
            }
        ]
        if CATEGORIES:
            self.CATEGORIES = CATEGORIES
        else:
            self.CATEGORIES = [
                {
                    'id': 1,
                    'name': 'LA',
                    'supercategory': 'UltroSonic',
                },
                {
                    'id': 2,
                    'name': 'LV',
                    'supercategory': 'UltroSonic',
                },
                {
                    'id': 3,
                    'name': 'RA',
                    'supercategory': 'UltroSonic',
                },
                {
                    'id': 4,
                    'name': 'RV',
                    'supercategory': 'UltroSonic',
                },
                {
                    'id': 5,
                    'name': 'IVS',
                    'supercategory': 'UltroSonic',
                },
                {
                    'id': 6,
                    'name': 'RIB',
                    'supercategory': 'UltroSonic',
                },
                {
                    'id': 7,
                    'name': 'DA',
                    'supercategory': 'UltroSonic',
                },
                {
                    'id': 8,
                    'name': 'SP',
                    'supercategory': 'UltroSonic',
                },
                {
                    'id': 9,
                    'name': 'A4C',
                    'supercategory': 'UltroSonic',
                },
                {
                    'id': 10,
                    'name': 'P4C',
                    'supercategory': 'UltroSonic',
                },
                {
                    'id': 11,
                    'name': 'B4C',
                    'supercategory': 'UltroSonic',
                }

            ]
        self.coco_output = {
            "info": self.INFO,
            "licenses": self.LICENSES,
            "categories": self.CATEGORIES,
            "images": [],
            "annotations": []
        }

    def _create_annotation_info(self, annotation_id, image_id, category_id, bounding_box, is_crowd=0):
        assert isinstance(bounding_box, np.ndarray)

        annotation_info = {
            "id": annotation_id,
            "image_id": image_id,
            "category_id": int(category_id),
            "iscrowd": is_crowd,
            "area": float(bounding_box[2] * bounding_box[3]),
            "bbox": [int(it) for it in bounding_box.tolist()],  # [x,y,width,height],
            "segmentation": [],
        }

        return annotation_info

    def _create_image_info(self, image_id, file_name, image_size,
                           date_captured=datetime.datetime.utcnow().isoformat(' '),
                           license_id=1, coco_url="", flickr_url=""):

        image_info = {
            "id": image_id,
            "file_name": file_name,
            "width": image_size[0],
            "height": image_size[1],
            "date_captured": date_captured,
            "license": license_id,
            "coco_url": coco_url,
            "flickr_url": flickr_url
        }

        return image_info

    def examples_to_coco(self, examples, save_path='xx/coco_xx.json'):
        coco_output = copy.deepcopy(self.coco_output)
        image_id = 1
        annotation_id = 1

        for img_path, bboxes in examples:
            if not os.path.exists(img_path):
                continue
            print('img_path:',img_path)
            height, width = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), -1).shape[0:2]
            # height, width = cv2.imread(img_path).shape[0:2]
            image_info = self._create_image_info(image_id, os.path.basename(img_path), (width, height))
            coco_output['images'].append(image_info)

            # coco中box的格式： [x,y,width,height]
            x1 = np.clip(bboxes[:, 0:1], 0, width - 1)
            y1 = np.clip(bboxes[:, 1:2], 0, height - 1)
            x2 = np.clip(bboxes[:, 2:3], 0, width - 1)
            y2 = np.clip(bboxes[:, 3:4], 0, height - 1)
            width = np.clip(x2 - x1, 0, width - 1)
            height = np.clip(y2 - y1, 0, height - 1)
            # bboxes[:, 2] = bboxes[:, 2] - bboxes[:, 0]
            # bboxes[:, 3] = bboxes[:, 3] - bboxes[:, 1]
            # bboxes = np.clip(bboxes, 0, )
            bboxes = np.concatenate([x1, y1, width, height, bboxes[:, 4:]], axis=-1)

            for box in bboxes:
                bounding_box = box[0:4]
                category_id = int(box[4] + 1)  # csv中的类别是从0开始的，但coco中是从1开始的
                anno_info = self._create_annotation_info(annotation_id, image_id, category_id, bounding_box)
                coco_output['annotations'].append(anno_info)
                annotation_id += 1

            image_id += 1

        string = json.dumps(coco_output)
        dirname = os.path.dirname(save_path)
        if len(dirname) > 0 and (not os.path.exists(dirname)):
            os.makedirs(dirname)
        with open(save_path, mode='w+', encoding='utf-8') as f:
            f.write(string)
        print('Write Done : ', save_path)
        print('image_id : ', image_id - 1)
        print('annotation_id : ', annotation_id - 1)


if __name__ == '__main__':
    csvs = [r'C:/Users/wh/Desktop/ChoosePic/NeedTest/Choose_All/all_coco.csv', ]
    # csvs = [r'./dataset/xx.csv',]
    splits = (0, 1, 0)
    classmapping = r'E:/hnumedical/4C_tool_code/csv2coc/classMapping.json'
    catagories = r'E:/hnumedical/4C_tool_code/csv2coc/catagories.json'
    img_root = r'C:/Users/wh/Desktop/ChoosePic/NeedTest/Choose_All'

    # img_root = r'./dataset'
    with open(classmapping, encoding='utf-8') as f:
        classmapping = json.loads(f.read())
    with open(catagories, encoding='utf-8') as f:
        catagories = json.loads(f.read())

    csv_reader = CsvFilesReader(csvs, classmapping, splits=splits, img_root=img_root, comment=True)
    train_examples = csv_reader.load_split(mode='train')
    test_examples = csv_reader.load_split(mode='test')
    print('train_examples: ', len(train_examples))
    print('test_examples: ', len(test_examples))

    transfer = ExamplesTOCoco(CATEGORIES=catagories)
    transfer.examples_to_coco(train_examples, save_path=r'C:/Users/wh/Desktop/ChoosePic/NeedTest/Choose_All/to_test_train.json')
    transfer.examples_to_coco(test_examples, save_path=r'C:/Users/wh/Desktop/ChoosePic/NeedTest/Choose_All/to_test_test.json')
