#!/bin/env python
# 
# Copyleft 2023 J. Félix Ontañón <felixonta@gmail.com>
# BASED ON: https://www.tensorflow.org/lite/models/modify/model_maker/image_classification 
# 
# Usage: 
# $ IMGPACK=myimagepack python3 train_model.py
# 
# Have prepared myimagepack.tgz file with set of images as per article above. Summary:
# $ ls -l training/
# |-labelA/
#   |-img1.png
#   |-img1.png
# |-labelB/
#   |-img1.png
#   |-img1.png
# 
# TensorflowLite model will be exported under ./model/model.tflite

import os

import numpy as np

import tensorflow as tf
assert tf.__version__.startswith('2')

from tflite_model_maker import model_spec
from tflite_model_maker import image_classifier
from tflite_model_maker.config import ExportFormat
from tflite_model_maker.config import QuantizationConfig
from tflite_model_maker.image_classifier import DataLoader

IMG_NAME = os.getenv('IMGPACK', 'myimagepack') # No extension here
IMG_FILE = IMG_NAME + '.tgz'
IMG_PATH = 'file://' + os.path.join(os.getcwd(), IMG_FILE)

image_path = tf.keras.utils.get_file(IMG_FILE, IMG_PATH, extract=True)
image_path = os.path.join(os.path.dirname(image_path), IMG_NAME)

data = DataLoader.from_folder(image_path)
train_data, test_data = data.split(0.9)

model = image_classifier.create(train_data)

loss, accuracy = model.evaluate(test_data)

# TensorflowLite model will be exported under ./model/model.tflite
model.export(export_dir='./model')