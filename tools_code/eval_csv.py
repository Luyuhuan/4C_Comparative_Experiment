#!/usr/bin/env python
# coding: utf-8
from __future__ import division
import os
import cv2
import numpy as np
import sys
import pickle
from optparse import OptionParser
import time
from keras_frcnn import config
from keras import backend as K
from keras.layers import Input
from keras.models import Model
from keras_frcnn import roi_helpers
from keras_frcnn.pascal_voc import pascal_voc_util
from keras_frcnn.pascal_voc_parser import get_data
from keras_frcnn import data_generators
from utils import get_bbox
from keras_frcnn.simple_parser import get_data
config_output_filename = "config.pickle"
with open(config_output_filename, 'rb') as f_in:
    C = pickle.load(f_in)
C.network = 'resnet50'
from keras_frcnn import resnet as nn
testboxlist = 'testbox.txt'
# **********************************************************************************************
# eval function
def voc_ap(rec, prec, use_07_metric=False):
    """ ap = voc_ap(rec, prec, [use_07_metric])
    Compute VOC AP given precision and recall.
    If use_07_metric is true, uses the
    VOC 07 11 point method (default:False).
    """
    if use_07_metric:
        # 11 point metric
        ap = 0.
        for t in np.arange(0., 1.1, 0.1):
            if np.sum(rec >= t) == 0:
                p = 0
            else:
                p = np.max(prec[rec >= t])
            ap = ap + p / 11.
    else:
        # correct AP calculation
        # first append sentinel values at the end
        mrec = np.concatenate(([0.], rec, [1.]))
        mpre = np.concatenate(([0.], prec, [0.]))

        # compute the precision envelope
        for i in range(mpre.size - 1, 0, -1):
            mpre[i - 1] = np.maximum(mpre[i - 1], mpre[i])

        # to calculate area under PR curve, look for points
        # where X axis (recall) changes value
        i = np.where(mrec[1:] != mrec[:-1])[0]

        # and sum (\Delta recall) * prec
        ap = np.sum((mrec[i + 1] - mrec[i]) * mpre[i + 1])
    return ap
def voc_eval(lines,
             annobox,
             imagenames,
             classname,
             ovthresh=0.5,
             use_07_metric=False):
    recs = {}
    # print('annobox:',annobox)
    for imagename in imagenames:
        # print('imagename:',imagename)
        recs[imagename] = annobox[imagename]
    class_recs = {}
    npos = 0
    # print('imagenames',imagenames)
    # print('recs:',recs)
    # print('classname:',classname)
    for imagename in imagenames:
        R = [obj for obj in recs[imagename] if obj['name'] == classname]
        bbox = np.array([x['bbox'] for x in R])
        difficult = np.array([x['difficult'] for x in R]).astype(np.bool)
        det = [False] * len(R)
        npos = npos + sum(~difficult)
        class_recs[imagename] = {'bbox': bbox,
                                 'difficult': difficult,
                                 'det': det}
    splitlines = [x.strip().split(' ') for x in lines]
    image_ids = [x[0] for x in splitlines]
    confidence = np.array([float(x[1]) for x in splitlines])
    BB = np.array([[float(z) for z in x[2:]] for x in splitlines])

    nd = len(image_ids)
    # print('image_ids:',image_ids)
    tp = np.zeros(nd)
    fp = np.zeros(nd)
    # print('class_recs:',class_recs)
    if BB.shape[0] > 0:
        # sort by confidence
        sorted_ind = np.argsort(-confidence)
        #    sorted_scores = np.sort(-confidence)
        BB = BB[sorted_ind, :]
        image_ids = [image_ids[x] for x in sorted_ind]
        # print('image_ids:',image_ids)

        # go down dets and mark TPs and FPs
        # print('nd:',nd)
        for d in range(nd):
            # print('d:',d)
            # print('image_ids[d]:',image_ids[d])
            # id = image_ids[d][-10:-4]
            # id = (image_ids[d].split('/')[-1]).split('.')[0]
            id = image_ids[d]
            # print('id:',id)
            # print('id:',id)
            # catch bad detections
            try:
                R = class_recs[id]
            except:
                print("det not found")
                continue

            bb = BB[d, :].astype(float)
            ovmax = -np.inf
            BBGT = R['bbox'].astype(float)
            # print('BBGT.size:',BBGT.size)
            # print('BBGT:',BBGT)
            # print('bb:',bb)
            if BBGT.size > 0:
                # compute overlaps
                # intersection
                ixmin = np.maximum(BBGT[:, 0], bb[0])
                iymin = np.maximum(BBGT[:, 1], bb[1])
                ixmax = np.minimum(BBGT[:, 2], bb[2])
                iymax = np.minimum(BBGT[:, 3], bb[3])
                iw = np.maximum(ixmax - ixmin + 1., 0.)
                ih = np.maximum(iymax - iymin + 1., 0.)
                inters = iw * ih
                # print('inters:',inters)
                # union
                uni = ((bb[2] - bb[0] + 1.) * (bb[3] - bb[1] + 1.) +
                       (BBGT[:, 2] - BBGT[:, 0] + 1.) *
                       (BBGT[:, 3] - BBGT[:, 1] + 1.) - inters)

                # print('uni:',uni)
                overlaps = inters / uni
                ovmax = np.max(overlaps)
                jmax = np.argmax(overlaps)
            # print('ovmax:',ovmax)
            # print('jmax:',jmax)
            # print('ovthresh:',ovthresh)
            if ovmax > ovthresh:
                # print('R[difficult][jmax]:',R['difficult'][jmax])
                if not R['difficult'][jmax]:
                    # print('R[difficult][jmax]:',R['difficult'][jmax])
                    if not R['det'][jmax]:
                        tp[d] = 1.
                        R['det'][jmax] = 1
                    else:
                        fp[d] = 1.
            else:
                fp[d] = 1.

    # compute precision recall
    fp = np.cumsum(fp)
    tp = np.cumsum(tp)
    rec = tp / float(npos)
    # avoid divide by zero in case the first detection matches a difficult
    # ground truth
    prec = tp / np.maximum(tp + fp, np.finfo(np.float64).eps)
    # print('rec:',rec)
    # print('prec:',prec)
    ap = voc_ap(rec, prec, use_07_metric)

    return rec, prec, ap
# **********************************************************************************************
def get_real_coordinates(ratio, x1, y1, x2, y2):
    real_x1 = int(round(x1 // ratio))
    real_y1 = int(round(y1 // ratio))
    real_x2 = int(round(x2 // ratio))
    real_y2 = int(round(y2 // ratio))
    return (real_x1, real_y1, real_x2, real_y2)
def format_img_size(img, C):
    """ formats the image size based on config """
    img_min_side = float(C.im_size)
    (height, width, _) = img.shape
    if width <= height:
        ratio = img_min_side / width
        new_height = int(ratio * height)
        new_width = int(img_min_side)
    else:
        ratio = img_min_side / height
        new_width = int(ratio * width)
        new_height = int(img_min_side)
    img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
    return img, ratio
def format_img_channels(img, C):
    """ formats the image channels based on config """
    img = img[:, :, (2, 1, 0)]
    img = img.astype(np.float32)
    img[:, :, 0] -= C.img_channel_mean[0]
    img[:, :, 1] -= C.img_channel_mean[1]
    img[:, :, 2] -= C.img_channel_mean[2]
    img /= C.img_scaling_factor
    img = np.transpose(img, (2, 0, 1))
    img = np.expand_dims(img, axis=0)
    return img
def format_img(img, C):
    """ formats an image for model prediction based on config """
    img, ratio = format_img_size(img, C)
    img = format_img_channels(img, C)
    return img, ratio
class_mapping = C.class_mapping
if 'bg' not in class_mapping:
    class_mapping['bg'] = len(class_mapping)
class_mapping = {v: k for k, v in class_mapping.items()}
class_to_color = {class_mapping[v]: np.random.randint(0, 255, 3) for v in class_mapping}
C.num_rois = int(32)
num_features = 1024
print(class_mapping)
if K.image_data_format() == 'channels_first':
    input_shape_img = (3, None, None)
    input_shape_features = (num_features, None, None)
else:
    input_shape_img = (None, None, 3)
    input_shape_features = (None, None, num_features)

img_input = Input(shape=input_shape_img)
roi_input = Input(shape=(C.num_rois, 4))
feature_map_input = Input(shape=input_shape_features)

# define the base network (resnet here, can be VGG, Inception, etc)
shared_layers = nn.nn_base(img_input)

# define the RPN, built on the base layers
num_anchors = len(C.anchor_box_scales) * len(C.anchor_box_ratios)
rpn_layers = nn.rpn(shared_layers, num_anchors)

classifier = nn.classifier(feature_map_input, roi_input, C.num_rois, nb_classes=len(class_mapping))

model_rpn = Model(img_input, rpn_layers)
# model_classifier_only = Model([feature_map_input, roi_input], classifier)
model_classifier = Model([feature_map_input, roi_input], classifier)

# model loading
C.model_path = "models/resnet50/voc.hdf5"
print('Loading weights from {}'.format(C.model_path))
model_rpn.load_weights(C.model_path, by_name=True)
model_classifier.load_weights(C.model_path, by_name=True)

model_rpn.compile(optimizer='sgd', loss='mse')
model_classifier.compile(optimizer='sgd', loss='mse')
classes = {}
bbox_threshold = 0.05
visualise = True
num_rois = C.num_rois
all_imgs, classes_count1, class_mapping1 = get_data(testboxlist)
# print(all_imgs)
ALLlines = {}
for i in class_mapping:
    ALLlines[class_mapping[i]] = []
ALLannobox = {}
ALLimagenames = []
for item in all_imgs:
    # print('item:',item)
    img_name = item['filepath']
    ALLimagenames.append(img_name)
    ALLannobox[img_name] = []
    for boxanno in item['bboxes']:
        # print('boxanno:',boxanno)
        dicnow = {}
        dicnow['name'] = boxanno['class']
        dicnow['bbox'] = [boxanno['x1'],boxanno['y1'],boxanno['x2'],boxanno['y2']]
        dicnow['difficult'] = 0
        ALLannobox[img_name].append(dicnow)
    if not img_name.lower().endswith(('.bmp', '.jpeg', '.jpg', '.png', '.tif', '.tiff')):
        continue
    # print(img_name)
    st = time.time()
    filepath = img_name
    img = cv2.imread(filepath)
    X, ratio = format_img(img, C)
    img_scaled = (np.transpose(X[0, :, :, :], (1, 2, 0)) + 127.5).astype('uint8')
    if K.image_data_format() == 'channels_last':
        X = np.transpose(X, (0, 2, 3, 1))
    # get the feature maps and output from the RPN
    [Y1, Y2, F] = model_rpn.predict(X)
    R = roi_helpers.rpn_to_roi(Y1, Y2, C, K.image_data_format(), overlap_thresh=0.3)
    # print(R.shape)
    R[:, 2] -= R[:, 0]
    R[:, 3] -= R[:, 1]
    bboxes = {}
    probs = {}
    # print('R.shape[0]//num_rois + 1:',R.shape[0]//num_rois + 1)
    for jk in range(R.shape[0] // num_rois + 1):
        ROIs = np.expand_dims(R[num_rois * jk:num_rois * (jk + 1), :], axis=0)
        if ROIs.shape[1] == 0:
            break
        if jk == R.shape[0] // num_rois:
            # pad R
            curr_shape = ROIs.shape
            target_shape = (curr_shape[0], num_rois, curr_shape[2])
            ROIs_padded = np.zeros(target_shape).astype(ROIs.dtype)
            ROIs_padded[:, :curr_shape[1], :] = ROIs
            ROIs_padded[0, curr_shape[1]:, :] = ROIs[0, 0, :]
            ROIs = ROIs_padded
        [P_cls, P_regr] = model_classifier.predict([F, ROIs])
        # print(P_cls)
        for ii in range(P_cls.shape[1]):
            # if np.max(P_cls[0, ii, :]) < 0.8 or np.argmax(P_cls[0, ii, :]) == (P_cls.shape[2] - 1):
            #     continue
            if np.max(P_cls[0, ii, :]) < 0.5 or np.argmax(P_cls[0, ii, :]) == (P_cls.shape[2] - 1):
                continue
            cls_name = class_mapping[np.argmax(P_cls[0, ii, :])]
            if cls_name not in bboxes:
                bboxes[cls_name] = []
                probs[cls_name] = []
            (x, y, w, h) = ROIs[0, ii, :]
            bboxes[cls_name].append([16 * x, 16 * y, 16 * (x + w), 16 * (y + h)])
            probs[cls_name].append(np.max(P_cls[0, ii, :]))
    all_dets = []
    # print('bboxes:',bboxes)
    for key in bboxes:
        bbox = np.array(bboxes[key])
        new_boxes, new_probs = roi_helpers.non_max_suppression_fast(bbox, np.array(probs[key]), overlap_thresh=0.3)
        for jk in range(new_boxes.shape[0]):
            # print('img_name:',img_name)
            # print('jk:',jk)
            # print('new_probs[jk]:',new_probs[jk])
            (x1, y1, x2, y2) = new_boxes[jk, :]
            (real_x1, real_y1, real_x2, real_y2) = get_real_coordinates(ratio, x1, y1, x2, y2)
            # print('(x1, y1, x2, y2):',x1, y1, x2, y2)
            # print('(real_x1, real_y1, real_x2, real_y2):',real_x1, real_y1, real_x2, real_y2)
            strnow = img_name+' '+str(new_probs[jk])+' '+str(real_x1)+' '+str(real_y1)+' '+str(real_x2)+' '+str(real_y2)
            ALLlines[key].append(strnow)
            cv2.rectangle(img, (real_x1, real_y1), (real_x2, real_y2),
                          (int(class_to_color[key][0]), int(class_to_color[key][1]), int(class_to_color[key][2])), 2)
            # textLabel = '{}: {}'.format(key, int(100 * new_probs[jk]))
            # all_dets.append((key, 100 * new_probs[jk]))
            textLabel = '{}: {}'.format(key,("%.2f" % new_probs[jk]))
            # print('textLabel:',textLabel)
            all_dets.append((key, new_probs[jk]))
            (retval, baseLine) = cv2.getTextSize(textLabel, cv2.FONT_HERSHEY_COMPLEX, 1, 1)
            textOrg = (real_x1, real_y1 - 0)
            cv2.rectangle(img, (textOrg[0] - 5, textOrg[1] + baseLine - 5),
                          (textOrg[0] + retval[0] + 5, textOrg[1] - retval[1] - 5), (0, 0, 0), 2)
            cv2.rectangle(img, (textOrg[0] - 5, textOrg[1] + baseLine - 5),
                          (textOrg[0] + retval[0] + 5, textOrg[1] - retval[1] - 5), (255, 255, 255), -1)
            cv2.putText(img, textLabel, textOrg, cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 0), 1)
    print('Elapsed time = {}'.format(time.time() - st))
    # print(all_dets)
    # print(bboxes)
    import os
    if not os.path.isdir("results-csv"):
        os.mkdir("results-csv")
    cv2.imwrite('./results-csv/{}'.format(img_name.split('/')[-1]), img)

aps = []
output_dir = 'output-csv'
if not os.path.isdir(output_dir):
    os.mkdir(output_dir)
ALLclasses = np.asarray(['LA','LV','RA','RV','IVS','RIB','DA','SP','A4C','P4C','B4C'])
for i, cls in enumerate(ALLclasses):
    if cls == 'bg':
        continue
    rec, prec, ap = voc_eval(ALLlines[cls], ALLannobox,
                             ALLimagenames, cls, ovthresh=0.5,
                             use_07_metric=True)
    aps+= [ap]
    print('AP for {} = {:.4f}'.format(cls, ap))
    with open(os.path.join(output_dir, cls + '_pr.pkl'), 'wb') as f:
        pickle.dump({'rec': rec, 'prec': prec, 'ap': ap}, f)
print('Mean AP = {:.4f}'.format(np.mean(aps)))
print('~~~~~~~~')
print('Results:')
for ap in aps:
    print('{:.3f}'.format(ap))
print('{:.3f}'.format(np.mean(aps)))
print('~~~~~~~~')
print('')
print('--------------------------------------------------------------')
print('Results computed with the **unofficial** Python eval code.')
print('Results should be very close to the official MATLAB eval code.')
print('Recompute with `./tools/reval.py --matlab ...` for your paper.')
print('-- Thanks, The Management')
print('--------------------------------------------------------------')
