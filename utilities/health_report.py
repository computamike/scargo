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
import libfixer

try:
    parser = argparse.ArgumentParser(
        prog='Fixer',
        description='Jenkins / KDE Health report',
        epilog="""
        This script builds a file containing details about scene issues..""")
    parser.add_argument('-kdenlive', help='KdenLive project to update '
        '(default storyboard.kdenlive)', default='storyboard.kdenlive')

    filename = args.kdenlive

    if not os.path.exists(filename):
        raise Exception('Kdenlive Project file specified does not exist.')



except Exception as inst:
    #print type(inst)     # the exception instance
    #print inst.args      # arguments stored in .args
    print("ERROR : " + str(inst))
