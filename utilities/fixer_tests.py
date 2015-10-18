#!/usr/bin/env python
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
# Copyright 2014 Mike Hingley
import unittest
import libfixer

# These unit tests aren't really good unit tests - they test specific conditions
# that occured during development of the SCARGO project, and are more accurately
# integration tests.  These tests are kept with a view that eventually coverage
# will be improved
class testLibFixer(unittest.TestCase):

    def testSeeWhatHappensWhenWeRenderScene20(self):
        f = libfixer.FixerLibrary()
        scene = "/home/mike/projects/github/scargo/scenes/scene_2.sif"
        f.RenderSynfigScene(scene, 960,540, "frame.png")
        f.CreateVideo(scene, "frame.png")
        f.ClearFrames(scene, "frame.png")

    #def testSeeWhatHappensWhenWeRenderScene12And13(self):
        #f = libfixer.FixerLibrary()
        #scene = "/home/mike/projects/github/scargo/scenes/scene_12.sif"
        #f.RenderSynfigScene(scene, 320, 240, "frame.png")
        #f.CreateVideo(scene, "frame.png")
        #f.ClearFrames(scene, "frame.png")
        #scene = "/home/mike/projects/github/scargo/scenes/scene_13.sif"
        #f.RenderSynfigScene(scene, 320, 240, "frame.png")
        #f.CreateVideo(scene, "frame.png")
        #f.ClearFrames(scene, "frame.png")

    #def testJustRenderScene12frames(self):
        #f = libfixer.FixerLibrary()
        #scene = "/home/mike/projects/github/scargo/scenes/scene_12.sif"
        #f.RenderSynfigScene(scene, 320, 240, "frame.png")

#    def testSeeWhatHappensWhenWeRenderScene11(self):
 #       f = libfixer.FixerLibrary()
  #      scene = "/home/mike/projects/github/scargo/scenes/scene_11.mp4"
        #f.RenderSynfigScene(scene, 320, 240, "frame.png")
        #f.CreateVideo(scene, "frame.png")
        #if.ClearFrames(scene, "frame.png")
   #     ID = "1"
    #    _in = 100
     #   _out = 200
      #  resource = "resource"
       # name = "name"

        #mediaInfo = f.GetMediaInformation( scene, ID, _in, _out, resource, name, 25)
        #res = f.CreateKdenliveProducer(mediaInfo)
        #res2 = f.CreateProducer(mediaInfo)
        #res3 = f.CreateKdenlivePlaylistEntry(mediaInfo)
        #print str(res)
        #print "====="
        #print str(res2)
        #print "====="
        #print str(res3)




    #def testSeeWhatMediaInformationWeCanDerriveForScene29(self):
        #f = libfixer.FixerLibrary()
        #scene = "/home/mike/projects/github/scargo/scenes/scene_13.mp4"
        #ID = "1"
        #_in = 100
        #_out = 200
        #resource = "resource"
        #name = "name"
        #mediaInfo = f.GetMediaInformation( scene, ID, _in, _out, resource, name, 25)
        #f.CreateKdenliveProducer(mediaInfo)
        ##print str(res)

    #def testKdenlive(self):
        #f = libfixer.FixerLibrary()
        #print"test"
        #print str(f.CalculateKdenLiveLength(133,24,25))


    def testOne(self):
        assert (True == True),"TESTS PASS"


def main():
    unittest.main()
if __name__ == '__main__':
            main()