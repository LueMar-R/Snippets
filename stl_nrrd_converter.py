#!/usr/bin/env python
import os
import vtk
import argparse
import nrrd
import numpy as np
import vtk.util.numpy_support as vtknp
import SimpleITK as sitk

"""
STL to NRRD converter
Convert all the .stl files from a given directory to NRRD format.

usage :
python nrrd_stl_converter.py <path-to-input-dir> -o <path-to-output-dir>
"""



def vtk2sitk(vtkimg, debug=False):
    """Takes a VTK image, returns a SimpleITK image."""
    #source : https://github.com/dave3d/dicom2stl/blob/main/utils/vtk2sitk.py
    sd = vtkimg.GetPointData().GetScalars()
    npdata = vtknp.vtk_to_numpy(sd)

    dims = list(vtkimg.GetDimensions())
    origin = vtkimg.GetOrigin()
    spacing = vtkimg.GetSpacing()

    if debug:
        print("dims:", dims)
        print("origin:", origin)
        print("spacing:", spacing)

        print("numpy type:", npdata.dtype)
        print("numpy shape:", npdata.shape)

    dims.reverse()
    npdata.shape = tuple(dims)
    if debug:
        print("new shape:", npdata.shape)
    sitkimg = sitk.GetImageFromArray(npdata)
    sitkimg.SetSpacing(spacing)
    sitkimg.SetOrigin(origin)

    if vtk.vtkVersion.GetVTKMajorVersion()>=9:
        direction = vtkimg.GetDirectionMatrix()
        d = []
        for y in range(3):
            for x in range(3):
                d.append(direction.GetElement(y,x))
        sitkimg.SetDirection(d)
    return sitkimg

def convertFile(filepath, outdir):
    """STL > 
        VTKPolydata >
            VTKImageData >
            StencilledPolyData >
                StencilledImageData >
                    SimpleITKImage (through func. vtk2sitk) > 
                        NRRD"""
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    if os.path.isfile(filepath):
        basename = os.path.basename(filepath)
        print("Copying file:", basename)
        basename = os.path.splitext(basename)[0]
        outfile = os.path.join(outdir, basename+".seg.nrrd")
        reader = vtk.vtkSTLReader()
        reader.SetFileName(filepath)
        reader.Update() # read the STL file

        ## get the plolydata from the STL reader
        polydata = reader.GetOutput()

        ## get the points from the polydata, define origin, spacing and shape of the volume
        bounds_coords = polydata.GetBounds()
        lenx = bounds_coords[1] - bounds_coords[0]
        leny = bounds_coords[3] - bounds_coords[2]
        lenz = bounds_coords[5] - bounds_coords[4]
        print(f"bounds_coords: {bounds_coords}")
        origin_coords = polydata.GetCenter()
        origin_coords = [origin_coords[0]-lenx/2, origin_coords[1]-leny/2, origin_coords[2]-lenz/2]
        print(f"origin_coords: {origin_coords}")
        points_nbr = polydata.GetNumberOfPoints()
        print(f"points: {points_nbr}")

        ## create a vtkImageData from the vtkPolydata
        imagedata = vtk.vtkImageData()
        imagedata.SetOrigin(origin_coords)
        imagedata.SetSpacing(1, 1, 1)
        imagedata.SetDimensions(int(lenx), int(leny), int(lenz))
        imagedata.AllocateScalars(vtk.VTK_UNSIGNED_CHAR, 1)
        imagedata.SetExtent(0, int(lenx)-1, 0, int(leny)-1, 0, int(lenz)-1)

        ## get the binary
        if basename.lower().endswith('femur'):
            maskval = 1
        elif basename.lower().endswith('tibia'):
            maskval = 2
        elif basename.lower().endswith('patella'):
            maskval = 3
        elif basename.lower().endswith('fibula'):
            maskval = 4
        else:
            raise Exception(f"Unknown bone in file: {basename}")
        bkgval = 0

        for i in range(imagedata.GetNumberOfPoints()):
            imagedata.GetPointData().GetScalars().SetTuple1(i, maskval)

        # get the stencil
        pol2stenc = vtk.vtkPolyDataToImageStencil()
        pol2stenc.SetInputData(polydata)
        pol2stenc.SetOutputOrigin(origin_coords)
        pol2stenc.SetOutputSpacing(1, 1, 1)
        pol2stenc.SetOutputWholeExtent(imagedata.GetExtent())
        pol2stenc.Update()

        imgstenc = vtk.vtkImageStencil()
        imgstenc.SetInputData(imagedata)
        imgstenc.SetStencilConnection(pol2stenc.GetOutputPort())
        imgstenc.ReverseStencilOff()
        imgstenc.SetBackgroundValue(bkgval)
        imgstenc.Update()

        # convert the VTKStencil to SimpleITK Image Formal
        sitkimage = vtk2sitk(imgstenc.GetOutput())
        # write the nrrd from the SimpleITK Image
        sitk.WriteImage(sitkimage, outfile)

        return 1

    return False

def convertFiles(indir, outdir):
    files = os.listdir(indir)
    files = [ os.path.join(indir,f) for f in files if f.endswith('.stl') ]
    ret = 0
    print("In:", indir)
    print("Out:", outdir)
    for f in files:
        ret += convertFile(f, outdir)
    print(f"Successfully converted {ret} out of {len(files)} files.")

def run(args):
    convertFiles(args.indir, args.outdir)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="STL to NRRD converter")
    parser.add_argument('indir', help="Path to input directory.")
    parser.add_argument('--outdir', '-o', default='output', help="Path to output directory.")
    parser.set_defaults(func=run)
    args = parser.parse_args()
    ret = args.func(args)

