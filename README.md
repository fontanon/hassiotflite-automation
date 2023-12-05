# Home Assistant TensorFlow Lite Image Classification Service

Classify Home Assistant camera snapshots with your pre-trained TensorFlow Lite model and invoke a Home Assistant Webhook as result. 

Use this software as a building block for your Home Assistant scenes: create an automation to take snapshots at intervals (service `camera.snapshot`, see https://www.home-assistant.io/integrations/camera) then another automation with webhook trigger. Connect the two automations with this software as explaied below.

It comes dockerized to be easily deployed on x86-64 (pc) and arch64 (raspberry-pi) architectures. Do not worry having to install tensorflow yourself.

## Table of Contents

- [Install](#install)
- [Support](#support)
- [Contributing](#contributing)

## Install

**NOTE**: If you do not have a `model.tflite` trained you can use the `train_model.py` script. Read instructions on the file. The rest of instructions assume there's a `model.tflite` file under `./model`

On your Home Assistant, create an automation to take a snapshot from your camera at intervals:

```
alias: Take Camera Snapshot
description: This example is once an hour
trigger:
  - platform: time_pattern
    hours: /1
    alias: Once an hour
condition: []
action:
  - service: camera.snapshot
    data:
      filename: /config/watchdir/cam_{{ now().strftime("%Y%m%d-%H%M%S") }}.jpg
    alias: Customise this with your settings
mode: single
```

And another automation to execute your actions when webhook is invoked:

```
alias: Image Classifed
description: Now lets act
trigger:
  - platform: webhook
    allowed_methods:
      - POST
    local_only: true
    webhook_id: "-YCB_gF7Kz8eRKgscqC0vjpXY"
condition: []
action: [] # Add yours, example: mobile notification, activate device, etc.
mode: single
```

Clone this repository on same host where home assistant is dropping snapshots:

```
$ git clone https://github.com/fontanon/hassiotflite.git
$ cd hassiotflite
```

Copy `.env-example` to `.env` and edit the file with your details:

```
$ cp .env-example .env
$ nano .env
```

Edit `docker-compose.yml` file to determine whether `Dockerfile` or `Dockerfile.arm64` (for raspberry-pi) will be used, also last line of file to declare the watchdog folder to supervise new file creation (as `/config/watchdir/` on the home assistant automation above).

Configuration is done, let's now deploy:

```
$ docker compose up --build -d
```

Once it finished check run:

```
$ docker ps
CONTAINER ID   IMAGE                    COMMAND                  CREATED          STATUS          PORTS                    NAMES
de35907862e2   hassiotflite:latest      "python ./service.py"    44 minutes ago   Up 44 minutes                            hassiotflite

$ docker logs --follow hassiotflite 
hassiotflite     2023-12-05 15:09:50,034 DEBUG    service.py:<module> http://{{HIDDEN}}/api/webhook/-YCB_gF7Kz8eRKgscqC0vjpXY
hassiotflite     2023-12-05 15:09:50,035 DEBUG    service.py:<module> /opt/model/model.tflite
hassiotflite     2023-12-05 15:09:50,035 DEBUG    service.py:<module> /opt/watchdir
hassiotflite     2023-12-05 15:10:18,074 INFO     service.py:on_created on_created: /opt/watchdir/con2.jpg
hassiotflite     2023-12-05 15:10:19,173 INFO     service.py:classify 0.803922: con
hassiotflite     2023-12-05 15:10:19,308 INFO     service.py:invoke_webhook Webhook invoked with result: <Response [200]>
hassiotflite     2023-12-05 15:10:19,319 INFO     service.py:classify 0.200000: sin
hassiotflite     2023-12-05 15:10:19,325 INFO     service.py:classify time: 260.663ms
```

## Support

Please [open an issue](https://github.com/fontanon/hassiotflite/issues/new) for support.

## Contributing

Please contribute using [Github Flow](https://guides.github.com/introduction/flow/). Create a branch, add commits, and open a pull request.
