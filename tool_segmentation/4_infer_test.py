# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 18:45:48 2020

@author: maria
"""

import os
import sys
import json
import numpy as np
import time
from PIL import Image, ImageDraw
import cv2
print(cv2.__version__)
ROOT_DIR = '/home/microralp/mk_dev/ReSort-IT/mask_rcnn'
SAVE_DIR = '/home/microralp/mk_dev/ReSort-IT/mask_rcnn/logs'
assert os.path.exists(ROOT_DIR), 'ROOT_DIR does not exist. Did you forget to read the instructions above? ;)'

# Directory to save logs and trained model
MODEL_DIR = os.path.join(ROOT_DIR, "logs")

# Import mrcnn libraries
sys.path.append(ROOT_DIR) 
from mrcnn.config import Config
from mrcnn import visualize, utils
import mrcnn.model as modellib

import tensorflow as tf
configtf = tf.ConfigProto()
configtf.gpu_options.per_process_gpu_memory_fraction = 0.4
session = tf.Session(config=configtf)

# import matplotlib.pyplot as plt
# from train_maskRcnn_toolSegm import InstrumentSegmConfig

# import warnings

# with warnings.catch_warnings():
#     warnings.filterwarnings("ignore", category=DeprecationWarning)
import sys
import warnings

if not sys.warnoptions:
    warnings.simplefilter("ignore")


maskRcnnfolder = '/home/microralp/mk_dev/ReSort-IT/mask_rcnn/'
#latesth5 = "toolSegm_Full02.h5" #toolSegm_FullB04.h5" #"toolSegm_Full02.h5"  #"toolSegm03.h5" 

# latesth5 = "mask_rcnn_instrumentsegm_0220.h5"

# latesth5 ="/home/microralp/mk_dev/ReSort-IT/mask_rcnn/logs/instrumentsegm20210412T1259/mask_rcnn_instrumentsegm_0120.h5"
# latesth5 ="/home/microralp/mk_dev/ReSort-IT/mask_rcnn/logs/instrumentsegm20210212T1855/mask_rcnn_instrumentsegm_0220.h5"
latesth5 ="/home/microralp/mk_dev/ReSort-IT/mask_rcnn/logs/instrumentsegm20210412T1808/mask_rcnn_instrumentsegm_0145.h5" #160


class InstrumentSegmConfig(Config):
    NAME = "InstrumentSegm"

    GPU_COUNT = 1
    IMAGES_PER_GPU = 1

    # Number of classes (including background)
    NUM_CLASSES = 1 + 1

    IMAGE_MIN_DIM = 256
    IMAGE_MAX_DIM = 256

    BACKBONE = "resnet50" 

    RPN_ANCHOR_SCALES = (16, 32, 64, 128, 256)   
    TRAIN_ROIS_PER_IMAGE = 128 
    MAX_GT_INSTANCES = 1
    POST_NMS_ROIS_INFERENCE = 500 
    POST_NMS_ROIS_TRAINING = 1000 
    DETECTION_MIN_CONFIDENCE = 0.85
#    IMAGE_MIN_SCALE = 70
    # DETECTION_MIN_CONFIDENCE = 0.9

# ####################################################
# #     ====================================         #
# #         Prepare to run Inference                 #
# #     ====================================         #  
# ####################################################

class InferenceConfig(InstrumentSegmConfig):
    GPU_COUNT = 1
    IMAGES_PER_GPU = 1
    IMAGE_MIN_DIM = 256         
    DETECTION_MIN_CONFIDENCE = 0.86
    MAX_INSTANCES = 1
    DETECTION_MAX_INSTANCES = 1

inference_config = InferenceConfig()

# Recreate the model in inference mode
model = modellib.MaskRCNN(mode="inference", 
                          config=inference_config,
                          model_dir=MODEL_DIR)
# Get path to saved weights
# Either set a specific path or find last trained weights
model_path = os.path.join(SAVE_DIR, latesth5)
print("Loading weights from ", model_path)
model.load_weights(model_path, by_name=True)

# model_path = model.find_last()
# # Load trained weights (fill in path to trained weights here)
# assert model_path != "", "Provide path to trained weights"
# print("Loading weights from ", model_path)
# model.load_weights(model_path, by_name=True)


####################################################
#     ====================================         #
#                Run Inference                     #
#     ====================================         #  
####################################################
import skimage
import re
import fnmatch
import matplotlib.pyplot as plt
import matplotlib.cm as cm

def filter_for_jpeg(root, files):
    file_types = ['*.png', '*.jpg', '*.bmp']
    file_types = r'|'.join([fnmatch.translate(x) for x in file_types])
    files = [os.path.join(root, f) for f in files]
    files = [f for f in files if re.match(file_types, f)]   
    # print ("here", files)
    return files  

def resiz(img,percent):
    scale_percent = percent # percent of original size
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)
    # resize image
    resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
    return resized


import os
# test_image_path = "/home/microralp/mk_dev/robot-surgery-segmentation/data/test/"
# test_image_path = "/media/microralp/MKOSK/instrument_seg/orange_1_img/img_left" 
# test_image_path = "/media/microralp/MKOSK/instrument_seg/orange_1_img/img_left_synthetic/"
# test_image_path = "/home/microralp//Documents/inst_scanning_2/imgR"
# test_image_path = "/home/microralp/mk_dev/ReSort-IT/lab_data/tests/imgs/"


# test_image_path = "/home/microralp/mk_dev/ReSort-IT/lab_data/datasetMin/train"
test_image_path = "/home/microralp/mk_dev/robot-surgery-segmentation/data/maskrcnn_dataset/train"
# test_image_path = "/home/microralp/mk_dev/ReSort-IT/lab_data/dataset/imgs"
def max_instance(L):
    max_i = 0
    for i in range(len(L)):
        if L[i]>=L[max_i]:
            max_i = i
    return max_i

def compute_batch_ap(image_ids, dataset, config):
    APs = []
    for image_id in image_ids:
        # Load image
        image, image_meta, gt_class_id, gt_bbox, gt_mask = modellib.load_image_gt(dataset, config, image_id, use_mini_mask=False)
        # Run object detection
        results = model.detect([image], verbose=0)
        # Compute AP
        r = results[0]
        AP, precisions, recalls, overlaps = utils.compute_ap(gt_bbox, gt_class_id, gt_mask, r['rois'], r['class_ids'], r['scores'], r['masks'])
        AP = 1 - AP
        APs.append(AP)
    return APs, precisions, recalls
        

def test_images(test_image_path):
    # test_path = "/home/microralp/mk_dev/ReSort-IT/lab_data/inst_scanning_4"

    for root, _, files in os.walk(test_image_path):
        image_files = filter_for_jpeg(root, files)
    
    nums = 4000
    for file in image_files: 
        img = skimage.io.imread(file)
        img  = resiz(img, 50)
        img_arr = np.array(img)
        x,y,z = img.shape

        # Remove alpha channel, if it has one
        if img_arr.shape[-1] == 4:
            img_arr = img_arr[..., :3]
            

            
        msk_str = file.split("/")[-1].split(".")[0]
        print (msk_str)
        
        results = model.detect([img_arr], verbose=1)
        r = results[0]
        class_names = ['BG', 'Tool']

        mask = r['masks']
        visualize.display_instances(img, r['rois'], r['masks'], r['class_ids'], class_names, r['scores'], figsize=(5,5))
        

        
        # if len(r['class_ids'])!=0:
        #     # plt.imshow(mask)
        #     # plt.show()
        #     print ("MMM", np.array(mask).reshape(img_arr.shape[0],img_arr.shape[1]).shape)
        #     plt.imsave( test_path +'/imgs/' + 'apr3L' + str(nums) +  msk_str +'.png', img) 
        #     plt.imsave(test_path + '/msks/' + 'apr3L' + str(nums) + msk_str + "mask" +'.png',  np.array(mask).reshape(img_arr.shape[0],img_arr.shape[1]), cmap=cm.gray)  
        #     visualize.display_instances(img, r['rois'], r['masks'], r['class_ids'], class_names, r['scores'], figsize=(5,5))
        #     nums -=1
        # else:
        #     os.remove(os.path.join(file))
        


if __name__ == '__main__':
      test_images(test_image_path)
      
      # from train_tool_segm import dataset, config
   
      # image_ids = np.random.choice(dataset.image_ids, 25)
      # APs, precisions, recalls = compute_batch_ap(image_ids, dataset, config)
      # print("mAP @ IoU=50: ", APs)

      # AP = np.mean(APs)
      # visualize.plot_precision_recall(AP, precisions, recalls)
      # plt.show()
      
      # class_names = ['BG', 'Tool']

      # config = InferenceConfig()
      # config.display()

      # model.load_weights(model_path, by_name=True)
      # colors = visualize.random_colors(len(class_names))

      # cap = cv2.VideoCapture("/home/microralp/mk_dev/ReSort-IT/videoLeft_vero.avi")
      # while True:

      #     _, frame = cap.read()
      #     predictions = model.detect([frame],
      #                                verbose=1)  # We are replicating the same image to fill up the batch_size
      #     p = predictions[0]

      #     visualize.display_instances(frame, p['rois'], p['masks'], p['class_ids'],
      #                                 class_names, p['scores'], colors=colors)
          # plt.imshow("Mask RCNN", output)
          # k = cv2.waitKey(10)
          # if k & 0xFF == ord('q'):
          #     break
      # cap.release()
      # cv2.destroyAllWindows()


#for real time
# if __name__ == '__main__':
#      class_names = ['BG', 'Tool']

#      config = InferenceConfig()
#      config.display()

#      model.load_weights(model_path, by_name=True)
#      colors = visualize.random_colors(len(class_names))

#      cap = cv2.VideoCapture(0)
#      while True:

#          _, frame = cap.read()
#          predictions = model.detect([frame],
#                                     verbose=1)  # We are replicating the same image to fill up the batch_size
#          p = predictions[0]

#          output = visualize.display_instances(frame, p['rois'], p['masks'], p['class_ids'],
#                                      class_names, p['scores'], colors=colors, real_time=True)
#          cv2.imshow("Mask RCNN", output)
#          k = cv2.waitKey(10)
#          if k & 0xFF == ord('q'):
#              break
#      cap.release()
#      cv2.destroyAllWindows()
