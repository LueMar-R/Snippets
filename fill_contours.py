import numpy as np
import SimpleITK as sitk
import os
import sys
import matplotlib.pyplot as plt
from scipy.ndimage import binary_fill_holes
import time
start = time.time()
#import pandas as pd
#from scipy.interpolate import RegularGridInterpolator 
#import GetNeighbors
inputDir1 = sys.argv[1] #'input file'
inputDir2 = sys.argv[2] #'input folder'
output = sys.argv[3] #'output'
label = sitk.ReadImage(inputDir1,sitk.sitkInt16)
print(label.GetSpacing())
labelArray = sitk.GetArrayFromImage(label)
# label_value=2
cart_value=2
bone_value=1
# labelArray[labelArray!=label_value]=0;
# labelArray=np.zeros((labelArray0.shape[2], labelArray0.shape[0], labelArray0.shape[1]))
# for i in range(labelArray0.shape[0]):
#    labelArray[:,i,:]=labelArray0[i,:,:]
labelArrayCart = np.zeros_like(labelArray)
labelArrayCart[labelArray==cart_value]=1
labelArrayBone = np.zeros_like(labelArray)
labelArrayBone[labelArray==bone_value]=1
#***************** Apply interpolated points on label map*************************  
folders = [f for f in os.listdir(inputDir2) if f.endswith('.txt')]
for file_name in folders:
    f_name=inputDir2+'/'+file_name
    with open(f_name, "r") as filestream:
        for line in filestream:
            currentline = line.split(",")
            #inter_points.append([int(currentline[0]), int(currentline[1]), int(currentline[2])])        
            labelArrayBone[int(currentline[1]), int(currentline[0]), int(currentline[2])]=int(bone_value)
#*********************************** Output interpolated labelmap*************************************
for j in range(1,labelArrayBone.shape[0]):
        mat=labelArrayBone[j,:,:]
        labelArrayBone[j,:,:]=filled = binary_fill_holes(mat).astype(int)
labelArray = labelArrayBone*2+labelArrayCart
resultImage = sitk.GetImageFromArray(labelArray)
resultImage.CopyInformation(label)
print(resultImage.GetSpacing())
#l_name=output+'/label_reconstructed_'+label_value+'.nii.gz'
sitk.WriteImage(resultImage, output)
elapsed_time_fl = (time.time() - start)
print('CPU time=',elapsed_time_fl)
