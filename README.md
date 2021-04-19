# ReSORT-IT 

![alt text](https://github.com/kskmar/ReSort-IT/blob/master/images/reSort-IT.jpg)

## Getting Started

see the [INSTALLATION.txt](https://github.com/kskmar/ReSort-IT/blob/master/installation.txt) file for details

### Requirements
To install the required python packages simply type

pip install -r requirements.txt

### Built With

* [Mask_RCNN](https://github.com/matterport/Mask_RCNN) for object detection and instance segmentation on Keras and TensorFlow.
W.  Abdulla,  https://github.com/matterport/Mask_RCNN,  2017,  maskR-CNN for object detection and instance segmentation on Keras andTensorFlow.

## Download the Datasets 

To download the datasets with images and annotation files from:

**Basic Dataset** <https://drive.google.com/file/d/1UVJ3XHo0a7VB648uNIAIMqWt99R7Yhcg/view?usp=sharing>

**Synthetic-Single Dataset** <https://drive.google.com/file/d/16g5A-Hxh4qNATRWb0c1UdiBecLhfmIxN/view?usp=sharing>

**Synthetic-Complex Dataset** <https://drive.google.com/file/d/18EeXpoLuDhgnUoVXEiw4lhYWZxrTmZRa/view?usp=sharing>
 

## Running the tests

Running the source codes

## Publications
Vision-based  Material  Classification  for  Robotic  Urban  Waste  Sorting

## Authors

M. Koskinopoulou, F. Raptopoulos, G. Papadopoulos, N. Mavrakis and M. Maniadakis
See the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the BSD License - see the [LICENSE.md](https://github.com/kskmar/ReSort-IT/blob/master/LICENSE.txt) file for details

## Acknowledgments

* This research has been co‐financed by the European Union and Greek national funds through the Operational Program Competitiveness, Entrepreneurship and Innovation, under the call RESEARCH – CREATE – INNOVATE (project name: ANASA, code:T1EDK-03110), MIS 5031867.

## Results

![alt text](https://github.com/kskmar/ReSort-IT/blob/master/images/)


### Setting up tf environment

https://mc.ai/machine-learning-deep-learning-toolkit-installation-on-windows-10/

conda install -c conda-forge opencv

https://github.com/matterport/Mask_RCNN
pip install -r requirements.txt
python setup.py install

conda install shapely

python -m pip install tensorflow-gpu==1.13.1

# import tensorflow as tf 
# print(tf.__version__)   ---> 1.13.1
meta to pip install 1.13.1
conda install -c anaconda tensorflow-gpu


# import keras
# print(keras.__version__) ---> pip install keras==2.2.5

conda install git
pip install Cython
pip install "git+https://github.com/philferriere/cocoapi.git#egg=pycocotools&subdirectory=PythonAPI"

### Plot Losses using Tensorboard 

tensorboard --logdir=F:\home\microralp\mk_dev\ReSort-IT\mask_rcnn\logs

 
