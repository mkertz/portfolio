"""
image_to_matrix.py converts an image (jpg, png, etc...) to an array
was created for speedier error proofing so the same image isn't repeatedly converted to numpy arrays
could combine with analyze_array.py for site analysis

previously used/error testing imports
import ImageDraw
import simpleimage
import os

"""
from PIL import Image
import numpy as np
from numpy import asarray
import sys
import logging

def main_exec(logger):

    #from shell_exec(shell_exec($imgToNumpy .' '. $uploadedPic.' '.$directoryPath))
    uploadedPic = sys.argv[1] #this is the pic name
    dirPath = sys.argv[2] # previously was 'ImageArray'
    
    img = Image.open(uploadedPic)
    img_arr = asarray(img) #could put error proof here (try/except) in case image can't be converted to array/is only an image by extension
    
    if len(img_arr.shape) == 2: #png file, or only one value for each pixel
        img_arr2 = []
        for i in range(len(img_arr)): #could use enumerate instead of range
            section = []
            for j in range(len(img_arr[i])):
                section.append([img_arr[i][j]]*3) #probably don't need to multiply by 3, but done so for consistency, error proofing 
            img_arr2.append(section)    
        img_arr = np.array(img_arr2)

    # this worked np.save('../uploads/TEMP_imgArr', img_arr,
    if len(img_arr.shape) == 3:
        np.save(dirPath + 'imgArr', img_arr, allow_pickle=True, fix_imports=True)#.npy extensions added, can't save using file name + path
        np.save('TEMPimgArr', img_arr, allow_pickle=True, fix_imports=True) #temporary for error proofing
        print('saved')
    else:
        print('Array has incorrect dimensions')
    

def main():
    '''
    consider renaming error shell
    better to run outside of this code, but potential complexity with passing sys.arg between python files.
    '''
    logging.basicConfig(filename="image_to_numpy.log", format='%(levelname)s:%(asctime)s %(message)s', filemode='w')
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    try:
        main_exec(logger)
    except Exception as e:
        logging.exception('Unexpected exception! %s', e)




if __name__ == '__main__':
    main()
