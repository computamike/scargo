#!/usr/bin/env python
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
# Copyright 2014 Mike Hingley
#import argparse
#from lxml import etree as ET
import os
import subprocess
import json
import jinja2
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


    def CalculateKdenLiveLength(self, SynfigNumberOfFrames, SynfigFrameRate, KdenFrameRate):
        result1 = (float(1) / float(SynfigFrameRate)) * float(SynfigNumberOfFrames)
        result2 = result1 / (float(1 )/ float(KdenFrameRate))
        result2 = int(round(result2, 0))
        return result2


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

    def CalculateFileHash(self, filename):
        size = os.path.getsize(filename)
        fileToHash = open(filename, 'rb')
        if(size > (1000000 * 2)):
            fileToHash.seek(0)
            fileData = file.read(1000000)
            fileToHash.seek(1000000, 2)  # Seek last 1000000 bytes
            fileData = fileData + file.read(1000000)
            #fileData.append(file.read(1000000))
        else:
            fileData = fileToHash.read()
        import hashlib
        m = hashlib.md5()
        m.update(fileData)
        fileHash = m.hexdigest()
        return fileHash

    def oldGetMediaInformation(self, File, ID, _in, _out, resource, name):
        """Gets information about a media file - such as a rendered scene"""
        FFMPEG_BIN = 'avprobe'
        lshw_cmd = [FFMPEG_BIN,
            '-show_format',
            '-show_streams',
            '-loglevel', 'quiet',
            '-of', 'json',
            File]

        proc = subprocess.Popen(lshw_cmd, stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE)
        data = json.loads(proc.communicate()[0])
        data['id'] = ID
        data['in'] = _in
        data['out'] = int(data["streams"][0]["nb_frames"])-1
        data['fps'] = data["streams"][0]["avg_frame_rate"].split("/")[0]
        data['codec_long_name'] = data["streams"][0]["codec_long_name"]
        data['resource'] = resource
        data['NumerofFrames'] = data["streams"][0]["nb_frames"]
        data['resourcename'] = name
        filehash = self.CalculateFileHash(File)
        data['FileHash'] = filehash
        return data


    def GetMediaInformation(self, File, ID, _in, _out, resource, name, KFR):
        """Gets information about a media file - such as a rendered scene"""
        FFMPEG_BIN = 'avprobe'
        lshw_cmd = [FFMPEG_BIN,
            '-show_format',
            '-show_streams',
            '-loglevel', 'quiet',
            '-of', 'json',
            File]

        proc = subprocess.Popen(lshw_cmd, stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE)
        data = json.loads(proc.communicate()[0])
        data['id'] = ID
        data['in'] = _in
        data['out'] = _out
        data['resource'] = File
        data['bitrate'] = data["streams"][0]["bit_rate"].split(".")[0]
        data['FileSize'] = data["format"]["size"].split(".")[0]
        data['resourcename'] = os.path.basename(File)

        dividend = float(data["streams"][0]["avg_frame_rate"].split("/")[0])
        divisor = float(data["streams"][0]["avg_frame_rate"].split("/")[1])

        data['fps'] = round(dividend / divisor,2)
        SynfigFramesRate = data['fps']
        SynfigFramesNumber = data["streams"][0]["nb_frames"]
        rescaledNumberFrames = self.CalculateKdenLiveLength(SynfigFramesNumber, SynfigFramesRate, KFR)
        data['NumerofFrames'] = rescaledNumberFrames
        data['SynfigNumberOfFrames'] = SynfigFramesNumber
        #data['resourcename'] = name
        filehash = self.CalculateFileHash(File)
        data['FileHash'] = filehash
        data['KDENLiveFrameRate'] = KFR
        return data




    def CreateProducer(self, MediaInfoObject):
        """Creates a Producer xml object for insertion into the
           kdenlive project file"""
        templatePath = os.path.dirname(os.path.realpath(__file__))
        templateLoader = jinja2.FileSystemLoader(searchpath=str(templatePath))
        templateEnv = jinja2.Environment(loader=templateLoader)
        TEMPLATE_FILE = "producers.xml"
        template = templateEnv.get_template(TEMPLATE_FILE)
        templateVars = {"Producer": MediaInfoObject}
        outputText = template.render(templateVars)
        return outputText

    def CreateKdenliveProducer(self, MediaInfoObject, GroupName, GroupID):
        """Creates a KdenLiveProducer for insertion into the
           kdenlive project file"""
        templatePath = os.path.dirname(os.path.realpath(__file__))
        templateLoader = jinja2.FileSystemLoader(searchpath=str(templatePath))
        templateEnv = jinja2.Environment(loader=templateLoader)
        TEMPLATE_FILE = "kdenliveproducer.xml"
        template = templateEnv.get_template(TEMPLATE_FILE)
        # Specify any input variables to the template as a dictionary.
        MediaInfoObject['GroupName'] = GroupName
        MediaInfoObject['GroupID'] = GroupID
        templateVars = {"Producer": MediaInfoObject}
        # Finally, process the templat e to produce our final text.
        outputText = template.render(templateVars)
        return outputText


    def CreateKdenlivePlaylistEntry(self, MediaInfoObject):
        """Creates a KdenLiveProducer for insertion into the
           kdenlive project file"""
        templatePath = os.path.dirname(os.path.realpath(__file__))
        templateLoader = jinja2.FileSystemLoader(searchpath=str(templatePath))
        templateEnv = jinja2.Environment(loader=templateLoader)
        TEMPLATE_FILE = "PlaylistEntry.xml"
        template = templateEnv.get_template(TEMPLATE_FILE)
        # Specify any input variables to the template as a dictionary.
        templateVars = {"Producer": MediaInfoObject}
        # Finally, process the templat e to produce our final text.
        outputText = template.render(templateVars)
        return outputText


if __name__ == '__main__':
    print"Libfixer is a module for kdenlive fixings."