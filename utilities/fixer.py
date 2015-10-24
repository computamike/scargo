#!/usr/bin/env python
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
# Copyright 2014 Mike Hingley
#
# This file is part of S-Cargo
#
#This program is free software: you can redistribute it and/or modify it
#under the terms of the GNU General Public License version 3, as published
#by the Free Software Foundation.

#This program is distributed in the hope that it will be useful, but
#WITHOUT ANY WARRANTY; without even the implied warranties of
#MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
#PURPOSE.  See the GNU General Public License for more details.

#You should have received a copy of the GNU General Public License along
#with this program.  If not, see <http://www.gnu.org/licenses/>.
# Update 1..2..3..4

import argparse
from lxml import etree as ET
import os
import subprocess
import json
import jinja2
import shutil
from fractions import gcd
import time
import libfixer
import sys, os
import traceback

#--Methods.
# - Many of these methods should move the lib file.

def GetRootInformation(path):
    x = os.getcwd().split(os.sep)
    root = os.sep.join(x[0:2])
    remainderPath = os.sep.join(x[0 - (len(x) - 2):])
    return root, remainderPath


def FilesAltered(cwd, Bzrfrom, bzrto):
    """Determines wich files have changed between 2 versions of a BZR Repository"""
    lshw_cmd = ['bzr', 'status',
        '-r' + str(Bzrfrom) + '..' + str(bzrto)
        ]
    os.chdir(cwd)
    proc = subprocess.Popen(lshw_cmd, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
    stdoutdata, stderrdata = proc.communicate()
    filesToRender = []
    files = stdoutdata.split('\n')
    for Modifiedfile in files:
        Modifiedfile = os.path.join(cwd, Modifiedfile .strip())
        if(os.path.isfile(Modifiedfile) and not(os.path.isdir(Modifiedfile))):
            filesToRender.append(Modifiedfile)
    return filesToRender


# Moving this to libfixer.py.  This library makes unit testing potentially easier
#def RenderSynfigScene(scene):
    #"""Renders a synfig scene to a series of png files."""
    #print "Rendering Synfig Scene " + scene
    #pathname = os.path.dirname(scene)

    #lshw_cmd = [SYNFIG_RENDER,
        #scene,
        #'-t', 'cairo_png',
        #'-w', str(WIDTH),
        #'-h', str(HEIGHT),
        #'-a', '15',
        #'-T', '4',
        #'-o', os.path.join(pathname, FRAME_NAME)
        #]
    #proc = subprocess.Popen(lshw_cmd, stdout=subprocess.PIPE,
                                        #stderr=subprocess.PIPE)
    #stdoutdata, stderrdata = proc.communicate()
    #print "Render Scene Return Code = " + str(proc.returncode)
    #return proc.returncode


def CreateVideo(Scene):
    """Creates a video from a set of images in the form Form 'Frame.xxxx.png'
    -where xxx is a leading zero frame number"""
    AVCNVFRAME_NAME = FRAME_NAME.split('.')[0] + ".%04d." + FRAME_NAME.split('.')[1]
    OUTPUT = os.path.splitext(Scene)[0] + VIDEO_FORMAT
    pathname = os.path.dirname(Scene)
    lshw_cmd = [AVCONVERTER,
               '-f', 'image2',
               '-r',FPS,
               '-y',
               '-i', os.path.join(pathname, AVCNVFRAME_NAME),
               os.path.join(pathname, OUTPUT)]
    proc = subprocess.Popen(lshw_cmd, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    proc = subprocess.Popen(lshw_cmd,)
    stdoutdata, stderrdata = proc.communicate()
    return proc.returncode


#def ClearFrames(Scene):
    #"""Clears all frames from the scene generation"""
    #import os
    #import re
    #pattern = FRAME_NAME.split(".")[0] + "\.\d+\." + FRAME_NAME.split(".")[1]
    #pathname = os.path.dirname(Scene)
    #for f in os.listdir(pathname):
        #if re.search(pattern, f):
            #os.remove(os.path.join(pathname, f))


def CreateProducer(MediaInfoObject):
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


def CreateKdenliveProducer(MediaInfoObject):
    """Creates a KdenLiveProducer for insertion into the
       kdenlive project file"""
    templatePath = os.path.dirname(os.path.realpath(__file__))
    templateLoader = jinja2.FileSystemLoader(searchpath=str(templatePath))
    templateEnv = jinja2.Environment(loader=templateLoader)
    TEMPLATE_FILE = "kdenliveproducer.xml"
    template = templateEnv.get_template(TEMPLATE_FILE)
    # Specify any input variables to the template as a dictionary.
    templateVars = {"Producer": MediaInfoObject}
    # Finally, process the templat e to produce our final text.
    outputText = template.render(templateVars)
    return outputText


def CreateKdenlivePlaylistEntry(MediaInfoObject):
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




def CalculateKdenLiveLength( SynfigNumberOfFrames, SynfigFrameRate, KdenFrameRate):
    result1 = (float(1) / float(SynfigFrameRate)) * float(SynfigNumberOfFrames)
    result2 = result1 / (float(1 )/ float(KdenFrameRate))
    result2 = int(round(result2, 0))
    return result2

#def GetMediaInformation(File, ID, _in, _out, resource, name, KFR):
    #"""Gets information about a media file - such as a rendered scene"""
    #FFMPEG_BIN = 'avprobe'
    #lshw_cmd = [FFMPEG_BIN,
        #'-show_format',
        #'-show_streams',
        #'-loglevel', 'quiet',
        #'-of', 'json',
        #File]

    #proc = subprocess.Popen(lshw_cmd, stdout=subprocess.PIPE,
                                      #stderr=subprocess.PIPE)
    #data = json.loads(proc.communicate()[0])
    #data['id'] = ID
    #data['in'] = _in
    #data['out'] = _out
    #data['resource'] = resource

    #SynfigFramesRate = data["streams"][0]["fps"]
    #SynfigFramesNumber = data["streams"][0]["nb_frames"]
    #rescaledNumberFrames = CalculateKdenLiveLength(SynfigFramesNumber, SynfigFramesRate, KFR)
    #data['NumerofFrames'] = rescaledNumberFrames
    #data['resourcename'] = name
    #filehash = CalculateFileHash(File)
    #data['FileHash'] = filehash
    #return data


def FixResources(root, Prefix, newFilename):
    """Obsolete : this was a first attempt at fixing project resources in
       KdenLive.  Use FixResources2 instead."""
    root.attrib['root'] = Prefix
    newFilename = os.path.join(newFilename, "animatic")
    for clip in root.findall("./producer/property[@name='resource']"):
        (prefix, sep, suffix) = os.path.basename(clip.text).rpartition('.')
        clip.text = os.path.join(newFilename, prefix + sep + suffix)

    #Fix the Kdenlive Producers
    for clip in root.findall("./kdenlivedoc/kdenlive_producer"):
        (prefix, sep, suffix) = os.path.basename(
                                    clip.attrib["resource"]).rpartition('.')
        clip.set('resource', os.path.join(Prefix,
                                          newFilename,
                                          prefix + sep + suffix))
    #tree.write(filename)


def findFile(BasePath, FileName):
    for directoryroot, dirs, sourcefiles in os.walk(BasePath):
        for file in sourcefiles:
            files = os.path.join(directoryroot, file)
            if (os.path.basename(files) == FileName):
                return files
            #(prefix, sep, extension) = os.path.basename(files).rpartition('.')
            #print  prefix + sep + extension + " ?= " + FileName
            #print os.path.basename(files)

def format_exception(e):
    exception_list = traceback.format_stack()
    exception_list = exception_list[:-2]
    exception_list.extend(traceback.format_tb(sys.exc_info()[2]))
    exception_list.extend(traceback.format_exception_only(sys.exc_info()[0], sys.exc_info()[1]))

    exception_str = "Traceback (most recent call last):\n"
    exception_str += "".join(exception_list)
    # Removing the last \n
    exception_str = exception_str[:-1]

    return exception_str



def FixResources2(root, CurrentProjectPath):
    """Fixes kdenlive resource references, rebasing them on the current
       project directory"""
    for clip in root.findall("./kdenlivedoc/kdenlive_producer"):
        if ('resource' in clip.attrib):
            (prefix, sep, suffix) = os.path.basename(
                                    clip.attrib["resource"]).rpartition('.')

            fileat = findFile(CurrentProjectPath, prefix + sep + suffix)
            if fileat != None and fileat != "" :
            	print "fileat = " + fileat
            	Fixed = clip.attrib["resource"].replace(ProjectPath, CurrentProjectPath)
                clip.set('resource', fileat)

    for clip in root.findall("./producer/property[@name='mlt_service']"):
        if clip.getparent().findall("property[@name='resource']") is not None:
            foobar = clip.getparent().findall("property[@name='resource']")
            if foobar[0] != None and foobar[0].text != None:
                (prefix, sep, suffix) = os.path.basename(foobar[0].text).rpartition('.')
                Fixed = foobar[0].text.replace(ProjectPath, CurrentProjectPath)
                Fixed = findFile(CurrentProjectPath, prefix + sep + suffix)
                foobar[0].text = Fixed


    for Producers in root.findall("./producer"):
        if ('resource' in clip.attrib):
            #print "[I] Fixing Producer : " + Producers.attrib["resource"]
            if (Producers.find("property[@name='mlt_service']").
                                            text not in INVALID_PRODUCERTYPES):
                resource = Producers.find("property[@name='resource']").text
                FullResourcePath = os.path.join(mltRoot, resource)
                FullResourcePath = FullResourcePath.replace(ProjectPath,
                                                            CurrentProjectPath)
                Producers.find("property[@name='resource']").text = '/'.join(FullResourcePath.split('/')[1:])
    SetMltRoot(root, '/')



def GetProjectRoot(root):
    """Returns the Project root from the Kdenlive project tree"""
    return root.find("kdenlivedoc").attrib["projectfolder"]

def GetProjectSpeed(root):
    """Returns the FPS from the Kdenlive project tree"""
    return root.find("profile").attrib["frame_rate_num"]


def SetProjectRoot(root, NewRoot):
    """Sets the Project root for the Kdenlive project tree"""
    root.find("kdenlivedoc").attrib["projectfolder"] = NewRoot


def GetMltRoot(root):
    """Returns the MLT Root - this method may become obsolete"""
    return root.attrib["root"]


def SetMltRoot(root, Val):
    """Sets the MLT root - this method may become obsolete"""
    root.attrib["root"] = Val


def FixClip(root, newFilename,kdenrate):
    """Replaces a animatic frame with a rendered video - if required."""
    (destprefix, destsep, destsuffix) = os.path.basename(newFilename).rpartition('.')
    fixerObject = libfixer.FixerLibrary()
    for Producers in root.findall("./producer"):
        #foo2 = Producers.find("property[@name='mlt_service']").text
        if (Producers.find("property[@name='mlt_service']").text not in INVALID_PRODUCERTYPES):
            clip = Producers.find("property[@name='resource']")
            if (clip != None):
                (prefix, sep, suffix) = os.path.basename(clip.text).rpartition('.')
                #mltRoot = GetMltRoot(root)
                if (prefix.upper() == destprefix.upper()):
                    #print mltRoot+prefix
                    parent = clip.getparent()
                    _id = parent.attrib["id"]
                    _in = parent.attrib["in"]
                    _out = parent.attrib["out"]
                    foo = ET.fromstring(
                        CreateProducer
                        (
                            fixerObject.GetMediaInformation(
                                newFilename,
                                _id,
                                _in,
                                _out,
                                newFilename[1:],
                                "",
                                kdenrate
                            )
                        )
                    )
                    parent.getparent().replace(parent, foo)

                    # Fix the Playlist:
                    for PlayListEntry in root.findall("./playlist/entry[@id='" + _id + "']"):
                        fooVar = fixerObject.GetMediaInformation(
                            newFilename,
                            _id,
                            _in,
                            _out,
                            newFilename[1:],
                            "",
                            kdenrate
                            )
                        Varentry = CreateKdenlivePlaylistEntry(fooVar)

                    for clip in root.findall("./kdenlivedoc/kdenlive_producer[@id='" + _id + "']"):
                        groupID = clip.attrib["groupid"]
                        groupName = clip.attrib["groupname"]
                        foo2 = ET.fromstring(
                            fixerObject.CreateKdenliveProducer
                            (
                                fixerObject.GetMediaInformation(
                                    newFilename,
                                    _id,
                                    _in,
                                    _out,
                                    newFilename[1:],
                                    "",
                                    kdenrate
                                ),
                                groupName,
                                groupID
                            )
                        )
                        clip.getparent().replace(clip,foo2)
                        #kdenlive_producer duration="120" frame_size="640x480" in="0" analysisdata="" file_size="320239" groupid="5" aspect_ratio="1" out="119" groupname="Storyboard" file_hash="cfbd78a6591ff1b7c2760bfbc9881fc7" type="5" id="81" name="scene_13.png" resource="/home/mike/projects/github/scargo/scenes/scene_13.png"/>



    return root


def CalculateFileHash(filename):
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


def FindApplication(renderer):
    """Locate an application"""
    WHEREIS_BIN = 'whereis'
    lshw_cmd = [WHEREIS_BIN,
        '-b',
        renderer
        ]
    proc = subprocess.Popen(lshw_cmd, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)
    return proc.communicate()[0].split(' ')[1]


def CreateRenderShellScript(NewRoot, NewPath):
    """Creates a new Render script."""
    (prefix, sep, extension) = os.path.basename(filename).rpartition('.')
    SCRIPT = filename + ".sh"
    Output = filename + ".mp4"
    Renderer = FindApplication('kdenlive_render')
    Melt = FindApplication('melt')
    if (Renderer is None):
        raise Exception("Unable to find renderer")
    if (Melt is None):
        raise Exception("Unable to find Melt")
    ShellScript = os.path.join(NewRoot, NewPath, SCRIPT)
    source = os.path.join(NewRoot, NewPath, SCRIPT + ".mlt")
    target = os.path.join(NewRoot, NewPath, Output).replace(' ', '%20')
    source_data = {}
    source_data['Source'] = source.replace(' ', '%20')
    source_data['Target'] = target
    source_data['Renderer'] = Renderer
    source_data['Melt'] = Melt
    source_data['Width'] = WIDTH
    source_data['Height'] = HEIGHT
    source_data['AspectRatio'] = str(WIDTH / gcd(WIDTH, HEIGHT)) + \
                                         '/' + str(HEIGHT / gcd(WIDTH, HEIGHT))
    templatePath = os.path.dirname(os.path.realpath(__file__))
    templateLoader = jinja2.FileSystemLoader(searchpath=str(templatePath))
    templateEnv = jinja2.Environment(loader=templateLoader)
    TEMPLATE_FILE = "animatic.sh.template"
    template = templateEnv.get_template(TEMPLATE_FILE)
    print("Writing " + ShellScript)
    #
    # Specify any input variables to the template as a dictionary.
    templateVars = {"source": source_data}
    OutputText = template.render(templateVars)
    OutputText = OutputText
    with open(ShellScript, "w") as text_file:
        text_file.write(OutputText)
    os.chmod(ShellScript, 0744)


def CopyKdenLiveFileToMLT(kdenLive):
    """Creates a new MLT file from a kdenLive file."""
    SCRIPT = filename + ".sh"
    meltFile = os.path.join(NewRoot, NewPath, SCRIPT + ".mlt")
    shutil.copy(filename, meltFile)

def ClearWorklist(worklist, rootpath):
    with open(worklist) as f:
        for line in f:
            base_file, ext = os.path.splitext(line)
            print "Clearing Video for" + line
            print "basefile="+base_file.strip()
            print "ext = "+ ext.strip()
            print "rootpath="+rootpath.strip()

            # os.rename(filename, base_file + ".text")
            video = os.path.join(rootpath, base_file + ".mp4")
            exists = os.path.exists(video)
            print video
            print "... " + str(exists)
            if (exists):
                os.remove(video)

try:
    parser = argparse.ArgumentParser(
        prog='Fixer',
        description='Jenkins / KDE animatic production utilities',
        epilog="""
        This script builds Synfig scenes into animations, and regenerates a
        KdenLive \n project.""")

    parser.add_argument('-width', type=int, help=('width of the generated '
    'frame (by default 640)'), default=320)
    parser.add_argument('-height', type=int, help='height of the generated '
    'frame (by default 480)', default=240)
    parser.add_argument('-frame', help='Name of generated frame '
    '(default frame.png)', default='frame.png')
    parser.add_argument('-fps', help='Framerate of generated animation '
    '(default 24)', default='24')
    parser.add_argument('-kdenlive', help='KdenLive project to update '
    '(default storyboard.kdenlive)', default='storyboard.kdenlive')
    parser.add_argument('-fix', action='store_true', default=False,
                        help='Fixer only fixes project references')

    parser.add_argument('-workfile', default=None,
                        help='''Fixer can operate through files identified in
                        the workfile, rather than the whole project.  A work
                        file should show the files to process.
                        project references''')
    args = parser.parse_args()

    # Animatic Constants
    VALID_EXTENSIONS = ["SIF", "SIFZ"]
    IMAGE_EXTENSIONS = ["PNG", "MP3", "WAV", "MP4"]
    INVALID_PRODUCERTYPES = ["kdenlivetitle", "colour"]
    WIDTH = args.width
    HEIGHT = args.height
    FPS = args.fps
    FRAME_NAME = args.frame
    VIDEO_FORMAT = ".mp4"

    # Applications used in rendering :
    FIX_ONLY = args.fix
    WORKFILE = args.workfile
    SYNFIG_RENDER = "synfig"
    AVCONVERTER = "avconv"
    NewRoot, NewPath = GetRootInformation(os.getcwd())
    filename = args.kdenlive
    fixerObject = libfixer.FixerLibrary()
    print ("                                       ")
    print ("  ______ _ _             ______ _      ")
    print (" |  ____(_) |           |  ____(_)     ")
    print (" | |__   _| |_ __ ___   | |__   ___  __")
    print (" |  __| | | | '_ ` _ \  |  __| | \ \/ /")
    print (" | |    | | | | | | | | | |    | |>  < ")
    print (" |_|    |_|_|_| |_| |_| |_|    |_/_/\\_\\")
    print ("                                       ")
    #print "                                       ")
    print ("Passed Parameters")
    print ("-----------------")
    #print ("From Version       : " + str(VERSIONFROM))
    #print ("To version         : " + str(VERSIONTO))
    print("Frame Width        : " + str(WIDTH))
    print("Frame Height       : " + str(HEIGHT))
    print("Frames Per Second  : " + str(FPS))
    print("Frame Name         : " + FRAME_NAME)
    print("Kdenlive           : " + filename)
    print("Root               : " + NewRoot)
    print("Path               : " + NewPath)
    print(" ")
    print("Fix Only           : " + str(FIX_ONLY))
    print("WorkFile           : " + str(WORKFILE))

    print (" ")
    
    
    # What this script does
    # ---- ---- ------ ----
    # This script can perform a number of tasks and these tasks can be switched
    # on or off through the use of command flags.
    #
    # 1. Fix the KdenLive file, re-writing it's project roots
    # 2. Clears any movie files that exist for any scenes that are referenced 
    # in the workfile
    #
    # Find All files
    print ("Job started at     : " + time.strftime("%c"))
    if not os.path.exists(filename):
        raise Exception('Kdenlive Project file specified does not exist.')
    tree = ET.parse(filename)
    root = tree.getroot()
    ProjectPath = GetProjectRoot(root)
    KdenLiveSpeed = GetProjectSpeed(root)
    mltRoot = GetMltRoot(root)
    CurrentProjectPath = os.getcwd()
    print("ProjectPath        :" + ProjectPath)
    print("CurrentProjectPath :" + CurrentProjectPath)
    print("mltRoot            :" + mltRoot)
    
    SetProjectRoot(root, CurrentProjectPath)
    FixResources2(root, CurrentProjectPath)
    tree.write(os.path.join(CurrentProjectPath, filename))
    
    
    if (FIX_ONLY is False):
	if (WORKFILE is not None):
	    ClearWorklist(os.path.join(CurrentProjectPath, WORKFILE),os.getcwd())

        for directoryroot, dirs, sourcefiles in \
	    os.walk(os.path.join(NewRoot, NewPath)):
            for file in sourcefiles:
                files = os.path.join(directoryroot, file)
                (prefix, sep, extension) = os.path.basename(files).rpartition('.')
		print "Processing file"
                if (extension.upper() in VALID_EXTENSIONS):
                    VideoFile= os.path.join( directoryroot ,file.split(".")[0] +VIDEO_FORMAT)
                    newFilename = os.path.join(os.path.dirname(files),
                        prefix + VIDEO_FORMAT)
                    animaticVideFile = os.path.join(os.getcwd(), os.path.basename(newFilename))
                    if (not os.path.isfile(VideoFile)):
                        fixerObject.RenderSynfigScene(files, WIDTH, HEIGHT, FRAME_NAME)
                        (prefix, sep, suffix) = os.path.basename(files).rpartition('.')
                        fixerObject.CreateVideo(files, FRAME_NAME)
                        fixerObject.ClearFrames(files, FRAME_NAME)
		    FixClip(root, newFilename,KdenLiveSpeed)
    tree.write(os.path.join(CurrentProjectPath, filename))

    # Fix the Production Scripts
    print "Creating Render Shell Script"
    CreateRenderShellScript(NewRoot, NewPath)
    CopyKdenLiveFileToMLT(filename)


    #tree.write(filename)

except Exception as inst:
    #print type(inst)     # the exception instance
    #print inst.args      # arguments stored in .args
    print("ERROR : " + str(inst))
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    print "Printing only the traceback above the current stack frame"
    print "".join(traceback.format_exception(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2]))
    print
    print "Printing the full traceback as if we had not caught it here..."
    print format_exception(inst)
