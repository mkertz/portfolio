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


def main_exec(logger):
  
    print('KEEP THIS, useful for returning success to php')
    
    dirPathToItems = sys.argv[1]
    item = sys.argv[2] #{items[head, body...]}'} placeholder this will be activated items
    itemType = sys.argv[3]
    old_status = sys.argv[4] #Status AS STATE, STATE USED IN mark_array.py, and analyze_array.py - status status before change
    
        
    with open(dirPathToItems, 'r') as j: #replace this with directory name
        items = json.loads(j.read())
    j.close()
   
    if old_status == 'inactive':
        new_status = 'active'
    else:
        new_status = 'inactive'

    

    if itemType == 'masses':
        for i in range(200):
            try:
                items[new_status][itemType][str(item)+str(i)] = items[old_status][itemType][str(item)+str(i)]
                del(items[old_status][itemType][str(item)+str(i)])
            except:
                break
    
    else:
        items[new_status][itemType][item] = items[old_status][itemType][item] #pop() prob more efficient than del, but ran into problems, so just deleted olds
        del(items[old_status][itemType][item])
        

    

    with open(dirPathToItems, 'w') as outfile: #replace this with directory name
        json.dump(items, outfile)
    outfile.close()



    '''    
    Below is for saving info, for potential use later

    for i, mass in enumerate(masses):
        itemTypeLevel[str(item_name)+str(i)] = mass_to_dict(mass)
        itemTypeLevel[str(item_name)+str(i)]['order'] = order
        itemTypeLevel[str(item_name)+str(i)]['color'] = color
    

    for itemType in items[state]:
        if itemType == 'groups' or itemType == 'edges':
            for item in items[state][itemType]:
                if item[0] == 'y': #these were made without tranvsvers img_arr
                    logging.info('normal item is '+ item)
                    mark_groupings(img_arr, items[state][itemType][item]['values'], items[state][itemType][item]['color']) 
                else:
                    logging.info('transverse item is ' + item)
                    mark_groupings(t_img_arr, items[state][itemType][item]['values'], items[state][itemType][item]['color']) 
        elif itemType == 'masses': #or itemType == 'features': //consider axis too
            for item in items[state][itemType]:
                mark_rectangle_from_dict(img_arr, items[state][itemType][item])

   
    '''

def main():
    '''
    consider renaming error shell
    better to run outside of this code, but potential complexity with passing sys.arg between python files.
    '''
    logging.basicConfig(filename="reverseStatus.log", format='%(levelname)s:%(asctime)s %(message)s', filemode='w')
    logger = logging.getLogger()
    logging.root.setLevel(logging.NOTSET)

    try:
        main_exec(logger)
    except Exception as e:
        logging.exception('Unexpected exception! %s', e)



if __name__ == '__main__':
    main()