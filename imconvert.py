#!/usr/bin/env python3
# -*- coding: utf-8 -*-
##############################################################################
# Name        : IMCONVERT
# Description : CLI for image <-> RLE image conversion (RLELib)
# Author      : Antoni Burguera (antoni dot burguera at uib dot com)
# History     : 21-December-2023 - Creation
###############################################################################

from rlelib import show_image,show_rle,load_rle,load_image,rle2rgb,rgb2rle,save_image,save_rle
import argparse
import os

theParser=argparse.ArgumentParser(prog='imconvert',
                                  formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                  description='Converts an image to an RLE image (RLELib) and vice versa')
theParser.add_argument("source_file_name",help='Source file name')
theParser.add_argument("target_file_name",help='Target file name')
theParser.add_argument("threshold",nargs='?',default=20,type=int,help='Maximum MSE in a run. 0 means lossless encoding. Meaningless if --rle option is used')
theParser.add_argument("-r", "--rle", action="store_true",help='Source image is RLE')
theParser.add_argument("-f", "--force", action="store_true",help='Force overwriting if target exists')
theParser.add_argument("-d", "--display", action="store_true",help='Display target image')
theParser.add_argument("-t", "--transparency", action="store",nargs='?',const='ff00ff',help='Transparency (hex string). Do not use it to avoid transparency. Do not specify value to use ff00ff')

theArguments=theParser.parse_args()

if not os.path.exists(theArguments.source_file_name):
    theParser.exit(1, message='The input file "%s" does not exist.\n'%theArguments.source_file_name)
if not theArguments.force and os.path.exists(theArguments.target_file_name):
    theParser.exit(1, message='The output file "%s" already exists. Use -f to force overwriting.\n'%theArguments.target_file_name)
if theArguments.rle:
    sourceImage=load_rle(theArguments.source_file_name)
    targetImage=rle2rgb(sourceImage)
    save_image(targetImage,theArguments.target_file_name)
    if theArguments.display:
        show_image(targetImage)
else:
    sourceImage=load_image(theArguments.source_file_name)
    targetImage=rgb2rle(sourceImage,theArguments.threshold,theArguments.transparency)
    save_rle(targetImage,theArguments.target_file_name)
    print('RLE SIZE: %d BYTES.'%len(targetImage))
    if theArguments.display:
        show_rle(targetImage)