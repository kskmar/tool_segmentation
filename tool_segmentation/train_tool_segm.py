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
import mrcnn.utils as utils
from mrcnn import visualize
import mrcnn.model as modellib
# import tensorflow as tf

# configtf = tf.ConfigProto()
# configtf.gpu_options.per_process_gpu_memory_fraction = 0.7
# session = tf.Session(config=configtf)

# import warnings

# with warnings.catch_warnings():
#     warnings.filterwarnings("ignore", category=DeprecationWarning)
import sys
import warnings

if not sys.warnoptions:
    warnings.simplefilter("ignore")


maskRcnnfolder = '/home/microralp/mk_dev/ReSort-IT/mask_rcnn/'



class InstrumentSegmConfig(Config):
    """Configuration for training on the cigarette butts dataset.
    Derives from the base Config class and overrides values specific
    to the cigarette butts dataset.
    """
    # Give the configuration a recognizable name
    NAME = "InstrumentSegm"

    # Train on 1 GPU and 1 image per GPU. Batch size is 1 (GPUs * images/GPU).
    GPU_COUNT = 1
    IMAGES_PER_GPU = 1

    # Number of classes (including background)
    NUM_CLASSES = 1 + 1

    # All of our training images are 512x512
    IMAGE_MIN_DIM = 512
    IMAGE_MAX_DIM = 512

    # You can experiment with this number to see if it improves training
    STEPS_PER_EPOCH = 50

    # This is how often validation is run. If you are using too much hard drive space
    # on saved models (in the MODEL_DIR), try making this value larger.
    VALIDATION_STEPS = 50
    
    # Matterport originally used resnet101, but I downsized to fit it on my graphics card
    BACKBONE = "resnet50" #'resnet50'

    RPN_ANCHOR_SCALES = (32, 64, 128, 256, 512) #(16, 32, 64, 128, 256)   #(4, 8, 16, 32, 64)  (32, 64, 128, 256, 320!!!)
    TRAIN_ROIS_PER_IMAGE = 256 #128 #256 #128  #32
    MAX_GT_INSTANCES = 3
    DETECTION_MAX_INSTANCES = 3
    # DETECTION_NMS_THRESHOLD  = 0.3 ti einai auto??
    POST_NMS_ROIS_INFERENCE = 500 
    POST_NMS_ROIS_TRAINING = 1000 
    DETECTION_MIN_CONFIDENCE = 0.8
#    IMAGE_MIN_SCALE = 70
    


class CocoLikeDataset(utils.Dataset):
    """ Generates a COCO-like dataset, i.e. an image dataset annotated in the style of the COCO dataset.
        See http://cocodataset.org/#home for more information.
    """
    def load_data(self, annotation_json, images_dir):
        """ Load the coco-like dataset from json
        Args:
            annotation_json: The path to the coco annotations json file
            images_dir: The directory holding the images referred to by the json file
        """

        json_file = open(annotation_json)      
        
        coco_json = json.loads(json_file.read())
        json_file.close()
               
        # Add the class names using the base method from utils.Dataset
        source_name = "coco_like"
        for category in coco_json['categories']:
            class_id = category['id']
            class_name = category['name']
            if class_id < 1:
                print('Error: Class id for "{}" cannot be less than one. (0 is reserved for the background)'.format(class_name))
                return
            
            self.add_class(source_name, class_id, class_name)
        
        # Get all annotations
        annotations = {}
        for annotation in coco_json['annotations']:
            image_id = annotation['image_id']
            if image_id not in annotations:
                annotations[image_id] = []
            annotations[image_id].append(annotation)
        
        # Get all images and add them to the dataset
        seen_images = {}
        for image in coco_json['images']:
            image_id = image['id']
            if image_id in seen_images:
                print("Warning: Skipping duplicate image id: {}".format(image))
            else:
                seen_images[image_id] = image
                try:
                    image_file_name = image['file_name']
                    image_width = image['width']
                    image_height = image['height']
                except KeyError as key:
                    print("Warning: Skipping image (id: {}) with missing key: {}".format(image_id, key))
                
                image_path = os.path.abspath(os.path.join(images_dir, image_file_name))
                image_annotations = annotations[image_id]
                
            # print ("AAAABABBABABAB-->", source_name)
            # print (image_id)
            # print (image_path)
            # print (image_annotations)
                
                
                # Add the image using the base method from utils.Dataset
                self.add_image(
                    source=source_name,
                    image_id=image_id,
                    path=image_path,
                    width=image_width,
                    height=image_height,
                    annotations=image_annotations
                )
                
    def load_mask(self, image_id):
        """ Load instance masks for the given image.
        MaskRCNN expects masks in the form of a bitmap [height, width, instances].
        Args:
            image_id: The id of the image to load masks for
        Returns:
            masks: A bool array of shape [height, width, instance count] with
                one mask per instance.
            class_ids: a 1D array of class IDs of the instance masks.
        """
        image_info = self.image_info[image_id]
        annotations = image_info['annotations']
        # print ("edwwww --> ", image_id)
        instance_masks = []
        class_ids = []
        
        for annotation in annotations:
            #print ("HERE--->",annotation)
            class_id = annotation['category_id']
            mask = Image.new('1', (image_info['height'], image_info['width']))
            mask_draw = ImageDraw.ImageDraw(mask, '1')
            for segmentation in annotation['segmentation']:
                #print ("MYYY-->", segmentation)
                mask_draw.polygon(segmentation, fill=1)
                bool_array = np.array(mask) > 0
                instance_masks.append(bool_array)
                class_ids.append(class_id)
        mask = np.dstack(instance_masks)
        class_ids = np.array(class_ids, dtype=np.int32) 
        # print ("edw,", mask.shape)
        return mask, class_ids
    
    
##################################################
#     ====================================       #
#   Create the Training and Validation Datasets  #
#     ====================================       #  
##################################################
    
config = InstrumentSegmConfig()
print("loading  weights for Mask R-CNN model…")
config.display()


path_json_train = '/home/microralp/mk_dev/robot-surgery-segmentation/data/maskrcnn_datasetB/annot/trainImgFulldataB.json'   #         trainImgFull.json'
path_images_train = "/home/microralp/mk_dev/robot-surgery-segmentation/data/maskrcnn_datasetB/train"    
dataset_train = CocoLikeDataset()
dataset_train.load_data(path_json_train, path_images_train )
dataset_train.prepare()

path_json_val = '/home/microralp/mk_dev/robot-surgery-segmentation/data/maskrcnn_datasetB/annot/trainImgFulldataB.json'  
path_images_val = "/home/microralp/mk_dev/robot-surgery-segmentation/data/maskrcnn_datasetB/train"
dataset_val = CocoLikeDataset()
dataset_val.load_data(path_json_val, path_images_val)
dataset_val.prepare()

dataset = dataset_train

# ####################################################
# #     ====================================         #
# #  Display a few images from the training dataset  #
# #     ====================================         #  
# ####################################################
# image_ids = np.random.choice(dataset.image_ids, 6)
# for image_id in image_ids:
#     image = dataset.load_image(image_id)
#     mask, class_ids = dataset.load_mask(image_id)
#     print ("lalala--> ", dataset_train.class_names)
#     print (class_ids)
#     limit=max(class_ids)
#     print ("limit=", limit)
#     print ("class_ids=", class_ids)
#     print (mask.shape)
#     visualize.display_top_masks(image, mask, class_ids, dataset_train.class_names, limit=max(class_ids))
#     # key = cv2.waitKey(0) & 0xFF
#     # if key == ord("q"):
#     #     cv2.destroyAllWindows()                      


# ####################################################
# #     ====================================         #
# #       Create the Training Model and Train        #
# #     ====================================         #  
# ####################################################

# # TRAIN_DIR = os.path.join(MODEL_DIR, "instrumentsegm20210205T1641")

# model = modellib.MaskRCNN(mode="training", config=config,
#                           model_dir=MODEL_DIR)
# # print("here", maskRcnnfolder+"mask_rcnn_coco.h5")

# # Which weights to start with?
# init_with = "last"

# if init_with == "imagenet": 
#     model.load_weights(model.get_imagenet_weights(), by_name=True)
# elif init_with == "coco":
#     # Load weights trained on MS COCO, but skip layers that
#     # are different due to the different number of classes
#     # See README for instructions to download the COCO weights
#     model.load_weights(maskRcnnfolder+"mask_rcnn_coco.h5", by_name=True,
#                         exclude=["mrcnn_class_logits", "mrcnn_bbox_fc", "mrcnn_bbox", "mrcnn_mask"])
# elif init_with == "last":
#     # Load the last model you trained and continue training
#     model.load_weights(model.find_last(), by_name=True)
#     # model.load_weights(maskRcnnfolder+"/logs/"+ "toolSegm_B01.h5", by_name=True)
    
# print ("Model Loaded-->", model)

# import imgaug    
  
# ####################################################
# #     ====================================         #
# #                    Training                      #
# #     ====================================         #  
# ####################################################
# start_train = time.time()

# print ("LEARNING RATE==>", config.LEARNING_RATE)
# #LEARNING_RATE = 0.006
# model.train(dataset_train, dataset_val, 
#             learning_rate=config.LEARNING_RATE,  #ean einai 0.006 vazoume * 2 edw!!
#             epochs=220, 
#             layers='heads',
#             augmentation = imgaug.augmenters.Sequential([ 
#             imgaug.augmenters.Fliplr(1), 
#             imgaug.augmenters.Flipud(1), 
#             imgaug.augmenters.Affine(rotate=(-45, 45)), 
#             imgaug.augmenters.Affine(rotate=(-90, 90)),
#             imgaug.augmenters.Affine(scale=(0.6, 1.2))]))
# end_train = time.time()
# minutes = round((end_train - start_train) / 60, 2)
# print(f'Training took {minutes} minutes')


# ####################################################

# # model.train(dataset_train, dataset_val, 
# #             learning_rate=config.LEARNING_RATE,  #ean einai 0.006 vazoume * 2 edw!!
# #             epochs=122, 
# #             layers='all')
# # end_train = time.time()
# # minutes = round((end_train - start_train) / 60, 2)
# # print(f'Training took {minutes} minutes')


# latesth5 = "toolSegm_FullB04.h5" 
# model_path = os.path.join(SAVE_DIR, latesth5)
# model.keras_model.save_weights(model_path)



# # ####################################################
# # #     ====================================         #
# # #         Prepare to run Inference                 #
# # #     ====================================         #  
# # ####################################################

# class InferenceConfig(InstrumentSegmConfig):
#     GPU_COUNT = 1
#     IMAGES_PER_GPU = 1
#     #IMAGE_MIN_DIM = 256           s
#     #IMAGE_MAX_DIM = 256
#     DETECTION_MIN_CONFIDENCE = 0.9

# inference_config = InferenceConfig()


# # Recreate the model in inference mode
# model = modellib.MaskRCNN(mode="inference", 
#                           config=inference_config,
#                           model_dir=MODEL_DIR)
# # Get path to saved weights
# # Either set a specific path or find last trained weights
# model_path = os.path.join(SAVE_DIR, latesth5)
# print("Loading weights from ", model_path)
# model.load_weights(model_path, by_name=True)

# # model_path = model.find_last()
# # # Load trained weights (fill in path to trained weights here)
# # assert model_path != "", "Provide path to trained weights"
# # print("Loading weights from ", model_path)
# # model.load_weights(model_path, by_name=True)


# ####################################################
# #     ====================================         #
# #                Run Inference                     #
# #     ====================================         #  
# ####################################################
# import skimage
# import re
# import fnmatch

# def filter_for_jpeg(root, files):
#     file_types = ['*.png', '*.jpg', '*.bmp']
#     file_types = r'|'.join([fnmatch.translate(x) for x in file_types])
#     files = [os.path.join(root, f) for f in files]
#     files = [f for f in files if re.match(file_types, f)]   
#     # print ("here", files)
#     return files  



# test_image_path = "/home/microralp/mk_dev/robot-surgery-segmentation/data/test/"
# for root, _, files in os.walk(test_image_path):
#     image_files = filter_for_jpeg(root, files)
    
# for file in image_files: 
#     img = skimage.io.imread(file)
#     img_arr = np.array(img)
#     print([img_arr])
#     # Remove alpha channel, if it has one
#     if img_arr.shape[-1] == 4:
#         img_arr = img_arr[..., :3]
#     results = model.detect([img_arr], verbose=1)
#     r = results[0]
#     print (dataset_val.class_names)
    
#     visualize.display_instances(img, r['rois'], r['masks'], r['class_ids'], 
#                                 dataset_val.class_names, r['scores'], figsize=(5,5))
