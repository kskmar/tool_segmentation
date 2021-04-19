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


####################################################
#     ====================================         #
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



input_dir = "/home/microralp/mk_dev/ReSort-IT/lab_data/dataset/imgs"
image_paths = []
for filename in os.listdir(input_dir):
    if os.path.splitext(filename)[1].lower() in ['.png', '.jpg', '.jpeg']:
        image_paths.append(os.path.join(input_dir, filename))
        
        
mask_dir = '/home/microralp/mk_dev/ReSort-IT/lab_data/dataset/msks' 
masks_paths = []
for filename in os.listdir(mask_dir):
    if os.path.splitext(filename)[1].lower() in ['.png', '.jpg', '.jpeg']:
        masks_paths.append(os.path.join(mask_dir, filename))
    
for n in range(len(image_paths)):
    # print(image_paths[n])
    image_name = image_paths[n].split("/")[-1]
    mask_name = masks_paths[n].split("/")[-1]
    
    img = plt.imread(image_paths[n])
    height, width = img.shape[:2]
    img_min  = resiz(img, 50)
    heightm, widthm = img_min.shape[:2]
    print ( "(height, width, heightmin, widthmin) -->", height, width, heightm, widthm)
    msk = plt.imread(masks_paths[n])
    msk_min  = resiz(msk, 50)
    
    plt.imsave("/home/microralp/mk_dev/ReSort-IT/lab_data/datasetMin/train/" + image_name, img_min) 
    plt.imsave("/home/microralp/mk_dev/ReSort-IT/lab_data/datasetMin/masks/" + mask_name, msk_min) 
    

