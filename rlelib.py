#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##############################################################################
# Name        : RLELIB
# Description : Functions to manage lossy image RLE.
# Author      : Antoni Burguera (antoni dot burguera at uib dot com)
# History     : 21-December-2023 - Creation
# Notes       : The RLE format used is a byte array structured as follows:
#               * 2 Bytes - Image width (pixels), big endian.
#               * 2 Bytes - Image height (pixels), big endian.
#               * The runs. Each run is:
#                 - 4 bytes - BBGGRRCC where BB, GG and RR are the blue, green
#                             and blue color channels, one byte each. CC is the
#                             run length minus one.
###############################################################################

###############################################################################
# IMPORTS
###############################################################################

from PIL import Image
import numpy as np
import sys

###############################################################################
# INPUT/OUTPUT
###############################################################################

#==============================================================================
# LOAD_IMAGE
# Loads an image performing some basic checks.
# Input  : fileName - Image file name
# Output : Image (ndarray)
#==============================================================================
def load_image(fileName):
    theImage=np.array(Image.open(fileName))
    theShape=theImage.shape
    if len(theShape)!=3 or not (theShape[2] in [3,4]):
        sys.exit('[ERROR] ONLY RGB IMAGES ALLOWED')
    elif theShape[2]==4:
        print('[WARNING] INPUT IMAGE IS RGBA. DISCARDING ALPHA CHANNEL')
        theImage=theImage[:,:,:3]
    elif theImage.dtype!='uint8':
        sys.exit('[ERROR] IMAGES MUST BE IN UINT8 FORMAT')
    return theImage

#==============================================================================
# SAVE_IMAGE
# Saves an image to disk.
# Input  : theImage - Image (ndarray)
#          fileName - Target file name
#==============================================================================
def save_image(theImage,fileName):
    pilImage=Image.fromarray(theImage)
    pilImage.save(fileName)

#==============================================================================
# LOAD_RLE
# Loads an RLE image from disk.
# Input  : fileName - RLE data file name
# Output : RLE data (bytearray)
#==============================================================================
def load_rle(fileName):
    with open(fileName,'rb') as inFile:
        rleImage=inFile.read()
    return rleImage

#==============================================================================
# SAVE_RLE
# Saves an RLE image to disk.
# Input  : rleImage - RLE image (bytearray)
#          fileName - Target file name
#==============================================================================
def save_rle(rleImage,fileName):
    with open(fileName,'wb') as outFile:
        outFile.write(rleImage)

###############################################################################
# CONVERSION
###############################################################################

#==============================================================================
# RGB2RLE
# Converts an image (ndarray) to an RLE image (bytearray)
# Input  : theImage - Image to convert (ndarray)
#          theThreshold - A run is considered complete when the mean squared
#                         error with respect to the original corresponding part
#                         of the image is larger or equal than this value.
#                         A value of 0 results in a lossless output.
#          strTransparent - RGB color (hex string) of the color to use as
#                         transparent. For example, "ff00ff". If the string
#                         has more than six characters, the first six are used.
#                         Use None if no transparency is desired.
# Output : RLE image (bytearray)
#==============================================================================
def rgb2rle(theImage,theThreshold,strTransparent):
    # Compute the RGB code
    wantTransparency=not (strTransparent is None)
    if wantTransparency:
        try:
            theTransparent=[int(strTransparent[i:i+2], 16) for i in (0, 2, 4)]
        except:
            sys.exit('[ERROR] %s IS NOT A VALID TRANSPARENT COLOR CODE'%strTransparent)
    # maxCount is the maximum run length
    maxCount=256
    outData=np.empty((0,4))
    nRows,nCols,_=theImage.shape
    # Iterate the image rows
    for curRow in range(nRows):
        # Init the run colors to the first in the row
        colorList=theImage[curRow,0].reshape((-1,3))
        # Iterate the image columns
        for curCol in range(1,nCols):
            # Check if current color is transparent
            isTransparent=wantTransparency and np.array_equal(theImage[curRow,curCol],theTransparent)
            # Check if all colors in list are transparent
            wasTransparent=wantTransparency and np.array_equiv(colorList,theTransparent)
            # Propose a run
            newColorList=np.vstack((colorList,theImage[curRow,curCol]))
            # If the run is still acceptable (MSE<threshold and no changes from/to transparent) consolidate it
            if (isTransparent and wasTransparent) or ((not isTransparent) and (not wasTransparent) and np.mean((newColorList-np.mean(colorList,axis=0))**2)<theThreshold):
                colorList=newColorList
            # If the run is not acceptable
            else:
                # Get the count and the color
                colorCount=colorList.shape[0]
                colorValue=np.mean(colorList,axis=0)
                # Split the run if it surpasses maxCount items
                nIters=int(np.floor(colorCount/maxCount))
                colorCount-=maxCount*nIters
                for _ in range(nIters):
                    outData=np.vstack((outData,[maxCount-1,*colorValue]))
                if colorCount!=0:
                    outData=np.vstack((outData,[colorCount-1,*colorValue]))
                # Init the new run to the current color
                colorList=theImage[curRow,curCol].reshape((-1,3))
        # After each row, process the remaining items
        colorCount=colorList.shape[0]
        colorValue=np.mean(colorList,axis=0)
        nIters=int(np.floor(colorCount/maxCount))
        colorCount-=maxCount*nIters
        for _ in range(nIters):
            outData=np.vstack((outData,[maxCount-1,*colorValue]))
        if colorCount!=0:
            outData=np.vstack((outData,[colorCount-1,*colorValue]))

    # Store the image shape in uint16 big endian format.
    rleImage=theImage.shape[1].to_bytes(2,'big')+theImage.shape[0].to_bytes(2,'big')
    # Store the data
    rleImage+=np.flip(np.round(outData).astype('uint8'),axis=1).tobytes()
    return rleImage

#==============================================================================
# RLE2RGB
# Converts an RLE image (bytearray) to an image (ndarray)
# Input  : rleImage - RLE image.
# Output : Image (nparray)
#==============================================================================
def rle2rgb(rleImage):
    # Get image size
    theWidth=int.from_bytes(rleImage[:2],'big')
    theHeight=int.from_bytes(rleImage[2:4],'big')
    # Get the run length data (the file size is ignored)
    rleData=np.flip(np.frombuffer(rleImage[4:],dtype='uint8').reshape((-1,4)),axis=1)
    # Create planar version of the image
    theImage=np.empty(theWidth*theHeight*3,dtype='uint8')
    # Loop for all the rle data
    idxStart=0
    for curItem in rleData:
        # Apply each run
        theCount=curItem[0]+1
        idxEnd=idxStart+theCount*3
        theImage[idxStart:idxEnd]=np.tile(curItem[1:],theCount)
        idxStart=idxEnd
    # Reshape the matrix
    theImage=np.reshape(theImage,(theHeight,theWidth,3))
    return theImage

#==============================================================================
# RLESHAPE
# Provides the shape of the RLE encoded image.
# Input  : rleImage - RLE image.
# Output : (H,W,3), where H is the number of rows or height, W is the number
#          of columns or width and 3 is the number of channels (always 3)
#==============================================================================
def rleshape(rleImage):
    return (int.from_bytes(rleImage[2:4],'big'),int.from_bytes(rleImage[:2],'big'),3)

###############################################################################
# VISUALIZATION
###############################################################################

#==============================================================================
# SHOW_IMAGE
# Displays an image.
# Input  : theImage - Image to show (ndarray)
#==============================================================================
def show_image(theImage):
    pilImage=Image.fromarray(theImage)
    pilImage.show()

#==============================================================================
# SHOW_RLE
# Displays an RLE image.
# Input  : rleImage - RLE image to show (bytearray)
#==============================================================================
def show_rle(rleImage):
    theImage=rle2rgb(rleImage)
    show_image(theImage)