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
        scene = "/home/mike/projects/github/scargo/scenes/scene_20.sif"
        f.RenderSynfigScene(scene, 320, 240, "frame.png")
        f.CreateVideo(scene, "frame.png")
        f.ClearFrames(scene, "frame.png")

    def testSeeWhatHappensWhenWeRenderScene12And13(self):
        f = libfixer.FixerLibrary()
        scene = "/home/mike/projects/github/scargo/scenes/scene_12.sif"
        f.RenderSynfigScene(scene, 320, 240, "frame.png")
        f.CreateVideo(scene, "frame.png")
        f.ClearFrames(scene, "frame.png")
        scene = "/home/mike/projects/github/scargo/scenes/scene_13.sif"
        f.RenderSynfigScene(scene, 320, 240, "frame.png")
        f.CreateVideo(scene, "frame.png")
        f.ClearFrames(scene, "frame.png")

    def testJustRenderScene12frames(self):
        f = libfixer.FixerLibrary()
        scene = "/home/mike/projects/github/scargo/scenes/scene_12.sif"
        f.RenderSynfigScene(scene, 320, 240, "frame.png")






    def testOne(self):
        assert (True == True),"TESTS PASS"


def main():
    unittest.main()
if __name__ == '__main__':
            main()