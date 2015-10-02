#!/usr/bin/env python
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
# Copyright 2014 Mike Hingley
#import argparse
#from lxml import etree as ET
import os
import subprocess
#import json
#import jinja2
#import shutil
#from fractions import gcd
#import time

AVCONVERTER = "avconv"
VIDEO_FORMAT = ".mp4"
SYNFIG_RENDER = "synfig"


class FixerLibrary(object):
    def __init__(self):
        pass

    def print_func(self, par):
       print "Hello : ", par

    def RenderSynfigScene(self, scene, WIDTH, HEIGHT, FRAME_NAME):
        """Renders a synfig scene to a series of png files."""
        print "Rendering Synfig Scene " + scene
        pathname = os.path.dirname(scene)

        lshw_cmd = [SYNFIG_RENDER,
            scene,
            '-t', 'cairo_png',
            '-w', str(WIDTH),
            '-h', str(HEIGHT),
            '--fps', '24',
            '-a', '15',
            '-T', '4',
            '-o', os.path.join(pathname, FRAME_NAME)
            ]
        print lshw_cmd
        proc = subprocess.Popen(lshw_cmd, stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE)
        stdoutdata, stderrdata = proc.communicate()
        print "Render Scene Return Code = " + str(proc.returncode)
        return proc.returncode

    def CreateVideo(self, Scene, FRAME_NAME):
        """Creates a video from a set of images in the form Form
        'Frame.xxxx.png' -where xxx is a leading zero frame number"""
        AVCNVFRAME_NAME = FRAME_NAME.split('.')[0] + ".%04d." + \
                          FRAME_NAME.split('.')[1]
        OUTPUT = os.path.splitext(Scene)[0] + VIDEO_FORMAT
        pathname = os.path.dirname(Scene)
        lshw_cmd = [AVCONVERTER,
                   '-framerate', '24',
                   '-y',
                   '-i', os.path.join(pathname, AVCNVFRAME_NAME),
                   '-r', '24',
                   os.path.join(pathname, OUTPUT)]
        proc = subprocess.Popen(lshw_cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        proc = subprocess.Popen(lshw_cmd,)
        stdoutdata, stderrdata = proc.communicate()
        print lshw_cmd
        return proc.returncode

    def ClearFrames(self, Scene, FRAME_NAME):
        """Clears all frames from the scene generation"""
        import os
        import re
        pattern = FRAME_NAME.split(".")[0] + "\..+\." + FRAME_NAME.split(".")[1]

        pathname = os.path.dirname(Scene)
        for f in os.listdir(pathname):
            if re.search(pattern, f):
                os.remove(os.path.join(pathname, f))


if __name__ == '__main__':
    print"Libfixer is a module for kdenlive fixings."