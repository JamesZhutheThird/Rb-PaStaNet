# uncompyle6 version 3.3.5
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.16 |Anaconda, Inc.| (default, Mar 14 2019, 15:42:17) [MSC v.1500 64 bit (AMD64)]
# Embedded file name: /Disk2/iCAN/tools/../lib/ult/ult.py
# Compiled at: 2019-08-09 15:50:35
"""
Generating training instance
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import numpy as np, json, pickle, random
from random import randint
import tensorflow as tf, cv2
from ult import config


print('*************data path:*************')
print(config.cfg.DATA_DIR)
print('************************************')

def bbox_trans(human_box_ori, object_box_ori, ratio, size=64):
    human_box = human_box_ori.copy()
    object_box = object_box_ori.copy()
    InteractionPattern = [
     min(human_box[0], object_box[0]), min(human_box[1], object_box[1]), max(human_box[2], object_box[2]), max(human_box[3], object_box[3])]
    height = InteractionPattern[3] - InteractionPattern[1] + 1
    width = InteractionPattern[2] - InteractionPattern[0] + 1
    if height > width:
        ratio = 'height'
    else:
        ratio = 'width'
    human_box[0] -= InteractionPattern[0]
    human_box[2] -= InteractionPattern[0]
    human_box[1] -= InteractionPattern[1]
    human_box[3] -= InteractionPattern[1]
    object_box[0] -= InteractionPattern[0]
    object_box[2] -= InteractionPattern[0]
    object_box[1] -= InteractionPattern[1]
    object_box[3] -= InteractionPattern[1]
    if ratio == 'height':
        human_box[0] = 0 + size * human_box[0] / height
        human_box[1] = 0 + size * human_box[1] / height
        human_box[2] = size * width / height - 1 - size * (width - 1 - human_box[2]) / height
        human_box[3] = size - 1 - size * (height - 1 - human_box[3]) / height
        object_box[0] = 0 + size * object_box[0] / height
        object_box[1] = 0 + size * object_box[1] / height
        object_box[2] = size * width / height - 1 - size * (width - 1 - object_box[2]) / height
        object_box[3] = size - 1 - size * (height - 1 - object_box[3]) / height
        InteractionPattern = [
         min(human_box[0], object_box[0]), min(human_box[1], object_box[1]), max(human_box[2], object_box[2]), max(human_box[3], object_box[3])]
        if human_box[3] > object_box[3]:
            human_box[3] = size - 1
        else:
            object_box[3] = size - 1
        shift = size / 2 - (InteractionPattern[2] + 1) / 2
        human_box += [shift, 0, shift, 0]
        object_box += [shift, 0, shift, 0]
    else:
        human_box[0] = 0 + size * human_box[0] / width
        human_box[1] = 0 + size * human_box[1] / width
        human_box[2] = size - 1 - size * (width - 1 - human_box[2]) / width
        human_box[3] = size * height / width - 1 - size * (height - 1 - human_box[3]) / width
        object_box[0] = 0 + size * object_box[0] / width
        object_box[1] = 0 + size * object_box[1] / width
        object_box[2] = size - 1 - size * (width - 1 - object_box[2]) / width
        object_box[3] = size * height / width - 1 - size * (height - 1 - object_box[3]) / width
        InteractionPattern = [
         min(human_box[0], object_box[0]), min(human_box[1], object_box[1]), max(human_box[2], object_box[2]), max(human_box[3], object_box[3])]
        if human_box[2] > object_box[2]:
            human_box[2] = size - 1
        else:
            object_box[2] = size - 1
        shift = size / 2 - (InteractionPattern[3] + 1) / 2
        human_box = human_box + [0, shift, 0, shift]
        object_box = object_box + [0, shift, 0, shift]
    return (
     np.round(human_box), np.round(object_box))

def Get_next_sp(human_box, object_box):
    InteractionPattern = [
     min(human_box[0], object_box[0]), min(human_box[1], object_box[1]), max(human_box[2], object_box[2]), max(human_box[3], object_box[3])]
    height = InteractionPattern[3] - InteractionPattern[1] + 1
    width = InteractionPattern[2] - InteractionPattern[0] + 1
    if height > width:
        H, O = bbox_trans(human_box, object_box, 'height')
    else:
        H, O = bbox_trans(human_box, object_box, 'width')
    Pattern = np.zeros((64, 64, 2))
    Pattern[int(H[1]):int(H[3]) + 1, int(H[0]):int(H[2]) + 1, 0] = 1
    Pattern[int(O[1]):int(O[3]) + 1, int(O[0]):int(O[2]) + 1, 1] = 1
    return Pattern

def bb_IOU(boxA, boxB):
    ixmin = np.maximum(boxA[0], boxB[0])
    iymin = np.maximum(boxA[1], boxB[1])
    ixmax = np.minimum(boxA[2], boxB[2])
    iymax = np.minimum(boxA[3], boxB[3])
    iw = np.maximum(ixmax - ixmin + 1.0, 0.0)
    ih = np.maximum(iymax - iymin + 1.0, 0.0)
    inters = iw * ih
    uni = (boxB[2] - boxB[0] + 1.0) * (boxB[3] - boxB[1] + 1.0) + (boxA[2] - boxA[0] + 1.0) * (boxA[3] - boxA[1] + 1.0) - inters
    overlaps = inters / uni
    return overlaps

def Augmented_box(bbox, shape, image_id, augment=15, break_flag=True):
    thres_ = 0.7
    box = np.array([0, bbox[0], bbox[1], bbox[2], bbox[3]]).reshape(1, 5).astype(np.float64)
    aug = [box]
    count = 0
    time_count = 0
    while count < augment:
        time_count += 1
        height = bbox[3] - bbox[1]
        width = bbox[2] - bbox[0]
        height_cen = (bbox[3] + bbox[1]) / 2
        width_cen = (bbox[2] + bbox[0]) / 2
        ratio = 1 + randint(-10, 10) * 0.01
        height_shift = randint(-np.floor(height), np.floor(height)) * 0.1
        width_shift = randint(-np.floor(width), np.floor(width)) * 0.1
        H_0 = max(0, width_cen + width_shift - ratio * width / 2)
        H_2 = min(shape[1] - 1, width_cen + width_shift + ratio * width / 2)
        H_1 = max(0, height_cen + height_shift - ratio * height / 2)
        H_3 = min(shape[0] - 1, height_cen + height_shift + ratio * height / 2)
        if bb_IOU(bbox, np.array([H_0, H_1, H_2, H_3])) > thres_:
            box_ = np.array([0, H_0, H_1, H_2, H_3]).reshape(1, 5)
            aug.append(box_)
            count += 1
        if break_flag == True and time_count > 150:
            break

    aug = np.concatenate(aug, axis=0)
    return aug

def Generate_action_HICO(action_list):
    action_ = np.zeros(600)
    for GT_idx in action_list:
        action_[GT_idx] = 1

    action_ = action_.reshape(1, 600)
    return action_

def Generate_action_rule(cls_rule,action_list,if_Pos):
    if if_Pos == 0:
        return np.ones((1,512,10),dtype = np.float64)
    score_ = np.zeros((1,512,10),dtype = np.float64)
    for GT_idx in action_list:
        for i in range(10):
            for j in range(512):
                score_[0,j,i] += cls_rule[GT_idx,i]
    return score_

def draw_relation(human_pattern, joints, size=64):
    joint_relation = [
     [
      1, 3], [2, 4], [0, 1], [0, 2], [0, 17], [5, 17], [6, 17], [5, 7], [6, 8], [7, 9], [8, 10], [11, 17], [12, 17], [11, 13], [12, 14], [13, 15], [14, 16]]
    color = [0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95]
    skeleton = np.zeros((size, size, 1), dtype='float32')
    for i in range(len(joint_relation)):
        cv2.line(skeleton, tuple(joints[joint_relation[i][0]]), tuple(joints[joint_relation[i][1]]), color[i])

    return skeleton

def get_skeleton(human_box, human_pose, human_pattern, num_joints=17, size=64):
    width = human_box[2] - human_box[0] + 1
    height = human_box[3] - human_box[1] + 1
    pattern_width = human_pattern[2] - human_pattern[0] + 1
    pattern_height = human_pattern[3] - human_pattern[1] + 1
    joints = np.zeros((num_joints + 1, 2), dtype='int32')
    for i in range(num_joints):
        joint_x, joint_y, joint_score = human_pose[3 * i:3 * (i + 1)]
        x_ratio = (joint_x - human_box[0]) / float(width)
        y_ratio = (joint_y - human_box[1]) / float(height)
        joints[i][0] = min(size - 1, int(round(x_ratio * pattern_width + human_pattern[0])))
        joints[i][1] = min(size - 1, int(round(y_ratio * pattern_height + human_pattern[1])))

    joints[num_joints] = (joints[5] + joints[6]) / 2
    return draw_relation(human_pattern, joints)

def Get_next_sp_with_pose(human_box, object_box, human_pose, num_joints=17):
    InteractionPattern = [
     min(human_box[0], object_box[0]), min(human_box[1], object_box[1]), max(human_box[2], object_box[2]), max(human_box[3], object_box[3])]
    height = InteractionPattern[3] - InteractionPattern[1] + 1
    width = InteractionPattern[2] - InteractionPattern[0] + 1
    if height > width:
        H, O = bbox_trans(human_box, object_box, 'height')
    else:
        H, O = bbox_trans(human_box, object_box, 'width')
    Pattern = np.zeros((64, 64, 2), dtype='float32')
    Pattern[int(H[1]):int(H[3]) + 1, int(H[0]):int(H[2]) + 1, 0] = 1
    Pattern[int(O[1]):int(O[3]) + 1, int(O[0]):int(O[2]) + 1, 1] = 1
    if human_pose != None and len(human_pose) == 51:
        skeleton = get_skeleton(human_box, human_pose, H, num_joints)
    else:
        skeleton = np.zeros((64, 64, 1), dtype='float32')
        skeleton[int(H[1]):int(H[3]) + 1, int(H[0]):int(H[2]) + 1, 0] = 0.05
    Pattern = np.concatenate((Pattern, skeleton), axis=2)
    return Pattern

def Generate_part_bbox(joint_bbox, Human_bbox=None):
    part_bbox = np.zeros([1, 10, 5], dtype=np.float64)
    if joint_bbox is None or isinstance(joint_bbox, int):
        if Human_bbox is None:
            raise ValueError
        for i in range(10):
            part_bbox[0, i, :] = np.array([0, Human_bbox[0], Human_bbox[1], Human_bbox[2], Human_bbox[3]], dtype=np.float64)

    else:
        for i in range(10):
            part_bbox[0, i, :] = np.array([0, joint_bbox[i]['x1'], joint_bbox[i]['y1'], joint_bbox[i]['x2'], joint_bbox[i]['y2']], dtype=np.float64)

    return part_bbox

def Generate_part_score(joint_list):
    score_list_16 = [ float(e['score']) for e in joint_list ]
    index_list = [0, 1, 4, 5, 6, 9, 10, 12, 13, 15]
    score_list_10 = [ max(0.0001, score_list_16[i]) for i in index_list ]
    score_list_6 = []
    score_list_6.append((score_list_10[0] + score_list_10[3]) / 2)
    score_list_6.append((score_list_10[1] + score_list_10[2]) / 2)
    score_list_6.append(score_list_10[4])
    score_list_6.append((score_list_10[6] + score_list_10[9]) / 2)
    score_list_6.append((score_list_10[7] + score_list_10[8]) / 2)
    score_list_6.append(score_list_10[5])
    score_list_6 = np.array(score_list_6, dtype=np.float64).reshape((1, 6))
    return score_list_6

def Generate_action_PVP(idx, num_pvp):
    action_PVP = np.zeros([1, num_pvp], dtype=np.float64)
    if isinstance(idx, int):
        action_PVP[:, idx] = 1
    else:
        action_PVP[:, list(idx)] = 1
    return action_PVP

def Generate_action_object(idx, num_pvp):
    action_PVP = np.zeros([1, num_pvp], dtype=np.float64)
    if isinstance(idx, int) or isinstance(idx, np.int32):
        action_PVP[:, idx] = 1
    else:
        action_PVP[:, list(idx)[0]] = 1
    return action_PVP

def Generate_relation_bbox(Human, Object, new=False, isnp=False):
    if not isnp:
        ans = [
         0, 0, 0, 0, 0]
        ans[1] = min(Human[0], Object[0])
        ans[2] = min(Human[1], Object[1])
        ans[3] = max(Human[2], Object[2])
        ans[4] = max(Human[3], Object[3])
        res = np.array(ans).reshape(1, 5).astype(np.float64)
        if new:
            return ans
        return res
    else:
        ans = np.zeros_like(Human)
        for i in range(ans.shape[0]):
            ans[(i, 1)] = min(Human[(i, 0)], Object[(i, 0)])
            ans[(i, 2)] = min(Human[(i, 1)], Object[(i, 1)])
            ans[(i, 3)] = min(Human[(i, 2)], Object[(i, 2)])
            ans[(i, 4)] = min(Human[(i, 3)], Object[(i, 3)])

        return ans

def Get_Next_Instance_HO_HICO_DET_for_only_PVP(Trainval_GT, Trainval_Neg, image_id, Pos_augment, Neg_select, pvp=76):
    if isinstance(image_id, unicode):
        im_file = config.cfg.DATA_DIR + '/' + 'hico_20160224_det/images/train2015/' + image_id
    else:
        im_file = config.cfg.DATA_DIR + '/' + 'hico_20160224_det/images/train2015/HICO_train2015_' + str(image_id).zfill(8) + '.jpg'
    im = cv2.imread(im_file)
    im_orig = im.astype(np.float32, copy=True)
    im_orig -= config.cfg.PIXEL_MEANS
    im_shape = im_orig.shape
    im_orig = im_orig.reshape(1, im_shape[0], im_shape[1], 3)
    cls_rule_data, Human_augmented, Object_augmented, Relation_augmented, Part_bbox, gt_object, action_HO, action_PVP0, action_PVP1, action_PVP2, action_PVP3, action_PVP4, action_PVP5, num_pos, binary_label, gt_10v, gt_verb = Augmented_HO_Neg_HICO_DET_for_only_PVP76(image_id, Trainval_GT, Trainval_Neg, Pos_augment, Neg_select)

    blobs = {}
#    print('rule_shape:')
#   cls_rule_data = np.array(cls_rule_data)
#   print(cls_rule_data.shape)
#   print(action_PVP0.shape)
#   print(action_PVP0)
#   print(cls_rule_data)
#    cls_rule_data = np.array(cls_rule_data)
#    print('cls_rule_data:',cls_rule_data.shape)
#    print(type(cls_rule_data))
#    print(type(action_PVP0))
#    print('111111 ', Pos_augment+Neg_select)
#    cls_rule_data = np.zeros((Pos_augment+Neg_select,512,10))
    blobs['cls_rule_vec'] = cls_rule_data
    blobs['image']   = im_orig
    blobs['H_boxes'] = Human_augmented
    blobs['O_boxes'] = Object_augmented
    blobs['R_boxes'] = Relation_augmented
    blobs['P_boxes'] = Part_bbox
    Part_bbox[:, :, 1] = np.maximum(Part_bbox[:, :, 1], 0)
    Part_bbox[:, :, 2] = np.maximum(Part_bbox[:, :, 2], 0)
    Part_bbox[:, :, 3] = np.minimum(Part_bbox[:, :, 3], im_shape[1])
    Part_bbox[:, :, 4] = np.minimum(Part_bbox[:, :, 4], im_shape[0])
    blobs['gt_class_HO'] = action_HO
    blobs['gt_class_P0'] = action_PVP0
    blobs['gt_class_P1'] = action_PVP1
    blobs['gt_class_P2'] = action_PVP2
    blobs['gt_class_P3'] = action_PVP3
    blobs['gt_class_P4'] = action_PVP4
    blobs['gt_class_P5'] = action_PVP5
    blobs['H_num'] = num_pos
    blobs['binary_label'] = binary_label
    blobs['gt_10v'] = gt_10v
    blobs['gt_verb'] = gt_verb
    blobs['gt_object'] = gt_object
    return blobs

def Augmented_HO_Neg_HICO_DET_for_only_PVP76(image_id, trainval_GT, Trainval_Neg, Pos_augment, Neg_select):
    pair_info = trainval_GT[image_id]
    pair_num = len(pair_info)
    if pair_num >= Pos_augment:
        GT = []
        for i in range(pair_num):
            GT.append(pair_info[i])

    else:
        GT = pair_info
        for i in range(Pos_augment - pair_num):
            index = random.randint(0, pair_num - 1)
            GT.append(pair_info[index])

    Human_augmented    = [np.empty((0, 5), dtype=np.float64)]
    Object_augmented   = [np.empty((0, 5), dtype=np.float64)]
    Relation_augmented = [np.empty((0, 5), dtype=np.float64)]
    action_HO   = [np.empty((0, 600), dtype=np.float64)]
    part_bbox   = [np.empty((0, 10, 5), dtype=np.float64)]
    action_PVP0 = [np.empty((0, 12), dtype=np.float64)]
    action_PVP1 = [np.empty((0, 10), dtype=np.float64)]
    action_PVP2 = [np.empty((0, 5), dtype=np.float64)]
    action_PVP3 = [np.empty((0, 31), dtype=np.float64)]
    action_PVP4 = [np.empty((0, 5), dtype=np.float64)]
    action_PVP5 = [np.empty((0, 13), dtype=np.float64)]
    action_verb = [np.empty((0, 117), dtype=np.float64)]
    action_hp10 = [np.empty((0, 10), dtype=np.float64)]
    gt_object   = [np.empty((0, 80), dtype=np.float64)]
    cls_rule_data = [np.empty((0,512,10),dtype=np.float64)]
    rule_data = np.loadtxt(config.cfg.ROOT_DIR+'/Weights/rule_power.txt',dtype=np.float64,delimiter=',')
#    rule_data = rule_data.tolist()
#  cls_rule_data.append(rule_data)
#    clsnum = 0
            

#    print('rule_data:')
#    print(rule_data[1][1])
    for i in range(Pos_augment):
        Human  = GT[i][2]
        Object = GT[i][3]
        Human_augmented.append(np.array([0, Human[0], Human[1], Human[2], Human[3]]).reshape(1, 5).astype(np.float64))
        Object_augmented.append(np.array([0, Object[0], Object[1], Object[2], Object[3]]).reshape(1, 5).astype(np.float64))
        Relation_augmented.append(Generate_relation_bbox(Human, Object))
        action_HO.append(Generate_action_HICO(GT[i][1]))
#       print('GT[I][1]',GT[i][1])
#       cls_rule_data.append(np.empty((1,512,10),dtype=np.float64))
        part_bbox.append(GT[i][4]['part_bbox'][None, :, :])
        cls_rule_data.append(Generate_action_rule(rule_data,GT[i][1],1))
        action_PVP0.append(Generate_action_PVP(GT[i][4]['pvp76_ankle2'], 12))
        action_PVP1.append(Generate_action_PVP(GT[i][4]['pvp76_knee2'], 10))
        action_PVP2.append(Generate_action_PVP(GT[i][4]['pvp76_hip'], 5))
        action_PVP3.append(Generate_action_PVP(GT[i][4]['pvp76_hand2'], 31))
        action_PVP4.append(Generate_action_PVP(GT[i][4]['pvp76_shoulder2'], 5))
        action_PVP5.append(Generate_action_PVP(GT[i][4]['pvp76_head'], 13))
        action_verb.append(Generate_action_PVP(list(GT[i][4]['verb117_list']), 117))
        action_hp10.append(Generate_action_PVP(GT[i][4]['hp10_list'], 10))
        gt_object.append(Generate_action_object(GT[i][4]['object80_list'], 80))

    num_pos = Pos_augment
    if image_id in Trainval_Neg.keys():
        if len(Trainval_Neg[image_id]) < Neg_select:
            List = range(len(Trainval_Neg[image_id]))
        else:
            List = random.sample(range(len(Trainval_Neg[image_id])), Neg_select)
        for i in range(len(List)):
            Neg = Trainval_Neg[image_id][List[i]]
            Human_augmented.append(np.array([0, Neg[2][0], Neg[2][1], Neg[2][2], Neg[2][3]]).reshape(1, 5))
            Object_augmented.append(np.array([0, Neg[3][0], Neg[3][1], Neg[3][2], Neg[3][3]]).reshape(1, 5))
            Relation_augmented.append(Generate_relation_bbox(Neg[2], Neg[3]))
            action_HO.append(Generate_action_HICO([Neg[1]]))
#            print('Neg:',[Neg[1]])
            cls_rule_data.append(Generate_action_rule(rule_data,[Neg[1]],0))
#           cls_rule_data.append(np.empty((1,512,10),dtype=np.float64))
            part_bbox.append(Neg[7][None, :, :])
            action_verb.append(Generate_action_PVP(57, 117))
            action_PVP0.append(Generate_action_PVP(-1, 12))
            action_PVP1.append(Generate_action_PVP(-1, 10))
            action_PVP2.append(Generate_action_PVP(-1, 5))
            action_PVP3.append(Generate_action_PVP(-1, 31))
            action_PVP4.append(Generate_action_PVP(-1, 5))
            action_PVP5.append(Generate_action_PVP(-1, 13))
            action_hp10.append(np.zeros([1, 10]))
            gt_object.append(Generate_action_object(Neg[4] - 1, 80))

    Human_augmented = np.concatenate(Human_augmented, axis=0)
    Object_augmented = np.concatenate(Object_augmented, axis=0)
    Relation_augmented = np.concatenate(Relation_augmented, axis=0)
    cls_rule_data = np.concatenate(cls_rule_data, axis=0)
    part_bbox = np.concatenate(part_bbox, axis=0)
    action_HO = np.concatenate(action_HO, axis=0)
    action_PVP0 = np.concatenate(action_PVP0, axis=0)
    action_PVP1 = np.concatenate(action_PVP1, axis=0)
    action_PVP2 = np.concatenate(action_PVP2, axis=0)
    action_PVP3 = np.concatenate(action_PVP3, axis=0)
    action_PVP4 = np.concatenate(action_PVP4, axis=0)
    action_PVP5 = np.concatenate(action_PVP5, axis=0)
    action_verb = np.concatenate(action_verb, axis=0)
    action_hp10 = np.concatenate(action_hp10, axis=0)
    gt_object = np.concatenate(gt_object, axis=0)
    binary_label = None
    return (
     cls_rule_data, Human_augmented, Object_augmented, Relation_augmented, part_bbox, gt_object, action_HO, action_PVP0, action_PVP1, action_PVP2, action_PVP3, action_PVP4, action_PVP5, num_pos, binary_label, action_hp10, action_verb)
