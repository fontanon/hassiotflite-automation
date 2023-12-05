FROM tensorflow/tensorflow

WORKDIR /opt/
COPY requirements.txt hassiotflite.py ./
RUN pip3 install -r requirements.txt
CMD ["python", "./hassiotflite.py"]