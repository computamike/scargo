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
                                                                                                                                
                                                                                                                                
import argparse                                                                                                                 
from lxml import etree as ET                                                                                                    
import os                                                                                                                       
import subprocess                                                                                                               
import json                                                                                                                     
import jinja2                                                                                                                   
import shutil                                                                                                                   
from fractions import gcd                                                                                                       
import time     


#--Methods.                                                                                                                     
                                                                                                                            
                                                                                                                                
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
                                                                                                                                
                                                                                                                                
def RenderSynfigScene(scene):                                                                                                   
    """Renders a synfig scene to a series of png files."""                                                                      
    print "Rendering Synfig Scene " + scene
    pathname = os.path.dirname(scene)                                                                                           

    lshw_cmd = [SYNFIG_RENDER,                                                                                                  
        scene,                                                                                                                  
        '-t', 'cairo_png',                                                                                                      
        '-w', str(WIDTH),                                                                                                       
        '-h', str(HEIGHT),                                                                                                      
        '-a', '15',                                                                                                             
        '-T', '4',                                                                                                              
        '-o', os.path.join(pathname, FRAME_NAME)                                                                                
        ]                                                                                                                       
    proc = subprocess.Popen(lshw_cmd, stdout=subprocess.PIPE,                                                                   
                                        stderr=subprocess.PIPE)                                                                 
    stdoutdata, stderrdata = proc.communicate()   
    print "Render Scene Return Code = " + str(proc.returncode)
    return proc.returncode                                                                                                      
                                                                                                                                
                                                                                                                                
def CreateVideo(Scene):                                                                                                         
    """Creates a video from a set of images in the form Form 'Frame.xxxx.png'                                                    
    -where xxx is a leading zero frame number"""                                                                                
    AVCNVFRAME_NAME = FRAME_NAME.split('.')[0] + ".%04d." + FRAME_NAME.split('.')[1]                                                                                  
    OUTPUT = os.path.splitext(Scene)[0] + VIDEO_FORMAT                                                                          
    pathname = os.path.dirname(Scene)                                                                                           
    lshw_cmd = [AVCONVERTER,                                                                                                    
               '-f', 'image2',                                                                                                  
               '-y',                                                                                                            
               '-i', os.path.join(pathname, AVCNVFRAME_NAME),                                                                   
               os.path.join(pathname, OUTPUT)]                                                                                  
    proc = subprocess.Popen(lshw_cmd, stdout=subprocess.PIPE,                                                                   
                            stderr=subprocess.PIPE)                                                                             
    proc = subprocess.Popen(lshw_cmd,)                                                                                          
    stdoutdata, stderrdata = proc.communicate()                                                                                 
    return proc.returncode                                                                                                      
                                                                                                                                
                                                                                                                                
def ClearFrames(Scene):                                                                                                         
    """Clears all frames from the scene generation"""                                                                           
    import os                                                                                                                   
    import re                                                                                                                   
    pattern = FRAME_NAME.split(".")[0] + "\.\d+\." + FRAME_NAME.split(".")[1]                                                   
    pathname = os.path.dirname(Scene)                                                                                           
    for f in os.listdir(pathname):                                                                                              
        if re.search(pattern, f):                                                                                               
            os.remove(os.path.join(pathname, f))                                                                                
                                                                                                                                
                                                                                                                                
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
                                                                                                                                
                                                                                                                                
def GetMediaInformation(File, ID, _in, _out, resource, name):                                                                   
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
    data['resource'] = resource                                                                                                 
    data['NumerofFrames'] = _out                                                                                                
    data['resourcename'] = name  
    print "----  VERY IMPORTANT ---- "
    print " CALCULATING HASH OF FILE " + File
    hash = CalculateFileHash(File)
    data['FileHash'] = hash
    return data                                                                                                                 
                                                                                                                                
                                                                                                                                
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
                                                                                                                                
                                                                                                                                
def FixResources2(root, CurrentProjectPath):                                                                                    
    """Fixes kdenlive resource references, rebasing them on the current                                                         
       project directory"""                                                                                                     
    for clip in root.findall("./kdenlivedoc/kdenlive_producer"):                                                                
        if ('resource' in clip.attrib):                                                                                         
            (prefix, sep, suffix) = os.path.basename(                                                                           
                                    clip.attrib["resource"]).rpartition('.')                                                    
            Fixed = clip.attrib["resource"].replace(ProjectPath,                                                                
                                                            CurrentProjectPath)                                                 
            clip.set('resource', Fixed)                                                                                         
    for clip in root.findall("./producer/property[@name='mlt_service']"): 
        if (clip.text == "avformat"):
            foobar = clip.getparent().find("property[@name='resource']")
            (prefix, sep, suffix) = os.path.basename(foobar.text).rpartition('.')                                                    
            Fixed = foobar.text.replace(ProjectPath, CurrentProjectPath)
            foobar.text = Fixed   


                                                                                                                                
    for Producers in root.findall("./producer"):                                                                                
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
                                                                                                                                
                                                                                                                                
def SetProjectRoot(root, NewRoot):                                                                                              
    """Sets the Project root for the Kdenlive project tree"""                                                                   
    root.find("kdenlivedoc").attrib["projectfolder"] = NewRoot                                                                  
                                                                                                                                
                                                                                                                                
def GetMltRoot(root):                                                                                                           
    """Returns the MLT Root - this method may become obsolete"""                                                                
    return root.attrib["root"]                                                                                                  
                                                                                                                                
                                                                                                                                
def SetMltRoot(root, Val):                                                                                                      
    """Sets the MLT root - this method may become obsolete"""                                                                   
    root.attrib["root"] = Val                                                                                                   
                                                                                                                                
                                                                                                                                
def FixClip(root, newFilename):                                                                                                 
    """Replaces a animatic frame with a rendered video - if required."""     
    print " -- INFO :Replacing the animcatic frame with rendered video"
    (destprefix, destsep, destsuffix) = os.path.basename(newFilename).rpartition('.')                                                 
    
    for Producers in root.findall("./producer"):  
        foo2 = Producers.find("property[@name='mlt_service']").text
        #print " -- THIS IS THE TEXT OF THE PRODUCER "+foo2
        if (Producers.find("property[@name='mlt_service']").text not in INVALID_PRODUCERTYPES): 
            #print "Producer in file : " + str(Producers.text)
            #print "Producer Type : " + Producers.find("property[@name='mlt_service']").text
            clip = Producers.find("property[@name='resource']")                                                                 
            (prefix, sep, suffix) = os.path.basename(clip.text).rpartition('.')                                                 
            print "====="
            print "clip      :" + ET.tostring(clip)
            #print "Resource  :" 
            print "prefix    :" + prefix
            #print "sep       :" + sep
            #print "suffix    :" + suffix
            print "destprefix:"+destprefix
            mltRoot = GetMltRoot(root)           
            #print "mltRoot   :"+mltRoot
                       
            if (prefix.upper() == destprefix.upper()): 
                #print mltRoot+prefix
                parent = clip.getparent()                                                                                       
                _id = parent.attrib["id"]                                                                                       
                _in = parent.attrib["in"]                                                                                       
                _out = parent.attrib["out"]  
                print "Found Producer..." 
                foo = ET.fromstring(                                                                                            
                    CreateProducer                                                                                              
                    (                                                                                                           
                        GetMediaInformation(                                                                                    
                            newFilename,                                                                                        
                            _id,                                                                                                
                            _in,                                                                                                
                            _out,                                                                                               
                            newFilename[1:],                                                                                    
                            ""                                                                                                  
                        )                                                                                                       
                    )                                                                                                           
                )    
                print "=== NEW PRODUCER ==="
                print ET.tostring(foo)
                print "===================="
                parent.getparent().replace(parent, foo)   
                print ET.tostring(parent)
                print "=== END OF FIX CLIP STUFF==="
                
# Last step : Create a new kdenlist_producernode                 
            #print "END HERE"
        #Fix the Kdenlive Producers                                                                                             
                print "FIXING kdenlive_produce [timeline].. " +_id
                for clip in root.findall("./kdenlivedoc/kdenlive_producer[@id='" + _id + "']"):  
                    print ET.tostring(clip)
                print "FIXING kdenlive_produce [timeline] : END"
#        print ET.tostring(clip)
#        if ('resource' in clip.attrib):                                                                                         
#            (prefix, sep, suffix) = os.path.basename(clip.attrib["resource"]).rpartition('.') 
#            #print "prefix     : " + clip.attrib["resource"]
#            #print "destprefix : " + destprefix
#            #print "newFilename: " + newFilename
#            if (prefix == destprefix):                                                                                          
#                #Adding in a new Producer for the New Video File.
#                foo = ET.fromstring(CreateKdenliveProducer(GetMediaInformation(newFilename, _id, _in, _out,newFilename, destprefix + destsep + destsuffix)))                                                             
#                clip.getparent().replace(clip, foo)                           
                
    return root
                                                                  
                                                                                                                                
def CalculateFileHash(filename):
    print "HASHING " + filename
    size = os.path.getsize(filename)
    file = open(filename, 'rb')
    if(size > (1000000*2)):
        file.seek(0)
        fileData = file.read(1000000)
        file.seek(1000000,2) #Seek last 1000000 bytes
        fileData.append(file.read(1000000))
    else:
        fileData = file.read()
    import hashlib
    m = hashlib.md5()
    m.update(fileData)
    print m.hexdigest()       
    fileHash =m.hexdigest()
    print fileHash
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
    print NewRoot                                                                                                               
    print NewPath                                                                                                               
    print filename                                                                                                              
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
    target = os.path.join(NewRoot, NewPath, Output).replace(' ','%20')                                                          
    source_data = {}                                                                                                            
    source_data['Source'] = source.replace(' ','%20')                                                                           
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
    print "Writing " + ShellScript                                                                                              
    print                                                                                                                       
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
                                                                                                                                
                                                                                                                                
                                                                                                                                
                                                                                                                                
try:                                                                                                                            
    parser = argparse.ArgumentParser(                                                                                           
        prog='Fixer',                                                                                                           
        description='Jenkins / KDE animatic production utilities',                                                              
        epilog="""                                                                                                              
This script builds Synfig scenes into animations, and regenerates a KdenLive \n                                                 
project.  If bzrto or bzrfrom is not passed, or is passed as 0, then %(prog)s\n                                                 
will just fix project resource references.                                                                                      
        """)                                                                                                                    
                                                                                                                                
    parser.add_argument('-width', type=int, help=('width of the generated '                                                     
    'frame (by default 640)'), default=640)                                                                                     
    parser.add_argument('-height', type=int, help='height of the generated '                                                    
    'frame (by default 480)', default=480)                                                                                      
    parser.add_argument('-frame', help='Name of generated frame '                                                               
    '(default frame.png)', default='frame.png')                                                                                 
    parser.add_argument('-fps', help='Framerate of generated animation '                                                        
    '(default 25)', default='25')                                                                                               
    parser.add_argument('-kdenlive', help='KdenLive project to update '                                                         
    '(default storyboard.kdenlive)', default='storyboard.kdenlive')                                                             
    parser.add_argument('-fix',action='store_true', default=False ,  help='Fixer only fixes project references' )               
    args = parser.parse_args()                                                                                                  
                                                                                                                                
    # Animatic Constants                                                                                                        
    VALID_EXTENSIONS = ["SIF", "SIFZ"]  
    IMAGE_EXTENSIONS = ["PNG","MP3","WAV","MP4"]
    INVALID_PRODUCERTYPES = ["kdenlivetitle", "colour"]                                                                         
    WIDTH = args.width                                                                                                          
    HEIGHT = args.height                                                                                                        
    FPS = args.fps                                                                                                              
    FRAME_NAME = args.frame                                                                                                     
    VIDEO_FORMAT = ".mp4"                                                                                                       

    # Applications used in rendering :                                                                                          
    FIX_ONLY = args.fix                                                                                                         
    SYNFIG_RENDER = "synfig"                                                                                                    
    AVCONVERTER = "avconv"                                                                                                      
    NewRoot, NewPath = GetRootInformation(os.getcwd())                                                                          
    filename = args.kdenlive                                                                                                    
                                                                                                                                
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
    print ("Frame Width        : " + str(WIDTH))                                                                                
    print ("Frame Height       : " + str(HEIGHT))                                                                               
    print ("Frames Per Second  : " + str(FPS))                                                                                  
    print ("Frame Name         : " + FRAME_NAME)                                                                                
    print ("Kdenlive           : " + filename)                                                                                  
    print ("Root               : " + NewRoot)                                                                                   
    print ("Path               : " + NewPath)                                                                                   
    print (" ")                                                                                                                 
    print ("Fix Only           : " + str(FIX_ONLY))                                                                             
    print (" ")                                                                                                                 
    # Find All files                                                                                                            
    print "Job started at      : " + time.strftime("%c")                                                                                                                            
    if not os.path.exists(filename):                                                                                            
        raise Exception('Kdenlive Project file specified does not exist.')                                                                       
    tree = ET.parse(filename)                                                                                                   
    root = tree.getroot()                                                                                                       
    ProjectPath = GetProjectRoot(root)                                                                                          
    mltRoot = GetMltRoot(root)                                                                                                  
    CurrentProjectPath = os.getcwd()                                                                                            
    print ("ProjectPath        :" + ProjectPath)                                                                                
    print ("CurrentProjectPath :" + CurrentProjectPath)                                                                         
    print ("mltRoot            :" + mltRoot)                                                                                    
    #print "TESTING HASH" + CalculateFileHash("/home/mike/projects/scargo/scenes/tux/Tux.png")
    #print " should be : 7ed8a808420a41cc91afa6236e7a1dd4"
    SetProjectRoot(root, CurrentProjectPath) 
    if(FIX_ONLY):
        FixResources2(root, CurrentProjectPath)                                                                                     
        tree.write(os.path.join(CurrentProjectPath,filename))  
    if (FIX_ONLY == False):
        FixResources2(root, CurrentProjectPath)     
        tree.write(os.path.join(CurrentProjectPath,filename))
        ##print "FIX ONLY NOT SPECIFIED"      
        ##print "Walking from :" + NewPath
        for directoryroot,dirs,sourcefiles in os.walk(os.path.join(NewRoot, NewPath)):                                                             
            for file in sourcefiles: 
                ##print "walking solution : " + file
                files = os.path.join(directoryroot,file)                                                                        
                (prefix, sep, extension) = os.path.basename(files).rpartition('.')                                              
                if (extension.upper() in IMAGE_EXTENSIONS):
                    print "== FIXING " + files
                    print "== FIXING " + file
                    print "================="                    
                    
                    # Some Asset needs re-writing
                    FixClip(root, files)   
                
                if (extension.upper() in VALID_EXTENSIONS):
                    if (RenderSynfigScene(files) == 0):                                                                         
                        (prefix, sep, suffix) = os.path.basename(files).rpartition('.')
                        CreateVideo(files)                                                                                      
                        ClearFrames(files)                                                                                      
                        newFilename = os.path.join(os.path.dirname(files),                                                      
                        prefix + VIDEO_FORMAT)                                                                                  
                        animaticVideFile = os.path.join(os.getcwd(),                                                            
                                                 os.path.basename(newFilename))                                                 
                        #print "Video moved to" + animaticVideFile                                                              
                        #shutil.move(newFilename, animaticVideFile)                                                          
                        ##print " -- FIXING CLIP"
                        FixClip(root, newFilename)   
                        ##print "== OLD ROOT=="
                        ##print ET.tostring(root)
                        ##print "== NEW ROOT=="
                        ##print ET.tostring(newroot)
                        
                        ##print " -- FIXING CLIP : DONE"
                        ##print "Writing to filename : " + os.path.join(CurrentProjectPath,filename)
    tree.write(os.path.join(CurrentProjectPath,filename))                                                                                                        
 
    # Fix the Production Scripts                                                                                                
    print "Creating Render Shell Script"                                                                                        
    CreateRenderShellScript(NewRoot, NewPath)                                                                                   
    CopyKdenLiveFileToMLT(filename)                                                                                             
                                                                                                                                
                                                                                                                                
    #tree.write(filename)                                                                                                        
                                                                                                                                
except Exception as inst:                                                                                                       
    #print type(inst)     # the exception instance                                                                              
    #print inst.args      # arguments stored in .args                                                                           
    print "ERROR : " + str(inst)      
