#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Example script 
"""

from __future__ import print_function

import os
import sys
import argparse
import fnmatch
import numpy as np
import tomopy

import hspeed

def main(arg):

    parser = argparse.ArgumentParser()
    parser.add_argument("top", help="top directory where the tiff images are located: /data/")
    parser.add_argument("start", nargs='?', const=1, type=int, default=1, help="index of the first image: 10001 (default 1)")

    args = parser.parse_args()

    top = args.top
    index_start = int(args.start)

    # Total number of images to read
    nfile = len(fnmatch.filter(os.listdir(top), '*.tif'))

    # Read the raw data
    rdata = hspeed.load_raw(top, index_start)

    particle_bed_reference = hspeed.particle_bed_location(rdata[0], plot=False)
    print("Particle bed location: ", particle_bed_reference)
    
    # Cut the images to remove the particle bed
    cdata = rdata[:, 0:particle_bed_reference, :]

    # Find the image when the shutter starts to close
    dark_index = hspeed.shutter_off(rdata)
    print("Shutter CLOSED on image: ", dark_index)

    # Find the images when the laser is on
    laser_on_index = hspeed.laser_on(rdata, particle_bed_reference, alpha=1.00)
    print("Laser ON on image: ", laser_on_index)

    # Set the [start, end] index of the blocked images, flat and dark.
    flat_range = [0, 1]
    data_range = [laser_on_index, dark_index]
    dark_range = [dark_index, nfile]

    flat = cdata[flat_range[0]:flat_range[1], :, :]
    proj = cdata[data_range[0]:data_range[1], :, :]
    dark = np.zeros((dark_range[1]-dark_range[0], proj.shape[1], proj.shape[2]))  

    # if you want to use the shutter closed images as dark uncomment this:
    #dark = cdata[dark_range[0]:dark_range[1], :, :]  

    ndata = tomopy.normalize(proj, flat, dark)
    ndata = tomopy.normalize_bg(ndata, air=ndata.shape[2]/2.5)
    ndata = tomopy.minus_log(ndata)
    hspeed.slider(ndata)

    ndata = hspeed.scale_to_one(ndata)
    ndata = hspeed.sobel_stack(ndata)
    hspeed.slider(ndata)

    ndata = tomopy.normalize(proj, flat, dark)
    ndata = tomopy.normalize_bg(ndata, air=ndata.shape[2]/2.5)
    ndata = tomopy.minus_log(ndata)

    blur_radius = 3.0
    threshold = .04
    nddata = hspeed.label(ndata, blur_radius, threshold)
    hspeed.slider(ndata)


if __name__ == "__main__":
    main(sys.argv[1:])
