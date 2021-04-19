#importing modules

import cv2
import numpy as np
import os
import re
import fnmatch
import matplotlib.pyplot as plt


# ROOT_DIR = '/home/microralp/mk_dev/robot-surgery-segmentation/data/AnnotatedImages/'   

ROOT_DIR = '/media/microralp/MKOSK/instrument_seg/orange_1_img/'
#IMAGE_DIR = os.path.join(ROOT_DIR, "test_im")
IMAGE_DIR = os.path.join(ROOT_DIR, "img_left")
mask_Dest = '/media/microralp/MKOSK/instrument_seg/orange_1_img/mask/'
#ANNOTATION_DIR = os.path.join(ROOT_DIR, "recy_annotations")
   

                    
def filter_for_jpeg(root, files):
    file_types = ['*.png', '*.jpg', '*.bmp']
    file_types = r'|'.join([fnmatch.translate(x) for x in file_types])
    files = [os.path.join(root, f) for f in files]
    files = [f for f in files if re.match(file_types, f)]   
    # print ("here", files)
    return files  

def searchD(f_str, image_GT):
    numGT = 0
    k = len(f_str)
    for i in range(len(image_GT)):
        gt_name = image_GT[i].split("/")[-1]
        # print (f_str == str(image_GT[i].split("/")[-1])[0:k-1])
        # print (f_str)
        # print (str(image_GT[i].split("/")[-1])[:k-1])
        if f_str in str(image_GT[i].split("/")[-1]):
            numGT = i
            # print ( numGT, f_str, gt_name[numGT])
            return numGT
  
def mask_tool(img):
    hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV) 
    # plt.imshow(hsv) 
    # plt.show()
    # #definig the range of red color   
    red_lower=np.array([0,0,100],np.uint8)
    red_upper=np.array([250,255,255],np.uint8)  
    
    mask = cv2.inRange(hsv, red_lower, red_upper)
    
    result = cv2.bitwise_and(img, img, mask=mask)
    b, g, r = cv2.split(result)  
    filter = g.copy()    
    ret,mask = cv2.threshold(filter,0,255, 1)
    img[ mask == 0] = 255
    
    # print (mask)
    # plt.imshow(mask, cmap='gray') 
    
    # masked_image = np.copy(img)
    # masked_image[mask == 0] = [0, 0, 0]
    # plt.imshow(masked_image)
    return mask


image_files = []   


for root, _, files in os.walk(IMAGE_DIR):
    image_files = filter_for_jpeg(root, files)
    
   
    
for n in range(len(image_files)):

    print (mask_Dest)

    image = cv2.imread(image_files[n])
    r = image.shape
    print (r)
    # image = image[50:r[0],0:r[1]-120]
    # r1 = image.shape
    # print (r1)
    image_name = (image_files[n].split("/")[-1]).split(".")[0]
    print(image_name)    
    msk = mask_tool(image)


    # msk = msk[50:r[0],0:r[1]-120]
    # r1 = image.shape
    # print (r1)

    cv2.imwrite(mask_Dest + image_name + '_mask.png', msk)   #[:, 80:r[1]-180]


 
        
            




          


   
   
