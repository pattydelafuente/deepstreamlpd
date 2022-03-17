# deepstreamlpd
#This is a sample DeepStream and Python Application that provides an example of incorporating pretrained TAO Models using a primary network to detect objects and a secondary network to detect license plates.  

#There is a LPD_Prototype notebook to demonstrate how to execute the different python files. The python script dslpd.py demonstrate using the two networks.  The python script dslpd_redacted.py is the same script but adds additional functionality to leverage the metadata of the second network to redact the license plate.  The python script dslpd_trained uses a tao model that was trained with additional data and exported.  

This code was modified and tested using a Jetson Nano 2gb and Deepstream 6.  You may need slight changes to run on x86.

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
