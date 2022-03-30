#!/usr/bin/env python3

################################################################################
# SPDX-FileCopyrightText: Copyright (c) 2019-2021 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
################################################################################

import sys
sys.path.append('../')
import platform
import configparser

# for RTSP ###################
import argparse
####################

import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst

# for RTSP ###################
gi.require_version('GstRtspServer', '1.0')
from gi.repository import GstRtspServer
####################

from common.is_aarch_64 import is_aarch64
from common.bus_call import bus_call

import pyds


PGIE_CLASS_ID_VEHICLE = 0
PGIE_CLASS_ID_BICYCLE = 1
PGIE_CLASS_ID_PERSON = 2
PGIE_CLASS_ID_ROADSIGN = 3
past_tracking_meta=[0]

SGIE_CLASS_ID_LPD = 0

PRIMARY_DETECTOR_UID = 1
SECONDARY_DETECTOR_UID = 2


def osd_sink_pad_buffer_probe(pad,info,u_data):
    frame_number=0
    #Intiallizing object counter with 0.
    obj_counter = {
        PGIE_CLASS_ID_VEHICLE:0,
        PGIE_CLASS_ID_PERSON:0,
        PGIE_CLASS_ID_BICYCLE:0,
        PGIE_CLASS_ID_ROADSIGN:0 
        #lp_count:0
    }
    num_rects=0
    gst_buffer = info.get_buffer()
    if not gst_buffer:
        print("Unable to get GstBuffer ")
        return

    # Retrieve batch metadata from the gst_buffer
    # Note that pyds.gst_buffer_get_nvds_batch_meta() expects the
    # C address of gst_buffer as input, which is obtained with hash(gst_buffer)
    batch_meta = pyds.gst_buffer_get_nvds_batch_meta(hash(gst_buffer))
    l_frame = batch_meta.frame_meta_list
    while l_frame is not None:
        try:
            # Note that l_frame.data needs a cast to pyds.NvDsFrameMeta
            # The casting is done by pyds.NvDsFrameMeta.cast()
            # The casting also keeps ownership of the underlying memory
            # in the C code, so the Python garbage collector will leave
            # it alone.
            frame_meta = pyds.NvDsFrameMeta.cast(l_frame.data)
        except StopIteration:
            break

        frame_number=frame_meta.frame_num
        num_rects = frame_meta.num_obj_meta
        l_obj=frame_meta.obj_meta_list
        while l_obj is not None:
            try:
                # Casting l_obj.data to pyds.NvDsObjectMeta
                obj_meta=pyds.NvDsObjectMeta.cast(l_obj.data)
            except StopIteration:
                break
            
             #Check that the object has been detected by the primary detector
            #and that the class id is that of vehicles/persons.
            if(obj_meta.unique_component_id == PRIMARY_DETECTOR_UID):
                
                obj_counter[obj_meta.class_id] += 1
                if(obj_meta.class_id == PGIE_CLASS_ID_PERSON ):
                    obj_meta.rect_params.border_width = 0
                    obj_meta.rect_params.has_bg_color = 1
                    obj_meta.rect_params.bg_color.red = 1.0
                    obj_meta.rect_params.bg_color.green = 0.0
                    obj_meta.rect_params.bg_color.blue = 0.0
                    obj_meta.rect_params.bg_color.alpha = 1
                    
                else:
                    obj_meta.rect_params.border_width = 0
                    obj_meta.rect_params.has_bg_color = 0
                    #obj_meta.rect_params.bg_color.red = 1.0
                    #obj_meta.rect_params.bg_color.green = 0.0
                    #obj_meta.rect_params.bg_color.blue = 0.0
                    #obj_meta.rect_params.bg_color.alpha = 1
                   
                
            if(obj_meta.unique_component_id == SECONDARY_DETECTOR_UID):
                #print("secondary_detector is working")
                #redact the roi of the license plates
                obj_meta.rect_params.border_width = 0
                #obj_meta.rect_params.border_color.set(1.0,0.0,0.0,1.0)
                obj_meta.rect_params.has_bg_color=1
                obj_meta.rect_params.bg_color.red = 0.0
                obj_meta.rect_params.bg_color.green = 1.0
                obj_meta.rect_params.bg_color.blue = 0.0
                obj_meta.rect_params.bg_color.alpha = 1
                
            
            try: 
                l_obj=l_obj.next
            except StopIteration:
                break
#nvosd.set_property('display_text',0)

        # Acquiring a display meta object. The memory ownership remains in
        # the C code so downstream plugins can still access it. Otherwise
        # the garbage collector will claim it when this probe function exits.
        #display_meta=pyds.nvds_acquire_display_meta_from_pool(batch_meta)
        #display_meta.num_labels = 1
        #display_meta.num_labels = 0
       # py_nvosd_text_params = display_meta.text_params[0]
        # Setting display text to be shown on screen
        # Note that the pyds module allocates a buffer for the string, and the
        # memory will not be claimed by the garbage collector.
        # Reading the display_text field here will return the C address of the
        # allocated string. Use pyds.get_string() to get the string content.
       # py_nvosd_text_params.display_text = "Frame Number={} Number of Objects={} Vehicle_count={} Person_count={} #".format(frame_number, num_rects, obj_counter[PGIE_CLASS_ID_VEHICLE], obj_counter[PGIE_CLASS_ID_PERSON])

        # Now set the offsets where the string should appear
     #   py_nvosd_text_params.x_offset = 10
      #  py_nvosd_text_params.y_offset = 12

        # Font , font-color and font-size
   #     py_nvosd_text_params.font_params.font_name = "Serif"
     #   py_nvosd_text_params.font_params.font_size = 10
        # set(red, green, blue, alpha); set to White
      #  py_nvosd_text_params.font_params.font_color.set(1.0, 1.0, 1.0, 1.0)

        # Text background color
       # py_nvosd_text_params.set_bg_clr = 1
        # set(red, green, blue, alpha); set to Black
        #py_nvosd_text_params.text_bg_clr.set(0.0, 0.0, 0.0, 1.0)
        # Using pyds.get_string() to get display_text as string
       # print(pyds.get_string(py_nvosd_text_params.display_text))
       # pyds.nvds_add_display_meta_to_frame(frame_meta, display_meta)
        try:
            l_frame=l_frame.next
        except StopIteration:
            break
    #past traking meta data
    past_tracking_meta[0] = past_tracking
    if(past_tracking_meta[0]==1):
        l_user=batch_meta.batch_user_meta_list
        while l_user is not None:
            try:
                # Note that l_user.data needs a cast to pyds.NvDsUserMeta
                # The casting is done by pyds.NvDsUserMeta.cast()
                # The casting also keeps ownership of the underlying memory
                # in the C code, so the Python garbage collector will leave
                # it alone
                user_meta=pyds.NvDsUserMeta.cast(l_user.data)
            except StopIteration:
                break
            if(user_meta and user_meta.base_meta.meta_type==pyds.NvDsMetaType.NVDS_TRACKER_PAST_FRAME_META):
                try:
                    # Note that user_meta.user_meta_data needs a cast to pyds.NvDsPastFrameObjBatch
                    # The casting is done by pyds.NvDsPastFrameObjBatch.cast()
                    # The casting also keeps ownership of the underlying memory
                    # in the C code, so the Python garbage collector will leave
                    # it alone
                    pPastFrameObjBatch = pyds.NvDsPastFrameObjBatch.cast(user_meta.user_meta_data)
                except StopIteration:
                    break
               # for trackobj in pyds.NvDsPastFrameObjBatch.list(pPastFrameObjBatch):
                    #print("streamId=",trackobj.streamID)
                    #print("surfaceStreamID=",trackobj.surfaceStreamID)
                   # for pastframeobj in pyds.NvDsPastFrameObjStream.list(trackobj):
                       # print("numobj=",pastframeobj.numObj)
                       # print("uniqueId=",pastframeobj.uniqueId)
                        #print("classId=",pastframeobj.classId)
                        #print("objLabel=",pastframeobj.objLabel)
                        #for objlist in pyds.NvDsPastFrameObjList.list(pastframeobj):
                            #print('frameNum:', objlist.frameNum)
                            #print('tBbox.left:', objlist.tBbox.left)
                            #print('tBbox.width:', objlist.tBbox.width)
                           # print('tBbox.top:', objlist.tBbox.top)
                           # print('tBbox.right:', objlist.tBbox.height)
                           # print('confidence:', objlist.confidence)
                            # print('age:', objlist.age)
            try:
                l_user=l_user.next
            except StopIteration:
                break
    return Gst.PadProbeReturn.OK	

def main(args):
    GObject.threads_init()
    Gst.init(None)

    # Create gstreamer elements
    # Create Pipeline element that will form a connection of other elements
    print("Creating Pipeline \n ")
    pipeline = Gst.Pipeline()

    if not pipeline:
        sys.stderr.write(" Unable to create Pipeline \n")

    # Source element for reading from the file
    print("Creating Source \n ")
    source = Gst.ElementFactory.make("filesrc", "file-source")
    if not source:
        sys.stderr.write(" Unable to create Source \n")

    # Since the data format in the input file is elementary h264 stream,
    # we need a h264parser
    print("Creating H264Parser \n")
    h264parser = Gst.ElementFactory.make("h264parse", "h264-parser")
    if not h264parser:
        sys.stderr.write(" Unable to create h264 parser \n")

    # Use nvdec_h264 for hardware accelerated decode on GPU
    print("Creating Decoder \n")
    decoder = Gst.ElementFactory.make("nvv4l2decoder", "nvv4l2-decoder")
    if not decoder:
        sys.stderr.write(" Unable to create Nvv4l2 Decoder \n")

    # Create nvstreammux instance to form batches from one or more sources.
    streammux = Gst.ElementFactory.make("nvstreammux", "Stream-muxer")
    if not streammux:
        sys.stderr.write(" Unable to create NvStreamMux \n")

    # Use nvinfer to run inferencing on decoder's output,
    # behaviour of inferencing is set through config file
    pgie = Gst.ElementFactory.make("nvinfer", "primary-inference")
    if not pgie:
        sys.stderr.write(" Unable to create pgie \n")

    tracker = Gst.ElementFactory.make("nvtracker", "tracker")
    if not tracker:
        sys.stderr.write(" Unable to create tracker \n")

    sgie1 = Gst.ElementFactory.make("nvinfer", "secondary1-nvinference-engine")
    if not sgie1:
        sys.stderr.write(" Unable to make sgie1 \n")


    nvvidconv = Gst.ElementFactory.make("nvvideoconvert", "convertor")
    if not nvvidconv:
        sys.stderr.write(" Unable to create nvvidconv \n")

    # Create OSD to draw on the converted RGBA buffer
    nvosd = Gst.ElementFactory.make("nvdsosd", "onscreendisplay")

    if not nvosd:
        sys.stderr.write(" Unable to create nvosd \n")

    # # Finally render the osd output
    # if is_aarch64():
    #     transform = Gst.ElementFactory.make("nvegltransform", "nvegl-transform")

    # print("Creating EGLSink \n")
    # sink = Gst.ElementFactory.make("nveglglessink", "nvvideo-renderer")
    # if not sink:
    #     sys.stderr.write(" Unable to create egl sink \n")

    # print("Playing file %s " %args[1])
    # source.set_property('location', args[1])

# for RTSP ###################
    nvvidconv_postosd = Gst.ElementFactory.make("nvvideoconvert", "convertor_postosd")
    if not nvvidconv_postosd:
        sys.stderr.write(" Unable to create nvvidconv_postosd \n")
    
    # Create a caps filter
    caps = Gst.ElementFactory.make("capsfilter", "filter")
    caps.set_property("caps", Gst.Caps.from_string("video/x-raw(memory:NVMM), format=I420"))
    
    # Make the encoder
    if codec == "H264":
        encoder = Gst.ElementFactory.make("nvv4l2h264enc", "encoder")
        print("Creating H264 Encoder")
    elif codec == "H265":
        encoder = Gst.ElementFactory.make("nvv4l2h265enc", "encoder")
        print("Creating H265 Encoder")
    if not encoder:
        sys.stderr.write(" Unable to create encoder")
    encoder.set_property('bitrate', bitrate)
    if is_aarch64():
        encoder.set_property('preset-level', 1)
        encoder.set_property('insert-sps-pps', 1)
        encoder.set_property('bufapi-version', 1)
    
    # Make the payload-encode video into RTP packets
    if codec == "H264":
        rtppay = Gst.ElementFactory.make("rtph264pay", "rtppay")
        print("Creating H264 rtppay")
    elif codec == "H265":
        rtppay = Gst.ElementFactory.make("rtph265pay", "rtppay")
        print("Creating H265 rtppay")
    if not rtppay:
        sys.stderr.write(" Unable to create rtppay")
    
    # Make the UDP sink
    updsink_port_num = 5400
    sink = Gst.ElementFactory.make("udpsink", "udpsink")
    if not sink:
        sys.stderr.write(" Unable to create udpsink")
    
    sink.set_property('host', '224.224.255.255')
    sink.set_property('port', updsink_port_num)
    sink.set_property('async', False)
    sink.set_property('sync', 1)
    
    print("Playing file %s " %stream_path)
    source.set_property('location', stream_path)

    streammux.set_property('width', 1920)
    streammux.set_property('height', 1080)
    streammux.set_property('batch-size', 1)
    streammux.set_property('batched-push-timeout', 4000000)
#############

    #Set properties of pgie and sgie
    pgie.set_property('config-file-path', "dslpd_pgie_config.txt")
    pgie.set_property('unique-id', PRIMARY_DETECTOR_UID)
   
    #sgie1.set_property('config-file-path', "dslpd_sgie1_config.txt")
    #sgie2.set_property('config-file-path', "dslpd_sgie2_config.txt")
    sgie1.set_property('config-file-path', "lpd_us_config.txt")
    sgie1.set_property('unique-id', SECONDARY_DETECTOR_UID)
    sgie1.set_property('process-mode', 2)
#     sgie3.set_property('config-file-path', "dstest2_sgie3_config.txt")

    #this line disables all the detected object labels, comment out if you want to enable them
    nvosd.set_property('display-text',0)
    #Set properties of tracker
    config = configparser.ConfigParser()
    config.read('dslpd_tracker_config.txt')
    config.sections()

    for key in config['tracker']:
        if key == 'tracker-width' :
            tracker_width = config.getint('tracker', key)
            tracker.set_property('tracker-width', tracker_width)
        if key == 'tracker-height' :
            tracker_height = config.getint('tracker', key)
            tracker.set_property('tracker-height', tracker_height)
        if key == 'gpu-id' :
            tracker_gpu_id = config.getint('tracker', key)
            tracker.set_property('gpu_id', tracker_gpu_id)
        if key == 'll-lib-file' :
            tracker_ll_lib_file = config.get('tracker', key)
            tracker.set_property('ll-lib-file', tracker_ll_lib_file)
        if key == 'll-config-file' :
            tracker_ll_config_file = config.get('tracker', key)
            tracker.set_property('ll-config-file', tracker_ll_config_file)
        if key == 'enable-batch-process' :
            tracker_enable_batch_process = config.getint('tracker', key)
            tracker.set_property('enable_batch_process', tracker_enable_batch_process)
        if key == 'enable-past-frame' :
            tracker_enable_past_frame = config.getint('tracker', key)
            tracker.set_property('enable_past_frame', tracker_enable_past_frame)

    print("Adding elements to Pipeline \n")
    pipeline.add(source)
    pipeline.add(h264parser)
    pipeline.add(decoder)
    pipeline.add(streammux)
    pipeline.add(pgie)
    pipeline.add(tracker)
    pipeline.add(sgie1)
    #pipeline.add(sgie2)
    pipeline.add(nvvidconv)
    pipeline.add(nvosd)
# for RTSP ###################
    pipeline.add(nvvidconv_postosd)
    pipeline.add(caps)
    pipeline.add(encoder)
    pipeline.add(rtppay) 
######  
    pipeline.add(sink)
    
    
    
    
    source.link(h264parser)
    h264parser.link(decoder)

    sinkpad = streammux.get_request_pad("sink_0")
    if not sinkpad:
        sys.stderr.write(" Unable to get the sink pad of streammux \n")
    srcpad = decoder.get_static_pad("src")
    if not srcpad:
        sys.stderr.write(" Unable to get source pad of decoder \n")       
    srcpad.link(sinkpad)
    
    streammux.link(pgie)
    pgie.link(tracker)
    tracker.link(sgie1)
    sgie1.link(nvvidconv)
    nvvidconv.link(nvosd)
# for RTSP ###################
    nvosd.link(nvvidconv_postosd)
    nvvidconv_postosd.link(caps)
    caps.link(encoder)
    encoder.link(rtppay)
    rtppay.link(sink)
###############

    # create and event loop and feed gstreamer bus mesages to it
    loop = GObject.MainLoop()

    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect ("message", bus_call, loop)

# for RTSP ###################    
    # Start streaming
    rtsp_port_num = 8554
    
    server = GstRtspServer.RTSPServer.new()
    server.props.service = "%d" % rtsp_port_num
    server.attach(None)
    
    factory = GstRtspServer.RTSPMediaFactory.new()
    factory.set_launch( "( udpsrc name=pay0 port=%d buffer-size=524288 caps=\"application/x-rtp, media=video, clock-rate=90000, encoding-name=(string)%s, payload=96 \" )" % (updsink_port_num, codec))
    factory.set_shared(True)
    server.get_mount_points().add_factory("/dslpd", factory)
    
    print("\n *** DeepStream: Launched RTSP Streaming at rtsp://localhost:%d/dslpd ***\n\n" % rtsp_port_num)
#########################    


    # Lets add probe to get informed of the meta data generated, we add probe to
    # the sink pad of the osd element, since by that time, the buffer would have
    # had got all the metadata.
    osdsinkpad = nvosd.get_static_pad("sink")
    if not osdsinkpad:
        sys.stderr.write(" Unable to get sink pad of nvosd \n")
    osdsinkpad.add_probe(Gst.PadProbeType.BUFFER, osd_sink_pad_buffer_probe, 0)


    print("Starting pipeline \n")
    
    # start play back and listed to events
    pipeline.set_state(Gst.State.PLAYING)
    try:
      loop.run()
    except:
      pass

    # cleanup
    pipeline.set_state(Gst.State.NULL)

# for RTSP ###################
def parse_args():
    parser = argparse.ArgumentParser(description='RTSP Output Sample Application Help ')
    parser.add_argument("-i", "--input",
                  help="Path to input H264 elementry stream", required=True)
    parser.add_argument("-c", "--codec", default="H264",
                  help="RTSP Streaming Codec H264/H265 , default=H264", choices=['H264','H265'])
    parser.add_argument("-b", "--bitrate", default=4000000,
                  help="Set the encoding bitrate ", type=int)
    parser.add_argument("-m", "--meta", default=0,
                  help="set past tracking meta ", type=int)
    # Check input arguments
    if len(sys.argv)==1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    args = parser.parse_args()
    global codec
    global bitrate
    global stream_path
    global past_tracking
    codec = args.codec
    bitrate = args.bitrate
    stream_path = args.input
    past_tracking = args.meta
    return 0
###############


if __name__ == '__main__':
    parse_args()
    sys.exit(main(sys.argv))
