#!/usr/bin/env python
import os
import vtk
import argparse

def convertFile(filepath, outdir):
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    if os.path.isfile(filepath):
        basename = os.path.basename(filepath)
        print("Copying file:", basename)
        basename = os.path.splitext(basename)[0]
        outfile = os.path.join(outdir, basename+".stl")
        reader = vtk.vtkNrrdReader()
        reader.SetFileName(filepath)
        reader.Update()

        ## vtk image_data to vtk polydata with vtk marching cubes
        marchingCubes = vtk.vtkMarchingCubes()
        marchingCubes.SetInputConnection(reader.GetOutputPort())
        marchingCubes.SetValue(0, 0.5)
        marchingCubes.Update()

        ## vtk polydata to vtk stl
        stlWriter = vtk.vtkSTLWriter()
        stlWriter.SetFileName(outfile)
        stlWriter.SetInputConnection(marchingCubes.GetOutputPort())
        return stlWriter.Write() == 1

    return False

def convertFiles(indir, outdir):
    files = os.listdir(indir)
    files = [ os.path.join(indir,f) for f in files if f.endswith('.nrrd') ]
    ret = 0
    print("In:", indir)
    print("Out:", outdir)
    for f in files:
        ret += convertFile(f, outdir)
    print("Successfully converted %d out of %d files." % (ret, len(files)))

def run(args):
    convertFiles(args.indir, args.outdir)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="NRRD to STL converter")
    parser.add_argument('indir', help="Path to input directory.")
    parser.add_argument('--outdir', '-o', default='output', help="Path to output directory.")
    parser.set_defaults(func=run)
    args = parser.parse_args()
    ret = args.func(args)


##
# Path: Dash_test/nrrd_slt_converter.py
# python Dash_test/nrrd_stl_converter.py -h
# python Dash_test/nrrd_stl_converter.py <path-to-input-dir> -o <path-to-output-dir>
# python /home/lmaintier/Documents/Projets/PCO/Dash_test/nrrd_slt_converter.py /home/lmaintier/Desktop/test_out/output -o /home/lmaintier/Desktop/test_out/output