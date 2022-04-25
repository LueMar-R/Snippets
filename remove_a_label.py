import numpy as np
import SimpleITK as sitk
import sys
import time

"""
use:
python3 merge_itk_segs.py inputFile1.seg.nrrd inputFile2.seg.nrrd output.seg.nrrd

--------------------------------------------------------------------------------

inputFile1 : Femoral bone and cartilage segmentation
inputFile2 : Tibial bone and cartilage segmentation
output : merged segmentation relabeled with
    1 : Femoral bone
    2 : Tibial bone
    3 : Femoral cartilage
    4 : Tibial cartilage

Set the initial values of the labels of inputFile1 and inputFile2 to the 
corresponding values if diferent from 1 (cartilage) and 2 (bone).

"""

# set the value of the labels in the input files

values_to_exclude = [5, 6, 7]

#********************************** run ****************************************

start = time.time()

inputFile1 = sys.argv[1] # nrrd file 
output = sys.argv[2] # output file name (with extension .nrrd)


mask1 = sitk.ReadImage(inputFile1,sitk.sitkInt16)

MaskArray = sitk.GetArrayFromImage(mask1)

for value in values_to_exclude:
    MaskArray[MaskArray==value]=0


resultImage = sitk.GetImageFromArray(MaskArray)
resultImage.CopyInformation(mask1)

sitk.WriteImage(resultImage, output)
elapsed_time_fl = (time.time() - start)
print('CPU time=',elapsed_time_fl)

