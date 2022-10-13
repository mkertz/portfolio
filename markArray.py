from tkinter import TRUE
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
from numpy.core.arrayprint import array_repr
from numpy.ma.extras import average
import math
import pickle
import copy
import sys
import pandas as pd
import requests 
from PIL import Image, ImageDraw
import logging
import json

'''
TO INCLUDE:
    plt.axline, stem axis variables etc...

pass pickled files, or dictionary files themsleves through python
use entered file for list as json vs pickle?

program designed to take numpy array and dictionary and display image based on parameters chosen

dictionary in form of items pickled file

items['feature'['location/bounds']]
items['feature'['color']] has corresponding color
consider including color in activated_items
for example:
    items['head'['superior_bounds']] gives the y value of the superior portion of the prosthesis head

activated_items = items_status['activated']
activated_items = dictionary of activated items


consider using classes for this


    activated_items is a dictionary of lists of activated items
        activated_items = {'items':['head', 'body', 'shell',... ], 'edges':['brightness_based', 'difference_based'...]
        has lists of feature types
        color is list [R,G,B] for color to appear on xray
        eg. activated_items= { feature: [head, body, ...], edges: [brightness_based, subtraction, matrix], axes
    
    items is a dictionary with lateral, medial, superior, and inferior bounds corresponding to img_arr,
        items includes
            head -boundaries (rad/dia/bound?) 
            prosthesis - boundaries
                masses
                borders
            extraction cannula -boundaries
            lower tip -point
        axes includes
            stem axis
            nect axis
        points include
            edges
                

    check out [y][w_min], make sure these correspond with dictionary values



'''



def mark_rectangle_from_dict(img_arr, feature): 
    '''
    see mark_rectangle_from_mass for original code

    '''
    for y in range(feature['y_superior'], feature['y_inferior']+1): #ends on inferior bounds, need +1 to cover inferior bounds
        img_arr[y][feature['x_medial']] = img_arr[y][feature['x_lateral']] = feature['color']
    for x in range(feature['x_medial'], feature['x_lateral']+1):
        img_arr[feature['y_superior']][x] = img_arr[feature['y_inferior']][x] = feature['color']
    return img_arr


def mark_points(img_arr, groups, color = [0, 255, 0], buffer = 2):##
    '''
    groups in form of [[y, x, angle],[y2, x2, angle 2],...]
    '''
    for group in groups:
        img_arr = mark_point(img_arr, group, color)

    return img_arr

def mark_point(img_arr, group, color = [0, 255, 0], buffer = 2): 
    '''
    point cannot be near border of img_arr, as area around is highlighted

    group is [y, x, angle]
    '''   
    [y_center, x_center, angle] = group

    y_min = y_center - buffer
    y_max = y_center + buffer
    x_min = x_center - buffer
    x_max = x_center + buffer

    for y in range(y_min, y_max+1):
        img_arr[y][x_min] = img_arr[y][x_max] = color
    for x in range(x_min, x_max+1):
        img_arr[y_min][x] = img_arr[y_max][x] = color

    return img_arr



def mark_groupings(img_arr, group, color = [255,0,0]):
    """
    mark_groupings is edges and groups
    color is yellow for groupings

    group has coordinates [y,[x_start, x_end], [x_start,x_end]],[y,[x_start...]]
    """
    excluded_length = 2
    for i in range(1,len(group)):
        y = group[i][0]
        for j in range(1, len(group[i])):
            try: 
                x_start = group[i][j][0]
                logging.info('group[i] ', group[i])
            except:
                logging.info('group[i] ', group[i])
            try: 
                x_end = group[i][j][1]
                logging.info('group[i] ', group[i])
            except:
                logging.info('group[i] ', group[i])
            if x_end - x_start > excluded_length:
                img_arr[y][x_start] = color
                img_arr[y][x_end] = color


def create_new_image(img_arr, dirPath, title):
    img = Image.fromarray(img_arr)
    img.save(str(dirPath)+str(title))



def main_exec(logger):
  
    print('KEEP THIS, NEEDED minimum needed for returning success to php')
    
    dirPath = sys.argv[1]
    ItemsFileName = sys.argv[2] #{items[head, body...]}'} placeholder this will be activated items
    multipleImages = sys.argv[3]
    #img_arr_original = np.load(sys.argv[3]) 
    #activated_items = sys.argv[4] #sys.argv[4] should be 'Image.jpeg' -open in file destination
    #activated_items={}
    
    '''
    with open('items.json', 'r') as j: #replace this with directory name
        items = json.loads(j.read())
    '''

    #y_groups_diff = items[state][itemType][item][item_category] 

    #DELETE THIS activated_items['masses'] = ['y_masses_by_mass_diff0']
 
    img_arr_original = np.load(dirPath+'imgArr.npy')
    img_arr = copy.deepcopy(img_arr_original)
    t_img_arr = np.rot90(img_arr, 1)
    
       
    with open(dirPath + 'items.json', "r") as k: #could make link to items.json if needed
        items = json.loads(k.read())

    state = 'active'

    
    #could rename img_arr if problems, to working_img_arr
    
    
    for itemType in items[state]:
        if itemType == 'groups' or itemType == 'edges':
            for item in items[state][itemType]:
                if itemType == 'groups': #may need to assign in analyze array, if want to divide into inverse groups, etc...
                    items[state][itemType][item]['color'] = [255,255,0]
                else:
                    items[state][itemType][item]['color'] = [255,0,0]
                if item[0] == 'y': #these were made without tranvsvers img_arr
                    logging.info('normal item is '+ item)
                    mark_groupings(img_arr, items[state][itemType][item]['values'], items[state][itemType][item]['color']) 
                else:
                    logging.info('transverse item is ' + item)
                    mark_groupings(t_img_arr, items[state][itemType][item]['values'], items[state][itemType][item]['color']) 
        elif itemType == 'masses': #or itemType == 'features': //consider axis too
            for item in items[state][itemType]:
                mark_rectangle_from_dict(img_arr, items[state][itemType][item])

   
    
    #mark_groupings(img_arr, y_groups_diff['values'], y_groups_diff['color'])
    
    img = Image.fromarray(img_arr)

    title = str(dirPath)+'postImage.jpeg'
    img.save(title)

  

    k.close()
    #file_name = 'uploadedPic'   




def main():
    '''
    consider renaming error shell
    better to run outside of this code, but potential complexity with passing sys.arg between python files.
    '''
    logging.basicConfig(filename="mark_array_py.log", format='%(levelname)s:%(asctime)s %(message)s', filemode='w')
    logger = logging.getLogger()
    logging.root.setLevel(logging.NOTSET)

    try:
        main_exec(logger)
    except Exception as e:
        logging.exception('Unexpected exception! %s', e)



if __name__ == '__main__':
    main()