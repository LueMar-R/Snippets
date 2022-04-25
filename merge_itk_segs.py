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
cart_femur_value=1 # Label of the femoral cartilage on the first input file
bone_femur_value=2 # Label of the femoral bone on the first input file

cart_tibia_value=1 # Label of the tibial cartilage on the second input file
bone_tibia_value=2 # Label of the tibial bone on the second input file

#********************************** run ****************************************

start = time.time()

inputFile1 = sys.argv[1] # nrrd file of femoral bone and cartilage segmentation
inputFile2 = sys.argv[2] # nrrd file of tibial bone and cartilage segmentation
output = sys.argv[3] # output file name (with extension .nrrd)


mask1 = sitk.ReadImage(inputFile1,sitk.sitkInt16)
mask2 = sitk.ReadImage(inputFile2,sitk.sitkInt16)
assert mask1.GetSpacing() == mask2.GetSpacing()
assert mask1.GetSize() == mask2.GetSize()

MaskFemurArray = sitk.GetArrayFromImage(mask1)
MaskTibiaArray = sitk.GetArrayFromImage(mask2)


FourLabelsArray = np.zeros_like(MaskFemurArray)
FourLabelsArray[MaskFemurArray==bone_femur_value]=1
FourLabelsArray[MaskTibiaArray==bone_tibia_value]=2
FourLabelsArray[MaskFemurArray==cart_femur_value]=3
FourLabelsArray[MaskTibiaArray==cart_tibia_value]=4

resultImage = sitk.GetImageFromArray(FourLabelsArray)
resultImage.CopyInformation(mask1)

sitk.WriteImage(resultImage, output)
elapsed_time_fl = (time.time() - start)
print('CPU time=',elapsed_time_fl)

