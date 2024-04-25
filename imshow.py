#!/usr/bin/env python3
# -*- coding: utf-8 -*-
##############################################################################
# Name        : IMSHOW
# Description : CLI for image and RLE image visualization (RLELib)
# Author      : Antoni Burguera (antoni dot burguera at uib dot com)
# History     : 21-December-2023 - Creation
#
# usage: imshow [-h] [-s] file_name
#
# Displays an image
#
# positional arguments:
#   file_name       Image file name
#
# optional arguments:
#   -h, --help      show this help message and exit
#   -s, --standard  The image has a standard format (not RLELib format)
###############################################################################

###############################################################################
# IMPORTS
###############################################################################
from rlelib import show_image,show_rle,load_rle,load_image
import argparse
import os

###############################################################################
# ARGUMENT PARSE
###############################################################################
theParser=argparse.ArgumentParser(prog='imshow',
                                  description='Displays an image')
theParser.add_argument("file_name",help='Image file name')
theParser.add_argument("-s", "--standard", action="store_true",help='The image has a standard format (not RLELib format)')
theArguments=theParser.parse_args()
if not os.path.exists(theArguments.file_name):
    theParser.exit(1, message='The image file "%s" does not exist.\n'%theArguments.file_name)
if theArguments.standard:
    show_image(load_image(theArguments.file_name))
else:
    show_rle(load_rle(theArguments.file_name))