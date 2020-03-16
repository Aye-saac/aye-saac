# Ayesaac

This repository contains the source code for Ayesaac, a Python program to help blind people to find what they have lost in a room.  

## Alternative setting up without poetry 

### Dependencies

- Python 3.7

- pip >= 20.0.2

```
pip3 install --upgrade pip
```

- This program uses [RabbitMQ](https://www.rabbitmq.com/) to communicates 
between the different processors of the software.
Therefore, installing RabbitMQ is a pre-requisite.
You can find instructions [here](https://www.rabbitmq.com/download.html).

### Installation

Once the dependencies have been taken care of, you need to install different packages.

#### `pip` installation

Run the following commands after installing RabbitMQ:

- [TensorFlow](https://www.tensorflow.org/)

`TensorFlow for CPU only`
```
pip3 install --upgrade tensorflow==2.1.0
```
`TensorFlow for GPU`
```
pip3 install --upgrade tensorflow-gpu==2.1.0
```

- [Opencv](https://pypi.org/project/opencv-python/)

```
pip3 install --upgrade opencv-python
```

- [Pika](https://pypi.org/project/pika/)

```
pip3 install --upgrade pika
```

- [gTTS](https://pypi.org/project/gTTS/)

```
pip3 install --upgrade gTTS
```

- [playsound](https://pypi.org/project/playsound/)

```
pip3 install --upgrade playsound
```

### Usage

First, start with:
```
./start_all_services.sh
```
After a few seconds, all the services will run in the background, waiting to do work, some warnings can appear, don't worry, it's just Tensorflow 
saying it doesn't find any compatible GPU or that CUDA is not installed, just ignore it, running Tensorflow 
with the GPU is not mandatory.

Now, we just need to tell the first service that there is job to be done ! 
`send_one_request.py` will ping the first service and the rest will follow (send_one_request.py will be replace in the future):
```
python3 send_one_request.py
```

You can look at the `logs/` directory for the services outputs.

To stop the services you just need to enter the following:
```
./stop_all_services.sh
```

### Architecture

![](data/diagram_aye-saac_v2.png)


### Potential dependencies errors 


##### PlaySound dependencies errors for Linux users:

- If this error occurs:

```
ModuleNotFoundError: No module named 'gi'
```

then you need to install [gi](https://askubuntu.com/questions/80448/what-would-cause-the-gi-module-to-be-missing-from-python):
```
sudo apt-get install python3-gi
```

- If this error occurs:
```
ValueError: Namespace Gst not available
```

then you need to install [GStreamer](https://gstreamer.freedesktop.org/documentation/installing/on-linux.html?gi-language=c):
```
sudo apt-get install libgstreamer1.0-0 gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav gstreamer1.0-doc gstreamer1.0-tools gstreamer1.0-x gstreamer1.0-alsa gstreamer1.0-gl gstreamer1.0-gtk3 gstreamer1.0-qt5 gstreamer1.0-pulseaudio
```
