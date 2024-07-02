#!/bin/env python
# Copyleft 2023 J. Félix Ontañón <felixonta@gmail.com>
# 
# Description: Use TensorFlow Lite image classifier model with
# your Home Assistant Cameras.
# 
# Usage: TbC
# Requirements: TbC
# License: TbD

import os 
import time
import logging
from sys import stdout

import requests
import numpy as np
from PIL import Image

try: 
    # If Dockerfile is used
    from tensorflow import lite as tflite
except:
    # If Dockerfile.arm64 is used
    import tflite_runtime.interpreter as tflite

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Mandatory envvars
TF_LABELS = os.getenv('TF_LABELS').split(',')
TF_LABEL_INVOKE = os.getenv('TF_LABEL_INVOKE')
HASSIO_WEBHOOKURL = os.getenv('WEBHOOKURL')

# Optional envvars
TF_MODEL_FILE = os.getenv('MODEL_FILE', '/opt/model/model.tflite')
HASSIO_WATCHDIR = os.getenv('WATCHDIR', '/opt/watchdir')

# TSFLOW lite parameters
INPUT_MEAN = 127.5
INPUT_STD = 127.5
THREADS = None

# Define logger for dockerized python app.
# FROM: https://gist.github.com/oseme-techguy/8dc90d1808174fc4899bce448ea0e5de
logger = logging.getLogger('hassiotflite')
logger.setLevel(logging.DEBUG) # set logger level
logFormatter = logging.Formatter("%(name)-12s %(asctime)s %(levelname)-8s %(filename)s:%(funcName)s %(message)s")
consoleHandler = logging.StreamHandler(stdout) #set streamhandler to stdout
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)

# Output mandatory envvars
logger.debug(HASSIO_WEBHOOKURL)
logger.debug(TF_MODEL_FILE)
logger.debug(HASSIO_WATCHDIR)

# Invoke the home assistant webhook, expects POST request.
def invoke_webhook(label, prob):
    if label == TF_LABEL_INVOKE and float(prob) > 0.5:
        response = requests.request("POST", HASSIO_WEBHOOKURL)
        logger.info('Webhook invoked with result: ' + str(response))

# Loads tflite model, classify image then triggers hassio automation 
def classify(model_file, image_file):
    # FROM: https://github.com/tensorflow/tensorflow/blob/master/tensorflow/lite/examples/python/label_image.py
    interpreter = tflite.Interpreter(model_path=model_file)
    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    # check the type of the input tensor
    floating_model = input_details[0]['dtype'] == np.float32

    # NxHxWxC, H:1, W:2
    height = input_details[0]['shape'][1]
    width = input_details[0]['shape'][2]
    img = Image.open(image_file).resize((width, height))

    # add N dim
    input_data = np.expand_dims(img, axis=0)

    if floating_model:
        input_data = (np.float32(input_data) - INPUT_MEAN) / INPUT_STD

    interpreter.set_tensor(input_details[0]['index'], input_data)

    start_time = time.time()
    interpreter.invoke()
    stop_time = time.time()

    output_data = interpreter.get_tensor(output_details[0]['index'])
    results = np.squeeze(output_data)

    top_k = results.argsort()[-5:][::-1]
    for i in top_k:
        if floating_model:
            logger.info('{:08.6f}: {}'.format(float(results[i]), TF_LABELS[i]))
        else:
            label = TF_LABELS[i]
            prob = '{:08.6f}'.format(float(results[i] / 255.0))
            logger.info(prob + ': ' + label)
            invoke_webhook(label, prob)

    logger.info('time: {:.3f}ms'.format((stop_time - start_time) * 1000))

# New files handler. Calls the classifier.
class MyHandler(FileSystemEventHandler):
    def on_created(self, event):
        # On newfile print log and classify
        logger.info("on_created: " + event.src_path)
        classify(TF_MODEL_FILE, event.src_path)

if __name__ == '__main__': 
    # Observer handler to check for new files
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path=HASSIO_WATCHDIR, recursive=False)
    observer.start()

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()