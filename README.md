# deepstreamlpd
#This is a sample DeepStream and Python Application that provides an example of incorporating pretrained TAO Models using a primary network to detect objects and a secondary network to detect license plates.  

## DLI Training Resources
I highly recommend that you take these NVIDIA DLI courses (at a minimum, the first two which are free):
1. take the NVIDIA DLI Course at https://courses.nvidia.com/courses/course-v1:DLI+S-IV-02+V2/.  It is currently free and is a comprehensive course that walks you through building a Deepstream Application on the Jetson. 
2. Training a Text Classification Model using TAO Toolkit https://courses.nvidia.com/courses/course-v1:DLI+T-FX-02+V1/.  This is a quick intro course on TAO. It is free.
3. Building Realtime Video AI Applications. https://courses.nvidia.com/courses/course-v1:DLI+S-IV-01+V1/  This is a comprehensive course covering the TAO Toolkit and provides an end to end walk through on builing and deploying a video AI application with TAO pretrained models and Deepstream. It covers training those models with additional custom data. There is a small fee for this course. 

#There is a LPD_Prototype notebook to demonstrate how to execute the different python files. There are four python scripts and several config files.
1. The python script dslpd.py demonstrate  incorporating the tao lpdnet network model https://catalog.ngc.nvidia.com/orgs/nvidia/models/tlt_lpdnet into an existing network that detects objects (cars, people, and signs).  
2. The python script dslpd_redacted.py is the same script but adds additional functionality to leverage the metadata of the second network to redact the license plate. You can adjust the bg_color to make fully opaque. This is set in line 109 (obj_meta.rect_params.bg_color.set(1.0,0.0,0.0,0.5)) of this script.
3. The python script dslpd_trained uses a tao model that was trained with additional data and exported.  
4. The python script dslpd_usb is a copy of dslpd edited to use a camera feed instead of a video file. 

This code was modified and tested using a Jetson Nano 2gb and Deepstream 6.  You may need slight changes to run on x86. You can view the output remotely as a network stream using vlc media player. Enter the url rtsp://<use Jetson IP address>:8554/dslpd for all scripts except for dslpd_usb use rtsp://<use jetson IP>:8554/dslpd-cam. You can change this url application name in line 431 ( server.get_mount_points().add_factory("/dslpd-cam", factory)). If you change it in 431, change the print reference in line 433.  

I recommend using Deepstream 6 as it will generate the appropriate inference engine on the Jetson if the right one does not exist. 

You need to be on the latest Jetpack. Please follow the instructions here https://developer.nvidia.com/embedded/learn/get-started-jetson-nano-devkit#prepare to flash an SD card.  The latest SD image can be downloaded at https://developer.nvidia.com/jetson-nano-sd-card-image.  

###Setup Instructions--

1.  Make this directory:
    mkdir ~/my_apps

2.  Navigate into that directory:
    cd my_apps
    sudo git clone https://github.com/pattydelafuente/deepstreamlpd.git

3.  Allow external applications to connect to the x-host display of the Jetson
    xhost +

4. Download and run the Deepstream L4t container

You can either pull the base container:
https://catalog.ngc.nvidia.com/orgs/nvidia/containers/deepstream-l4t 

sudo docker run -it --rm --net=host --runtime nvidia  -e DISPLAY=$DISPLAY \
-w /opt/nvidia/deepstream/deepstream-6.0 \
-v /tmp/.X11-unix/:/tmp/.X11-unix \
-v /tmp/argus_socket:/tmp/argus_socket \
-v ~/my_apps:/dli/task/my_apps \
nvcr.io/nvidia/deepstream-l4t:6.0.1-samples

You can run the scripts directly. If you want to run Jupyter-lab, you can install it directly https://jupyterlab.readthedocs.io/en/stable/getting_started/installation.html or or use this container that has Jupter-lab environment
