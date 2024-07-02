FROM arm64v8/python:3.9.12

WORKDIR /opt/
COPY requirements.txt hassiotflite.py ./
RUN pip install tflite-runtime
RUN pip install -r requirements.txt

# Copy data for add-on
COPY run.sh /
RUN chmod a+x /run.sh
CMD [ "/run.sh" ]