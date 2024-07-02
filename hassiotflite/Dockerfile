ARG BUILD_FROM
FROM $BUILD_FROM

RUN apk add --no-cache -U python3 python3-dev gcc linux-headers musl-dev tcpdump \
    && pip3 install --no-cache --upgrade pip

WORKDIR /opt/
COPY requirements.txt hassiotflite.py ./
RUN pip install tflite-runtime
RUN pip install -r requirements.txt

# Copy data for add-on
COPY run.sh /
RUN chmod a+x /run.sh
CMD [ "/run.sh" ]