'''
File: analyze_array.py, (originally known as detect_implant.py)
program has two purposes that do not run togethers:
   1. to create data sets associated with implant
   2. to evaluate an image of the implant and match the implant to the created data set
these both rely on the same array analysis, one creates the database from the arrays, the other matches it to previously created arrays


previously used/error testing imports
import tkinter
from tkinter import Y
import os
import pandas
import time
import pickle
import simpleimage #previously from simpleimage import SimpleImage


'''

from PIL import Image, ImageDraw
from numpy.ma.extras import average
from pylab import * #be specific?
import numpy as np
from numpy import asarray, int0, single, zeros
import operator
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import math
import sys
import json
import logging

def check_if_grey_scale(img_arr):
    '''
    error proofing
    checks if img_arr is grey_scale
    '''
    for y, row in enumerate(img_arr):
        for x, colors in enumerate(row):
            if colors[0] != colors[1] or colors[0] != colors[2]:
                return False
    return True

def convert_to_grey_scale(img_arr):
    '''
    used in the event that a phone with colors takes pictures of x rays
    '''
    for y, row in enumerate(img_arr):
        for x, colors in enumerate(row):
            avg = (int( colors[0]) + int(colors[1]) + int(colors[2])) // 3
            colors[0] = colors[1] = colors[2] = avg

    return img_arr

def compact_array(img_arr):
    '''
    program to reduce 3D image array to 2D array for quicker, easier analysis
    compact_img_arr is in form of [[y1x1,y1x2,y1x3],[y1x1,y1x2,y1x3]] 
    where y is the value of the row
    '''
    compact_img_arr = []
    for row in img_arr:
        compact_row = []
        for pixel in row:
            compact_row.append(pixel[0])
        compact_img_arr.append(compact_row)
    return compact_img_arr

def get_edges(img_arr, number_of_diffs = 10, jump_fraction = 0 ):
    '''
    program to get largest changes (presumably includes prosthesis edges) per area 

    img_gar is the image array
    number_of_diffs is the number of edges (number of differences) in intensity between pixels jump distances away stored within every row
        these are the largest differences in intensity - using absolute values
    jump_fraction is the fraction of the length

    edge_groups stired as lowest difference to the highest difference, see below
        [[y0,[ [diff 1, x1] ,[diff 2, x2] ,[diff 3, x3],... [diff n, xn]][y1...]] (most typical)
        NOTE: the x value will sometimes be the higher and the lower value, will affect imaging if used directly
            for imaging consider altering x to x = (2x +jump)//2 

    for groupings - if want to do y grouping return
        for axis 0 = y --> [[y,[x_start, x_end],[x_start, x_end]] (most typical)

    NOTE:could create redundancies with get y groupings - may want to return a y groupings function.

    '''
    

    width = len(img_arr[0])
    jump = int(jump_fraction*width) + 1
    
    #line groups are groups around the largest differences in radiolucency
    edge_groups = []

    for y, row in enumerate(img_arr):
        edge_groups.append([y])
        diffs_coords = []
        #populate the initial differences
        #consider writing a program that organizes by distance and by intensity
        for x in range(width-jump):
            diff = int(row[x+jump][0]) - int(row[x][0]) #difference in value between two pixels
            diffs_coords.append([diff, x]) #[diff0, x0]...[diff n, x n]
        diffs_coords = sorted(diffs_coords, key = lambda x:abs(x[0])) 
        diffs_coords = diffs_coords[width - number_of_diffs: width]
        diffs_coords = sorted(diffs_coords, key = lambda x:x[1]) #low number of differences mean copying prior to previous sorted takes longer
        edge_groups[y].append(diffs_coords)

    
    return edge_groups, jump


def get_edges2(img_arr, number_of_diffs = 10, jump_fraction = 0 ):
    '''
    program designed to be more efficient than get_edges, but not much of a difference and less clear/ more room for error
    program to get largest changes (presumably includes prosthesis edges) per area 

    img_arr is the image array
    number_of_diffs is the number of edges (number of differences) in intensity between pixels jump distances away stored within every row
        these are the largest differences in intensity - using absolute values
    jump_fraction is the fraction of the length

    edge_groups stired as lowest difference to the highest difference, see below
        [[y0,[ [diff 1, x1] ,[diff 2, x2] ,[diff 3, x3],... [diff n, xn]][y1...]] (most typical)
        NOTE: the x value will sometimes be the higher and the lower value, will affect imaging if used directly
            for imaging consider altering x to x = (2x +jump)//2 

    for groupings - if want to do y grouping return
        for axis 0 = y --> [[y,[x_start, x_end],[x_start, x_end]] (most typical)

    NOTE:could create redundancies with get y groupings - may want to return a y groupings function.

    '''

    width = len(img_arr[0])
    
    #line groups are groups around the largest differences in radiolucency
    edge_groups = []
 
    #jump is distance between two pixels that are evaluated, in which the difference between pixels is found
    jump = int(width * jump_fraction) 
    if jump == 0:
        jump = 1 
    adjusted_width= width - jump #variables created for clarity


    #using y and x instead of h and w, y is axis 0, x is axis 1
    #could consider actively sorting for lines to reduce time to run program
    #or could reprocess the data later

    jump_counter = 0 #jump counter tracks spaces between diffs, to avoid counting diff multiple times

    delete_thin_lines = False #deletes lines that are thin unlikely to be part of prosthesis

    for y, row in enumerate(img_arr):
        edge_groups.append([y])

        diffs_coords = []
        #populate the initial differences
        #consider writing a program that organizes by distance and by intensity
        for x in range(number_of_diffs):
            diff = int(row[x+jump][0]) - int(row[x][0])
            diffs_coords.append([diff, x]) #[diff0, x0]...[diff n, x n]
        for x in range(number_of_diffs, adjusted_width):
            diff = int(row[x+jump][0]) - int(row[x][0]) #diff indicates direction of change, negative nums means dimmer on left
            abs_diff = abs(diff) #reduces calling absolute function
            lowest_diff_value = int(diffs_coords[0][0]) #variable for clarity
            abs_lowest_diff_value = abs(lowest_diff_value)
            if abs_diff > abs_lowest_diff_value: #this is greater than the lowest difference
                insert_values = [diff, x]
                if jump_counter > 0: #jump counter means there is a local difference and one difference will be cancelled out
                    for diff_coord_index in range(number_of_diffs): #ASSUMPTION: there's a low number of diffs, or else a search should be used
                        prev_x_value = diffs_coords[diff_coord_index][1] #variable created for clarity
                        if x - prev_x_value < jump_counter: 
                            abs_prev_diff_value = abs(diffs_coords[diff_coord_index][0]) #variable created for clarity
                            if abs_diff > abs_prev_diff_value:
                                diffs_coords[diff_coord_index] = insert_values  #insert values in place of close by x
                            #if delete_thin_lines == True and prev_diff_value/abs(prev_diff_value) != diff/abs(diff) and x>0:
                            #    diffs_coords[0] = [-1,-1] #put in a replacement number that replaces the thin line
                else: 
                    del(diffs_coords[0]) #delete lowest value, not in area of previous edge
                    if abs_diff >= abs(diffs_coords[-1][0]): #should be better way than this and below
                        diffs_coords.append(insert_values)
                    else: 
                        for diff_coord_index in range( number_of_diffs - 1): #insert new values in order, ASSUME: number of diffs small, search not needed
                            abs_prev_diff_value = abs(diffs_coords[diff_coord_index][0]) #variable created for clarity
                            if abs_diff < abs_prev_diff_value: #compare to previous difference
                                diffs_coords.insert(diff_coord_index, insert_values)
                                break
                jump_counter = jump  #make sure not jump -1, reset if two successive diffs in same area?
            jump_counter -= 1
        diffs_coords = sorted(diffs_coords, key = lambda x:x[1]) 

        edge_groups[y].append(diffs_coords)
    

    return edge_groups, jump




def edges_around_extremes(edges, extremes):
    '''
    converts edges to groups surrounding the value within extreme (usually brightest or dimmest)

    extremes[[y,x, bright_value],[y2, x2, bright_value]]
    edge_groups stired as lowest difference to the highest difference, see below
        [[y0,[ [diff 1, x1] ,[diff 2, x2] ,[diff 3, x3],... [diff n, xn]][y1...]] (most typical)
    
    returns grouping in form of [[y,[x_start, x_end]],[y2 , [x_start, x_end]]...]

    '''
    

    groupings = []
    for i, group in enumerate(edges):
        y = group[0]
        x_extreme = extremes[y][1] #use instead of y, as brightest per row is all rows, i may not be all rows

        for j, pairing in enumerate(group[1]):
            x = pairing[1]

            if x > x_extreme and j > 0: #ensure brightest point between two differences
                x_start = group[1][j-1][1]
                x_end = x
                groupings.append( [y,[x_start, x_end]])
                break 

    return groupings



def edges_within_brightest(img_arr, groups, coords, number_of_diffs = 6, jump_fraction = 0, axis = 'x'):
    '''
    finds edges within the brightest segments

    could combine with edges program - much of same basis

    img_arr is the image array
    groups is in form of [[y[x start, x end, massID]],[y, [x start, x end]] - massID not always present

    edge_groups stired as lowest difference to the highest difference, see below
        [[y0,[ [diff 1, x1] ,[diff 2, x2] ,[diff 3, x3],... [diff n, xn]][y1...]] (most typical)

    darkest_per_row is [[y,x, dark_value],[y2, x2, dark_value]]
    '''

    jump = int(jump_fraction*len(groups)) + 1 #generally works best if jump = 1
    edge_groups = []
    
    if axis == 'x':
        lower_bounds = coords['y_medial']
        upper_bounds = coords['y_inferior']
    else:
        lower_bounds = coords['x_medial']
        upper_bounds = coords['x_lateral']

    start=0
    for group in groups:
        y = group[0]
        if y < lower_bounds:
            start += 1
        else:
            break

    end = 0
    for group in reversed(groups):
        y = group[0]
        if y > upper_bounds:
            end += 1
        else:
            break
    
    if end == 0: #give valid endpoint for return group
        end = -len(groups)

    groups = groups[start:-end]

    for group in groups:
        y = group[0]
        x_start = group[1][0]
        x_end = group[1][1]
        width = x_end - x_start
        edge_group = [y]
        diffs_coords = []
        #populate the initial differences
        #consider writing a program that organizes by distance and by intensity
        for x in range(x_start, x_end-1):
            diff = int(img_arr[y][x+1][0]) - int(img_arr[y][x][0])
            diffs_coords.append([diff, x]) #[diff0, x0]...[diff n, x n]
        diffs_coords = sorted(diffs_coords, key = lambda x:abs(x[0])) #could do reverse sort for less math
        diffs_coords = diffs_coords[width - number_of_diffs: width]
        diffs_coords = sorted(diffs_coords, key = lambda x:x[1])
        edge_group.append(diffs_coords)
        edge_groups.append(edge_group)

    #darkest_per_row = get_darkest_per_row(img_arr, groups) #could consider combinining with get_inverse_edges and altering return
    
    return edge_groups # darkest_per_row

def get_darkest_segments(img_arr, edge_groups): #incomplete
    '''
    selects the dark edge groups based on diffs (between negative and positive diffs)
    gets the average brightness of the edge groups within the diffs
    selects the lowest brightness

    edge_groups is [[y0,[ [diff 1, x1] ,[diff 2, x2] ,[diff 3, x3],... [diff n, xn]][y1...]] (most typical)

    darkest_segments returns as [[y [x start, x end]][y [x start, x end]]]
    '''
    darkest_segments = []
    for group in edge_groups:
        y = group[0]
        diff_group = group[1]
        seg_start = -2
        avg_dimness = 255
        dim_segment_present = False
        for group in diff_group:
            diff = group[0] 
            x = group[1]
            if diff < 0: #filters for negative groups, diffs are negative from positive to negative values
                seg_start = x
            elif seg_start > -1:
                seg_end = x
                temp_dimness = np.average(img_arr[y][seg_start+1:seg_end+1]) #seg_ends are on the first value of greatest change
                if temp_dimness < avg_dimness:
                    avg_dimness = temp_dimness
                dim_segment_present = True
        if dim_segment_present == True:
            darkest_segments.append([y, [seg_start, seg_end]])

    return darkest_segments

def convert_edge_format_to_group_format(edge):##1
    edge_group = []
    for i in range(0,len(edge)):
        y = edge[i][0]
        edge_sub_group = [y]
        for j in range(0, len(edge[i][1])):
            x_start = edge[i][1][j][0]
            x_end = edge[i][1][j][1]
            edge_sub_group.append([x_start, x_end])
        edge_group.append(edge_sub_group)
    return edge_group


def get_darkest_segments_simplified(img_arr, edge_groups):#incomplete
    '''
    selects the dark edge groups based on diffs (between negative and positive diffs)
    gets the average brightness of the edge groups within the diffs
    selects the lowest brightness

    edge_groups is [[y0,[ [diff 1, x1] ,[diff 2, x2] ,[diff 3, x3],... [diff n, xn]][y1...]] (most typical)

    darkest_segments returns as [[y [x start, x end]][y [x start, x end]]]
    '''
    darkest_segments = []
    for group in edge_groups:
        y = group[0]
        diff_groups = group[1]
        seg_start = -2
        avg_dimness = 255
        x_start = diff_groups[0][1]
        for i in range(1, len(diff_groups)): #goes through [diff, x] groups, diff group = [[diff, x],[diff, x]]
            x_end = diff_groups[i][1]
            temp_dimness = np.average(img_arr[y][seg_start+1:seg_end+1]) #seg_ends are on the first value of greatest change
            if temp_dimness < avg_dimness:
                avg_dimness = temp_dimness
                seg_start = x_start
                seg_end = x_end
                darkest_segments.append([y, [seg_start, seg_end]])
    return darkest_segments

def get_inverse_edges(dark_edge_groups, darkest_per_row):#incomplete, not functioning well - get's barrors
    '''
    program to find edges around the darkest groups

    could consolidate with get brightest per row, but would take more edditing
    
    dark_edge_groups is [[y0,[ [diff 1, x1] ,[diff 2, x2] ,[diff 3, x3],... [diff n, xn]][y1...]] 
    darkest_per_row is [[y,x, dark_value],[y2, x2, dark_value]]

    returns [[y,[x_start, x_end]],[y2 , [x_start, x_end]]...], where start and end are around the darkest x value

    '''
    #print(darkest_per_row[0:5])
    inverse_edges = []
    for i, row in enumerate(darkest_per_row):
        y = row[0]
        x_dark = row[1]
        x_groups = dark_edge_groups[i][1]
        
        for j, group in enumerate(x_groups):
            x = group[1]
            if x > x_dark:
                x_start = x_groups[j-1][1]
                x_end = x
                inverse_edges.append([y,[x_start, x_end]])
                break
    
    return inverse_edges
                




def add_avg_brightness(img_arr, groups):
    '''
    get the avg brightness of segments withing each group

    returns group in form of [[y,[x_start, x_end]],[y2 , [x_start, x_end]]...]
    '''
    for i, group in enumerate(groups): #changed y to i - was for y, group in enum...
        y = group[0]
        x_start = group[1][0]
        x_end = group[1][1]
        avg = int(np.average(img_arr[y][x_start:x_end]))
        group.append(avg) 

    return groups


def delete_dim_sort(groups, dim_fraction = .3):
    '''
    function deletes dimmest sections

    groups = [y,[x start, x end],brightness]

    probably quicker to create seperate list for deletions, a list of pointers, so sort isn't used twice.

    TODO: do quicker way than sort (keep seperate list of n sections, delete from this)
    '''

    length = len(groups)
    deleted_fract = int(length*dim_fraction) #consider doing an alternative statistical approach
    groups_dim_to_bright = sorted(groups, key = lambda x:x[2])# order least to most bright
    groups_dim_to_bright = groups_dim_to_bright[deleted_fract:length] #delete least bright groups
    groups_dim_to_bright = sorted(groups_dim_to_bright, key = lambda x:x[0]) #rearrange by y values, low to high

    return groups_dim_to_bright

def delete_dim(groups, dim_fraction = .3):
    '''
    function deletes dimmest sections
    probably isn't much quicker than using python's sort so will not use it

    TODO: do quicker way than sort (keep seperate list of n sections, delete from this)
    '''

    length = len(groups)
    deleted_fract = int(length*dim_fraction)

    #groups_dim_to_bright = sorted(groups, key = lambda x:x[2]) #probably quicker to create seperate list for deletions
    deleted_group = []
    for i in range(deleted_fract):
        deleted_group.append(groups[i]) 

    
    for i in range(deleted_fract, length):
        groups_dim_to_bright = groups_dim_to_bright[deleted_fract:length]
    groups_dim_to_bright = sorted(groups_dim_to_bright, key = lambda x:x[0]) #would be quicker to delete y values from y groups del(group[y])
    
    return groups_dim_to_bright

def edges_to_y_groups(edges,jump):
    '''
    edges in form of  [[y0,[ [diff 1, x1] ,[diff 2, x2] ,[diff 3, x3],... [diff n, xn]][y1...]] 
    -edges are arranged in order of x values
    brightest_per_row [[y,x, bright_value],[y2, x2, bright_value]]
    
    returns grouping in form of [[y,[x_start, x_end]],[y2 , [x_start, x_end]]...]
    '''
    '''
    groupings = []
    for i, group in enumerate(edges):
        y = group[0]
        for j, pairing in enumerate(group[1]):
            x = pairing[1]

            if x > x_brightest and j > 0: #ensure brightest point between two differences
                x_start = group[1][j-1][1]
                x_end = x
                groupings.append( [y,[x_start, x_end]])
                break 

    return groupings
    '''

def edges_to_sided_groupings(edge_groups, jump):
    '''
    edges not included if within a single side (two left edges in a row)

    edge_groups in form of  [[y0,[ [diff 1, x1] ,[diff 2, x2] ,[diff 3, x3],... [diff n, xn]][y1...]] 
    returns grouping in form of [[y,[x_start, x_end],[x_start, x_end]]

    '''
    #edge_groups = edge_groups[615:620]
    left_right = False

    groupings = []
    for i, group in enumerate(edge_groups):
        y = group[0]
        segment = [y]
        x_start = -1 #this is the starting location of the  segment
        x_end = -1
        left_edge_present = False
        diff_start = 0
        diff_end = 0

        for j, pairing in enumerate(group[1]):
            diff = pairing[0] #the difference between two points
            x = pairing[1]
            
            if diff > 0: #a left edge detected
                x_start = x #go for widest margin (not x + jump for left hand margin)
                if left_edge_present == False:    #diff/diff start relations go both ways, previous right edge
                    segment.append([x_start])
                    diff_start = diff #used for increase comparison
                    left_edge_present = True #current left edge
                elif diff > diff_start: # left_edge_present == True and diff > diff_start - segment is replaced
                    segment[-1][0] = x_start
                    diff_start = diff #used for increase comparison #repeat line
            else: #diff < 0
                x_end = x + jump #for wide margins
                if left_edge_present == True:
                    segment[-1].append(x_end)
                    left_edge_present = False
                elif diff < diff_end and len(segment) > 1: #left_edge_present = False, here there will be a replacement end
                        segment[-1][1] = x_end
                        diff_end = diff
        groupings.append(segment)

    return groupings

            

def winnow_groupings(groupings):   
    for i in reversed(range(len(groupings))):
        for j in reversed(range(1, len(groupings[i]))):
            if len(groupings[i][j]) < 2:
                del(groupings[i][j])
        if len(groupings[i]) < 3:
            del(groupings[i])
    
    return groupings

def get_brightest_per_row(img_arr):
    '''
    returns brightest value per row, along with y value and x value
    brightest_per_row in form of [[y,x, bright_value],[y2, x2, bright_value]]

    consider brightest per segment return for greater efficiency and function that better aligns segments (due to aberrant brightness)
    '''
    brightest_per_row = []
    for y, row in enumerate(img_arr):
        brightest_per_row.append([y])
        x = np.argmax(row)//3 #is there a function combining this with np.max? //3 because flattened array
        brightest_per_row[y].append(x)
        brightest = row[x][0]
        brightest_per_row[y].append(brightest)
    
    return brightest_per_row

def get_darkest_per_row(img_arr, groups): 
    '''
    finds the darkest value per row within the prosthesis, and the location

    darkest_per_row is [[y,x, dark_value],[y2, x2, dark_value]]

    doesn't work well, do lowest average between edges (+diff, then -diff) 
    '''
    
    darkest_segment = []
    for group in groups:
        y = group[0]
        x_start = group[1][0]
        x_end = group[1][1]
        t = np.argmin(img_arr[y][x_start:x_end])//3
        try:
            x = np.argmin(img_arr[y][x_start+2:x_end-1])//3 #is there a function combining this with np.max? //3 because flattened array
            print(x, t)
        except:
            pass
        
        darkest = img_arr[y][x][0]
        darkest_segment.append([y, x, darkest])
  
    #print(darkest_segment[35:45])
    return darkest_segment



def isolate_bright_groupings(groupings, brightest_per_row):
    '''
    groupings in form of [[y,[x_start, x_end],[x_start, x_end]][y,[x_start, x_end]]]
    brightest_per_row in form of [[y,x,brightness][y2,x2,brightness2]]
    '''
    bright_groups = []
    for i, group in enumerate(groupings):
        y = group[0]
        for j in range(1, len(group)):
            x_start = group[j][0]
            x_end = group[j][1]
            x_bright = brightest_per_row[y][1]
            if x_bright > x_start and x_bright < x_end:
                bright_groups.append([y, [x_start, x_end]]) #could consider putting brightness here for error checkin
    
    return bright_groups

def regularize_individual_outliers(groups, margin = 4): #incomplete

    '''
    program to get rid of points that are isolated, or not part of a larger curve/scale
    groups in form [[y[xstart,xend]][y2[x2start,x2end]]]
        y used for x value, when the array is reoriented so y is x.

    margin is in pixels
    '''
    #delete single sided outliers, vs dual sided outliers - single sided contribute data.
    #keep reserve of single sided outliers?
    new_groups = []

    cutoff_count = 0 #prevents infinite while group
    i = len(groups) - 2

    while i > 1 and cutoff_count < 10000:
        y_prev = groups[i-1][0]
        y = groups[i][0]
        y_next = groups[i+1][0]
        if y_next - y == 1 and y - y_prev == 1:
            x_prev_start = groups[i-1][1][0]
            x_prev_end = groups[i-1][1][1]
            x_start = groups[i][1][0]
            x_end = groups[i][1][1]
            if abs(x_start - x_prev_start) > margin or abs(x_end - x_prev_end) > margin:
                del(groups[i:i+2])
                i -= 3


            '''
            x__next_start = groups[i][1][0]
            x_next_end = groups[i][1][1]
            if abs(x_next_end - x_prev_end) > 2 * margin:
                del(groups[i-1:i+2])
                i-=2 #will be -3 after cycle
            elif 

                
                x_start_avg = (x_prev_start + x__next_start)//2
                x_end_avg = (x_prev_end + x_next_end)//2
              


                if (x_start < x_start_avg - margin or x_start > x_start_avg + margin) \
                    and (x_end > x_end_avg - margin and x_end < x_end_avg + margin):
                    x_start = groups[i][1][0] = x_start_avg
                elif (x_end < x_end_avg - margin or x_end > x_end_avg + margin) \
                    and (x_start > x_start_avg - margin and x_start < x_start_avg + margin):
                    x_end = groups[i][1][1] = x_end_avg
                
                else: #get rid of outliers
                    print('group i', i)
                    print(x_prev_start, x_prev_end)
                    print( x_start, x_end)
                    print(x__next_start,x_next_end)
                    del(groups[i])
                    i -=1 #resets so that the next value is analyzed
            '''
                
        
        i-=1
        cutoff_count +=1

    del(groups[0:margin])
    del(groups[-margin: ])     
    return groups
        
def convert_masses(x_masses, width): 
    '''
    converts rotated masses from imgur to y masses
    works for image array that has been rotated left

    [combined_mass, [[h_min, w_h_min], [h_max, w_h_max], [h_w_min, w_min], [h_w_max, w_max]], mass_ID]
    '''
    width = width - 1 #done to preserve changes
    y_masses = []
    for x_mass in x_masses:
        [w_max, h_w_max], [w_min, h_w_min], [w_h_min, h_min], [w_h_max, h_max] = x_mass[1] 
        y_mass = [x_mass[0]] #combined mass
        y_mass.append([[h_min, width - w_h_min], [h_max, width- w_h_max],[h_w_min, width - w_min], [h_w_max, width - w_max]])
        y_mass.extend([x_mass[2]])
        y_masses.append(y_mass) #appends single mass (y_mass) to collection of masses (y_masses)
 
    return y_masses
   
def combine_masses(y_masses, y_x_masses): 
    '''
    goes through masses and combines masses that have overlap
    masses in form of
    [combined_mass, [[h_min, w_h_min], [h_max, w_h_max], [h_w_min, w_min], [h_w_max, w_max]], mass_ID]

    intended for small sized mass groups, if using very large groups, could consider arranging by location for 
    easier filtering

    consider putting in overlap, so multiple overlaps and they get added
    '''
    combo_mass = []
    count=0
    for y_mass in y_masses: #might be a better way to sort - 25 iterations if 5 masses
        for y_x_mass in y_x_masses:
            if overlap_check(y_mass, y_x_mass):
                combo = mass_combine(y_mass, y_x_mass)
                combo_mass.append(combo)              
            count+=1
    return combo_mass


def internal_combine_masses(combo_masses): 
    '''
    combines all the masses within a single grouping
    '''
    combo = combo_masses[0]
    for i in range(1,len(combo_masses)):
        combo = mass_combine(combo, combo_masses[i])
    return combo


def overlap_check(mass1, mass2, margin = 2): 
    '''
    mass in form of [mass, [[h_min, w_h_min], [h_max, w_h_max], [h_w_min, w_min], [h_w_max, w_max]], mass_ID]

    determines if two masses are overlapping

    margin used as buffer, around neck masses could be overlapping
    '''
    
    #['y_inferior'], ['y_superior'], ['x_lateral'], coords['x_medial']
    
    coords1 = mass_to_dict(mass1)
    coords2 = mass_to_dict(mass2)

    if coords1['y_superior'] > coords2['y_inferior'] + margin or \
        coords2['y_superior'] > coords1['y_inferior'] + margin  or \
        coords1['x_lateral'] < coords2['x_medial'] - margin or \
        coords2['x_lateral'] < coords1['x_medial'] - margin:
        return False

    return True

def print_coords(coords1):
    '''
    for error proofing
    '''
    print('y_superior',  coords1['y_superior'])
    print( 'y_inferior', coords1['y_inferior']) 
    print('x_lateral',    coords1['x_lateral']) 
    print('x_medial', coords1['x_medial'])
    


def get_variance_of_groupings(compact_img_arr, bright_groupings):
    '''
    bright_groupings is in form of [y, [x_start, x_end]]
    compact_img_arr in form of [[y1x1, y1x2],[y2x1, y2x2]] -yx corresponds to brightness of row y/column x

    isolates groupings that have the lowest variance
    presumes groups with tissue + prosthesis will have a higher variance than prosthesis alone
    -likely tissue alone will have greater variance than prosthesis alone as well
    '''
    vars = []
    for i, row in enumerate(bright_groupings):
        y = row[0]
        x_start = row[1][0]
        x_end = row[1][1]
        select_var = np.var(compact_img_arr[y][x_start:x_end])
        vars.append([y, select_var])
    
    return(vars)

def isolate_low_var_groups(bright_groupings, vars, retained = .7):
    '''
    bright_groupings is in form of [y, [x_start, x_end]]
    vars is in form of [[y, var for range in y],[y2...]]

    eliminates larger variances
    done to eliminate ranges that don't have the prosthesis
    '''
 
    vars.sort(key=lambda row: row[1])

     #proportion of vars that are cutoff from samples
    length = len(vars)
    
    vars = vars[:int(retained*length)]
    
    low_var_bright_groupings = []
    
    for i, var in enumerate(vars):
        y = var[0]
        try:
            low_var_bright_groupings.append(bright_groupings[y])
        except IndexError:
            pass
    
    return low_var_bright_groupings
    

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



def mark_groupings(refined_arr, refined_group, color = [0,255,0]):
    """
    mark_groupings is used for error checking

    refined_group has coordinates [y,[x_start, x_end], [x_start,x_end]],[y,[x_start...]]
    """
    ''' 
    not sure what this is for below, need to look into it
    if len(refined_group[0]) == 3: 
        for group in refined_group:
            del(group[2])
    '''
    excluded_length = 2
    for i in range(1,len(refined_group)):
        y = refined_group[i][0]
        for j in range(1, len(refined_group[i])):
            x_start = refined_group[i][j][0]
            x_end = refined_group[i][j][1]
            if x_end - x_start > excluded_length:
                refined_arr[y][x_start] = color
                refined_arr[y][x_end] = color


def mark_mass(img_arr, mass, color = [0,255,0]): 
    '''
    draws rectangle around bounds of image
    '''
    [[h_min, w_h_min], [h_max, w_h_max], [h_w_min, w_min], [h_w_max, w_max]] = mass[1]
    for y in range(h_min, h_max):
        img_arr[y][w_min] = img_arr[y][w_max] = color
    for x in range(w_min, w_max):
        img_arr[h_min][x] = img_arr[h_max][x] = color

    return img_arr


def get_cutoff(img_arr, brightest_fraction = .15):
    """
    returns the lowest pixel value within the brightest fraction
    consider putting function
    """
    brightest = np.max(img_arr)
    dimmest = np.min(img_arr)
    cutoff = int(brightest-(brightest-dimmest)*brightest_fraction)
    return cutoff, brightest

def get_groupings(img_arr, cutoff, buffer = 4, axis_0 = 'y'):
    '''
    creates a list of lists of segments with pixel values above the cutoff value

    img_arr is an array for the image
    cutoffs is the single cutoff point
    buffer excludes white edges of image, which are 
    
    h corresponds to y for axis_0 = y, when y orientation of the prosthesis is upright
    -will be x, if prosthesis image mistakenly put sideways

    return:
        for axis 0 = x --> [[x,[y_start, y_end, mass],[w_start, w_end, mass],[x, [ystart, yend, mass]]...]
        for axis 0 = y --> [[y,[x_start, x_end],[x_start, x_end]] (most typical)
            -y = row
            x_start = first x value above cutoff 
            x_end = last x_value above segment

    NOTE: x and y are used interchangeably with w and h.
    '''

    if axis_0 == 'x': #x become axis 0, each axis 0 value corresponds to an x value, spans across y values
        img_arr = np.swapaxes(img_arr,0,1)
   
    height = len(img_arr)   #in unaltered photo y values are axis 0, and so represents height, altering matricy makes x height
    width = len(img_arr[0]) 

    groupings = []

    for h in range(buffer, height-buffer):
        w_length = 0
        w_segments = [h] #index 0 of the spans will be the height
        # w_segments could be set to groupings[len(groupings)-1], but this is less clear
        #cutoff = cutoffs[h][0]
        for w in range(buffer, width-buffer):
            intensity = img_arr[h][w][0] #if not greyscale, could do average of [0],[1],[2]
            if intensity > cutoff:
                if w_length == 0: #could probably do without w_length
                    w_start = w
                w_length += 1
                if w == width - buffer - 1: #at edge of frame
                    w_end = w
                    w_segments.append([w_start, w_end])
            else: #intensity < cutoff
                if w_length > 0: 
                    w_end = w-1
                    w_segments.append([w_start, w_end])
                w_length = 0
        if len(w_segments) > 1: #take out x columns with no corresponding y values
            groupings.append(w_segments) 

    return groupings

def visualize_y_groupings(img_arr, y_groupings):
    '''
    img_arr is incoming array
    y_groupings are groups of x spans along the y axis where all the values are larger than the cutoff
        is arranged as [[y,[x_start, x_end],[x_start, x_end]],[[y,[x_start, x_end]... (most typical)
        y values are arranged from small to large
    '''
    for i, column in enumerate(y_groupings):
        y = column[0]
        for x_vals in range(1, len(column)):
            x_start = column[x_vals][0]
            x_end = column[x_vals][1]
            img_arr[y][x_start][1] = img_arr[y][x_end][0] = 255 #color positions [R, G, B] for 0,1,2
    return img_arr
          

def get_masses(groupings):
    '''
    :param groupings:[[h,[w_start, w_end],[w_start, w_end],[h, [w_start, w_end, mass]]...]
            this becomes [[h,[w_start, w_end, mass_ID],[w_start, w_end, mass_ID]][h]
        the groupings are the segments above a certain brightness
        h is the height/ y value,    w_start, w_end are the start and end of width respectively

    coords are as follows           [[h_min, w_h_min][h_max, w_h_max] [h_w_min, w_min] [h_w_max, w_max]...
    for masses is as follows      [combined_mass, [[h_min, w_h_min], [h_max, w_h_max], [h_w_min, w_min], [h_w_max, w_max]], mass_ID]
                           
    masses[mass_ID] is the mass (or volume) that corresponds to the mass_ID


    consider converting files to nested dictionary for easy access
    '''
    
    masses = []

    for span in range(1, len(groupings)): #span is y and corresponding x value ranges (unless image dimensions swapped)
        h = groupings[span][0]     #this is the row for the columns or the column for the row
        prev_h = groupings[span - 1][0]

        if h - prev_h == 1: #this ensures adjacent x pixels for overlap
            w_seg = 1 #y segments start at 1, x is at position 0
            w_prev_seg = 1

            #w_seg, w_prev_seg are the y starts, ends and masses, start at 1, end at len - 1
            while w_seg < len(groupings[span]) and w_prev_seg < len(groupings[span - 1]): #or <= ?
                #use variables for clarification
                w_start = groupings[span][w_seg][0]
                w_end = groupings[span][w_seg][1]

                w__prev_start = groupings[span-1][w_prev_seg][0]
                w_prev_end = groupings[span-1][w_prev_seg][1]

                #if there is overlap between the segments
                if (w_start <= w__prev_start and w_end >= w__prev_start) \
                    or (w__prev_start <= w_start and w_prev_end >= w_start):

                    try:
                        groupings[span-1][w_prev_seg][2] #checking if previous mass was assigned a mass ID
                        prev_mass_ID = groupings[span - 1][w_prev_seg][2] #create variable assignment for simplicity

                        try:
                            groupings[span][w_seg][2] #checking if current mass ID and previous mass ID
                            mass_ID = groupings[span][w_seg][2] #get mass ID from current segment if current mass ID

                            if mass_ID != prev_mass_ID: #they are listed as separate masses
                                masses[mass_ID] = mass_combine(masses[mass_ID], masses[prev_mass_ID]) #could do masses[mass_ID] = if prob
                                groupings[span - 1][w_prev_seg][2] = mass_ID #prev ID = mass_ID, avoid counting twice

                        except IndexError: #if no current mass ID but there is a previous mass ID
                            mass_ID = prev_mass_ID                  #get mass ID from previous segment
                            groupings[span][w_seg].append(mass_ID)  #give mass ID to current segment
                            new_mass = convert_segment_to_mass(h, w_start, w_end, mass_ID)
                            masses[mass_ID] = mass_combine(new_mass, masses[mass_ID])

                    except IndexError: #no previous mass ID

                        try:                #if current mass_ID
                            groupings[span][w_seg][2] #checking if current mass ID
                            mass_ID = groupings[span][w_seg][2] #current mass_ID exists, but no previous
                            groupings[span - 1][w_prev_seg].append(mass_ID) #previous ID assigned from current
                            
                            new_mass = convert_segment_to_mass(h-1, w__prev_start, w_prev_end, mass_ID)

                            masses[mass_ID] = mass_combine(masses[mass_ID], new_mass) 

                        except IndexError: #no current or previous mass_ID
                            mass_ID = len(masses)  # new mass ID
                            groupings[span - 1][w_prev_seg].append(mass_ID)
                            groupings[span][w_seg].append(mass_ID)

                            mass1 = convert_segment_to_mass(h, w_start, w_end, mass_ID)
                            mass2 = convert_segment_to_mass(h, w__prev_start, w_prev_end, mass_ID)

                            masses.append(mass_combine(mass1, mass2))

                #advance the while loop
                if w_end <= w_prev_end:
                    w_seg += 1
                if w_end >= w_prev_end:  #this will put both a step forward if equal
                    w_prev_seg += 1
            
    return masses, groupings


def convert_segment_to_mass(h, w_start, w_end, mass_ID):
    '''
    turns a segment into a list for which will be incorporated into masses list
    h is the height level, or the lengthwise level, usually corresponds to y axis
    w_start is where the width segment starts
    w_end is where the width segment ends
    :param mass_ID: the new mass ID that is created
    :return: segment returned in form of mass block
        mass is the length of the segment
        w is the middle of the width
     mass_ID to verify correlations
        if x is in h direction, y in w direction, returns [h_min, y ] [xmax, y,] [x, ymin,] [x, ymax]]
    '''
    w = (w_start + w_end) //2    #used for maximum value in w direction
    mass = w_end - w_start

    return [mass, [[h, w], [h, w], [h, w_start], [h, w_end]], mass_ID]


def mass_combine(mass_supplemented, mass_negated):
    '''
    program to combine masses
    incoming masses in form of [mass,[[hmin, whmin], [hmax,whmax], [hwmin, wmin], [hwmax, wmax]]]
    -mass is the amount of adjoining pixels above the cutoff brightness
    :param mass_supplemented:
    :param mass_negated: mass is removed to avoid double counts, mins and maxes are retained
    '''
    mass_ID = mass_supplemented[2]

    combined_mass = mass_supplemented[0] + mass_negated[0] #these are the masses

    mass_negated[0] = 0           #prevent double count if mass is collected again

    h_min = min(mass_supplemented[1][0][0], mass_negated[1][0][0])
    h_max = max(mass_supplemented[1][1][0], mass_negated[1][1][0])
    w_min = min(mass_supplemented[1][2][1], mass_negated[1][2][1])
    w_max = max(mass_supplemented[1][3][1], mass_negated[1][3][1])

    #corresponding coordinates to min and max
    w_h_min = mass_negated[1][0][1] if h_min == mass_negated[1][0][0] else mass_supplemented[1][0][1]
    w_h_max = mass_negated[1][1][1] if h_max == mass_negated[1][1][0] else mass_supplemented[1][1][1]
    h_w_min = mass_negated[1][2][0] if w_min == mass_negated[1][2][1] else mass_supplemented[1][2][0]
    h_w_max = mass_negated[1][3][0] if w_max == mass_negated[1][3][1] else mass_supplemented[1][3][0]

    mass_supplemented = [combined_mass, [[h_min, w_h_min], [h_max, w_h_max], [h_w_min, w_min], [h_w_max, w_max]], mass_ID]

    return mass_supplemented


def mass_check(masses):
    '''
    for error checking
    ensures mass ID corresponds to location of mass
    mass_ID is redundant, self contained,
    masses[mass_ID][2] = mass_ID
    '''
    for x in range(len(masses)):
        if x != masses[x][2]:
            return False
    return True


def order_masses(masses):
    ordered_masses = sorted(masses, key=operator.itemgetter(0), reverse = True)
    return ordered_masses

def bridge_masses_by_y(masses_by_y, skip = 2):#incomplete
    '''
    combines masses that are within prosthesis, or same body and cut off
    masses_by_y [combined_mass, [[h_min, w_h_min], [h_max, w_h_max], [h_w_min, w_min], [h_w_max, w_max]], mass_ID]
    y groupings in form of [[h,[w_start, w_end, mass_ID],[w_start, w_end, mass_ID]] - h for y, w for x
    edge_groups as lowest difference to the highest difference
    #       [[y0,[ [diff 1, x1] ,[diff 2, x2] ,[diff 3, x3],... [diff n, xn]][y1...]] 
    
    
    '''
    
    mass_length = len(masses_by_y)

    mass_IDs = []

    #coords 2 are the inferior grooping, mass_ID from coords_1 will be used
    coords_2 = mass_to_dict(masses_by_y[-1])
    for i in reversed(range(0, mass_length - 1)): 
        coords = mass_to_dict(masses_by_y[i])


        if within_range(coords['y_inferior'], coords_2['y_superior'], coords['x_medial'], coords['x_lateral'], \
            coords_2['x_medial'], coords_2['x_lateral'], skip ):
                mass_ID = masses_by_y[i][2]
                mass_ID_2 = masses_by_y[i+1][2]
                masses_by_y[mass_ID] = mass_combine(masses_by_y[mass_ID], masses_by_y[mass_ID_2])
                mass_IDs.extend([mass_ID_2, mass_ID])
                del(masses_by_y[i+1])
                
        coords_2 = coords #coords2 moves up

    mass_IDs = list(set(mass_IDs))
    return masses_by_y, mass_IDs
    


def within_range(y, y_next, x_start, x_end, x2_start, x2_end, skip = 2):
    '''
    determines if two segments are within range
    '''
    if skip < 2:
        skip = 2
    #check if y values within range of eachother
    if y_next - y > skip:
        return False
    #check if x boundaries overlap
    if (x2_start < x_end and x2_start > x_start) or (x2_end < x_end and x2_end > x_start):
        return True
    return False

def get_mass_coordinates(mass):
    '''
    mass in form of [mass, [[h_min, w_h_min], [h_max, w_h_max], [h_w_min, w_min], [h_w_max, w_max]], mass_ID]

    h_min, w_min, h_max, w_max - 4 coords of mass returned 
    h_min is height minimum value, lowest y value, but y not used due to reorientation
    w_min is lowest width value
    NOTE: RETURN IS IN DIFFERENT ORDER THAN STORAGE IN LIST MASS
    could redo so return corresponds to x1, y1, x2, y2 pattern

    consider returning in form of a dictionary to reduce need to reference
    '''
    h_min = mass[1][0][0]
    h_max = mass[1][1][0]
    w_min = mass[1][2][1]
    w_max = mass[1][3][1]

    return h_min, w_min, h_max, w_max

def get_all_mass_coordinates(mass):##
     h_min, w_min, h_max, w_max = get_mass_coordinates(mass)
     w_h_min = mass[1][0][1]
     w_h_max = mass[1][1][1]
     h_w_min = mass[1][2][0]
     h_w_max = mass[1][3][0]
     return h_min, w_h_min, h_max, w_h_max, h_w_min, w_min, h_w_max, w_max

def convert_coordinates_to_dictionary(values):
    '''
    program to convert get_all_mass/get_mass programs into dictionary of coordinates
    '''
    coords = {}
    if len(values) == 8:
        [h_min, w_h_min, h_max, w_h_max, h_w_min, w_min, h_w_max, w_max] = values
        coords['x_inferior'] = w_h_max
        coords['x_superior'] = w_h_min
        coords['y_lateral'] = h_w_max
        coords['y_medial'] = h_w_min
    elif len(values) == 4:
        [h_min, w_min, h_max, w_max] = values
    else:
        print('error, incorrect number of values into convert_coordinates')
        return

    coords['y_inferior'] = h_max
    coords['y_superior'] = h_min
    coords['x_lateral'] = w_max
    coords['x_medial'] = w_min
    coords = get_derived_data(coords)

    return coords

def get_derived_data(coords):
    #could include put program within convert coordinates to dictionary, but wanted flexibility for the use
    coords['width'] = coords['x_lateral'] - coords['x_medial']
    coords['height'] = coords['y_inferior'] - coords['y_superior'] #could do y_lateral instead, for stem height
    coords['mass'] = coords['width'] * coords['height']
    return coords

def convert_mass_coordinates(h_min, w_h_min, h_max, w_h_max, h_w_min, w_min, h_w_max, w_max, axis_0 = 'y'):
    """axis_0 = y value corresponds to h"""
    if axis_0 == 'y':
        y_min, x_y_min, y_max, x_y_max, y_x_min, x_min, y_x_max, x_max = h_min, w_h_min, h_max, w_h_max, h_w_min, w_min, h_w_max, w_max
    else:
        x_min, y_x_min, x_max, y_x_max, x_y_min, y_min, x_y_max, y_max = h_min, w_h_min, h_max, w_h_max, h_w_min, w_min, h_w_max, w_max
    return x_min, y_x_min, x_max, y_x_max, x_y_min, y_min, x_y_max, y_max


def get_coords_distances(mass):
    '''
    get's the distances between all of the coordinates of the prosthesis
    takes a single mass from the masses list
    ASSUMES minimum difference between points is on the two edges of the ball/socket
    ASSUMES orientation of prothesis may not be upright, but the high and low points will correspond
        to the same landmarks used to find the orientation
    :param mass = masses[mass_ID] -  for mass that corresponds to implant (largest/brightest by default)
    :return: the distances between the coordinates
    TODO: ? consider creating coords_distances as a dictionary or a nested dictionary for clarity
    '''
    x_min, y_x_min, x_max, y_x_max, x_y_min, y_min, x_y_max, y_max = get_all_mass_coordinates(mass)
    x_min, y_x_min, x_max, y_x_max, x_y_min, y_min, x_y_max, y_max = convert_mass_coordinates(x_min, y_x_min, x_max, y_x_max, x_y_min, y_min, x_y_max, y_max)

    x_low  = [x_min, y_x_min]
    x_high = [x_max, y_x_max]
    y_low  = [x_y_min, y_min]
    y_high = [x_y_max, y_max]

    ordered_points = [x_low, x_high, y_low, y_high]
    x_extremes = [x_low, x_high]
    y_extremes = [y_low, y_high]

    coords_distances = []

    for x_coords in x_extremes:
        for y_coords in y_extremes:
            distance = get_distance(x_coords,y_coords) #line for clarity
            coords_distances.append([distance,[x_coords, y_coords]])

    #sort by distance- low to high - more efficient sorts, but this is a list of 4, could also sort with labeling above
    for i in range(len(coords_distances)):
        for j in range(i+1, len(coords_distances)):
            #distance is at position 0
            if coords_distances[j][0] < coords_distances[i][0]:
                coords_distances[i], coords_distances[j] = coords_distances[j], coords_distances[i]

    #coords distances are the four lines and distances from the four prominent prosthesis corners
    #use distances to find orientation and sidedness of prosthesis

    return coords_distances


def get_distance(A_coords, B_coords):
    """
    get's the distance between two sets of coordinates
    :param A_coords: [x,y]
    :param B_coords: [x,y]
    :return:
    """
    x1 = A_coords[0]
    y1 = A_coords[1]
    x2 = B_coords[0]
    y2 = B_coords[1]

    #pythagorean's theorom
    distance = ((x1 - x2)**2 + (y1 - y2)**2)**.5
    return distance

def get_orientation(coords_distances):
    """
    returns dictionary of coords
    -dictionary holds x and y points of boundaries of coords. eg x_superior, y_superior, x_lateral, y_lateral

    coords_distances is in form of [[distance between A and B, [[point A,coord A][point B]]...]
    -eg. [[176.7766952966369, [[42, 233], [167, 108]]], [329.0060789711947, [[42, 233], [304, 432]]], [654.0412831006923, [[955, 369], [304, 432]]], [830.0993916393386, [[955, 369], [167, 108]]]] 
    -in other words coords_distances = [distance,[x_coords, y_coords]],[distance,[x_coords, y_coords]]...]
    -distances between the coordinates are sorted from low to high
    the superior, inferior, medial and lateral coordinates of the hip replacement determined by distances of points
    superior coordinate is in the two smallest distances
    -smallest distance is med - superior, second smallist is sup - lateral
    medial is in the largest and smallest
    -largest is medial - inferior
    lateral is in the middle two distances
    inferior is in the largest two distances

    NOTE: order of coordinates doesn't correspond to order in masses

    POTENTIAL PROBLEM IF VERY SKEWED PROSTHESIS AND THERE ARE TWO EQUAL (TIED) VALUES FOR (Y OR X) MAX OR MIN
    -TODO: write code to adjust to this problem
    """
    coords = dict()
    #superior and medial points will have the shortest distance between them
    if coords_distances[0][1][0] == (coords_distances[1][1][0] or
                                     coords_distances[1][1][1]):
        coords['x_superior'] = coords_distances[0][1][0][0]
        coords['y_superior'] = coords_distances[0][1][0][1]
        coords['x_medial'] = coords_distances[0][1][1][0]
        coords['y_medial'] = coords_distances[0][1][1][1]
    else:
        coords['x_superior'] = coords_distances[0][1][1][0]
        coords['y_superior'] = coords_distances[0][1][1][1]
        coords['x_medial'] = coords_distances[0][1][0][0]
        coords['y_medial'] = coords_distances[0][1][0][1]

    #inferior + lateral common in third largest distance
    if coords_distances[2][1][0] == (coords_distances[3][1][0] or
                                    coords_distances[3][1][1]):
        coords['x_inferior'] = coords_distances[2][1][0][0]
        coords['y_inferior'] = coords_distances[2][1][0][1]
        coords['x_lateral'] = coords_distances[2][1][1][0]
        coords['y_lateral'] = coords_distances[2][1][1][1]
    else:
         coords['x_inferior'] = coords_distances[2][1][1][0]
         coords['y_inferior'] = coords_distances[2][1][1][1]
         coords['x_lateral'] = coords_distances[2][1][0][0]
         coords['y_lateral'] = coords_distances[2][1][0][1]

    coords['width'] = abs(coords['x_lateral'] - coords['x_lateral'])
    coords['height'] = abs(coords['y_inferior'] - coords['y_superior']) #abs prob not needed
    
    return coords


def get_sidedness(coords):
    """
    coords is a dictionary containing the coordinates (x,y) positions 
        of the superior, inferior, lateral, and medial most points
    returns if a left or right prosthesis and which side is at top of radiograph
    probably excessive, as a safe assumption is radiograph will always be right side up
    -if this assumption is not true, could write code to rearrange array to right side up

    PROBLEM: if two min y values are equal
  
    """
    x_diff_lat_med = coords['x_lateral'] - coords['x_medial']
    y_diff_lat_med = coords['y_lateral'] - coords['y_medial']
    x_diff_inf_sup = coords['x_inferior'] - coords['x_superior']
    y_diff_inf_sup = coords['y_inferior'] - coords['y_superior']

    #lengthwise may not be needed, could consider using a dictionary for a switch instead of if statements
    if abs(y_diff_inf_sup) > abs(x_diff_inf_sup):
        #lengthwise = 'vertical'
        if y_diff_inf_sup > 0:
            top_side = 'superior'
            if x_diff_lat_med > 0:
                component_side = 'left' #ball is on left/medial, lateral on right
            else:
                component_side = 'right'
        else:
            top_side = 'inferior'
            if x_diff_lat_med > 0:
                component_side = 'right' #ball is on left/medial,
            else:
                component_side = 'left'
    else:
        #lengthwise = 'horizontal'
        if x_diff_inf_sup > 0: #superior/socket on left side of radiograph
            if y_diff_lat_med > 0: #lateral side lower
                component_side = 'right'
                top_side = 'medial'
            else:
                top_side = 'lateral'
                component_side = 'left'
        else:                   #superior/scoket on right side of radiography
            if y_diff_lat_med > 0: #lateral side lower
                component_side = 'left'
                top_side = 'medial'
            else:
                component_side = 'right'
                top_side = 'lateral'
    return(top_side,component_side)

def map_prosthesis(img_arr, top_side, component_side):
    """
    Rearranges prosthesis to be oriented so the same mapping applies to all cases for analysis
    makes each prosthesis an upright left prosthesis
    -like a left prosthesis upright on a ap radiography
    -medial is pointing left on the radiography, lateral right side, superior top, and inferior bottom

    """
    rotations = 0
    if top_side == 'lateral' and component_side == 'left' or \
        top_side == 'medial' and component_side == 'right':
            rotations = 3
    if top_side == 'lateral' and component_side == 'right' or \
        top_side == 'medial' and component_side == 'left':
            rotations = 1
    if top_side == 'inferior':
            rotations = 2
    img_arr = np.rot90(img_arr, rotations)
    if component_side == 'right':
        img_arr = np.fliplr(img_arr)
    
    return img_arr


def get_brightness_cutoff(img_arr, coords): 
    '''
    gets the lowest brightness within the known coordinates (coords) of the image array (img_arr)
    coords has keywords lateral, medial, inferior, superior, with y_ and x_ in front of them

    '''
    # faster ways to do belows
    max_brightness_cutoff = max(int(img_arr[coords['y_superior']+1][coords['x_superior']][0]), int(img_arr[coords['y_inferior']-1][coords['x_inferior']][0]), \
        int(img_arr[coords['y_medial']][coords['x_medial']+1][0]), int(img_arr[coords['y_lateral']][coords['x_lateral']-1][0]) )
    
    min_brightness_cutoff = min(int(img_arr[coords['y_superior']+1][coords['x_superior']][0]), int(img_arr[coords['y_inferior']-1][coords['x_inferior']][0]), \
        int(img_arr[coords['y_medial']][coords['x_medial']+1][0]), int(img_arr[coords['y_lateral']][coords['x_lateral']-1][0]) )

    return max_brightness_cutoff, min_brightness_cutoff



def get_segments_within_mass(img_arr, cutoff, buffer = 4, axis_0 = 'y'):#incomplete?
    '''
    creates a list of lists of segments with pixel values above the cutoff value

    img_arr is an array for the image
    cutoffs is the single cutoff point
    buffer excludes white edges of image
    
    h corresponds to y for axis_0 = y, when y orientation of the prosthesis is upright
    -will be x, if prosthesis image mistakenly put sideways

    return:
        for axis 0 = x --> [[x,[y_start, y_end, mass],[w_start, w_end, mass],[x, [ystart, yend, mass]]...]
        for axis 0 = y --> [[y,[x_start, x_end],[x_start, x_end]] (most typical)
            -y = row
            x_start = first x value above cutoff 
            x_end = last x_value above segment

    NOTE: x and y are used interchangeably with w and h.
    '''

    if axis_0 == 'x': #x become axis 0, each axis 0 value corresponds to an x value, spans across y values
        img_arr = np.swapaxes(img_arr,0,1)
   
    height = len(img_arr)   #in unaltered photo y values are axis 0, and so represents height, altering matricy makes x height
    width = len(img_arr[0]) 

    groupings = []

    for h in range(buffer, height-buffer):
        w_length = 0
        w_segments = [h] #index 0 of the spans will be the height
        #cutoff = cutoffs[h][0]
        for w in range(buffer, width-buffer):
            intensity = img_arr[h][w][0] #if not greyscale, could do average of [0],[1],[2]
            if intensity > cutoff:
                if w_length == 0:
                    w_start = w
                w_length += 1
                if w == width - buffer - 1: #at edge of frame
                    w_end = w
                    w_segments.append([w_start, w_end])
            else: #intensity < cutoff
                if w_length > 0: 
                    w_end = w-1
                    w_segments.append([w_start, w_end])
                w_length = 0
        if len(w_segments) > 1: #take out x columns with no corresponding y values
            groupings.append(w_segments)

    return groupings



def get_shell_quarters(image, shell_coords):
    """
    THIS PROGRAM IS FOR ERROR CHECKING - ENSURING THE SHELL IS IDENTIFIED, not used in computation
    consider removing?
    :param image: image of prosthesis
    :param shell_coords: in form of [[x,y],[x,y]], where on quarter covered by x and y
    :return: image with elipse drawn in over shell is returned
    """

    [[x_1, y_1],[x_2, y_2]] = shell_coords
    x_max = max(x_1, x_2)
    x_min = min(x_1, x_2)
    y_max = max(y_1, y_2)
    y_min = min(y_1, y_2)

    x_max = 2 * (x_max - x_min) + x_min  # for left prothesis, stem on right side
    y_max = 2 * (y_max - y_min) + y_min

    shell_coords = [x_min, y_min, x_max, y_max]

    shell_quarters = x_min, y_min, x_max, y_max
    draw = ImageDraw.Draw(image)
    draw.ellipse([x_min, y_min, x_max, y_max], fill=None, outline=(0, 255, 0))

    return image



def get_head_shell_info(img_arr, coords, cutoff):
    """
    For isolating the femoral head from the femoral shell

    probably not needed

    Could be used to further analyze prosthesis
    :param img_arr: image array
    :param coords: coordinates of the prosthesis med, sup, lat, inf
    :param cutoff: cutoff value of pixel
    :return: head_info: dictionary of head with radius, x center, y center, and the head bounds
                head_bounds is a list of the lowest x and y bounds of the femoral implant head
                    [low x, low y, high x, high y]
            shell info is similiar

    NOTE: unlikely to impact results, but bounding boxes are not perfect, based on radius, which is made from one direction from center. 
            For more precision, do average radius of combined edges
            
    """

    x_center, y_center =  coords['x_superior'], coords['y_medial'] #this will not work if shell is nailed in
    shell_radius = coords['y_medial'] - coords['y_superior']

    y_upper_bounds_head = coords['y_superior']

    #could make function for both of below, prob not worth it
    
    #change function to differences 
    for y in range(y_center, y_center + shell_radius):
        if img_arr[y][x_center][0] < cutoff:
            y_upper_bounds_head = y-1
            break
     
    
    #shell radius there to make sure doesn't get drop off after shell (may need to subtract more than 1)
    #below is in case shell, or item is below head (highly unlikely)
    
    x_upper_bounds_head = None
    for x in range( x_center, x_center + shell_radius):
        y = y_center
        if img_arr[y][x][0] < cutoff:
            x_upper_bounds_head = x-1
            break
    
    #extremely unlikely to get this, both x and y directions away from shell are covered by shell
    if x_upper_bounds_head == x_center + shell_radius - 1:
        x_upper_bounds_head = None
    if y_upper_bounds_head == y_center + shell_radius - 1:
        y_upper_bounds_head = None

    if x_upper_bounds_head and y_upper_bounds_head is None:
        print('ERROR, HEAD BOUNDS NOT DEFINED')
        return

    if y_upper_bounds_head is None:
        head_radius = x_upper_bounds_head - x_center
    elif x_upper_bounds_head is None:
        head_radius = y_upper_bounds_head - y_center
    else:
        head_radius = max((x_upper_bounds_head - x_center), (y_upper_bounds_head - y_center))

    #head radius is wrong, look over, see items.json
    head_bounds = [x_center - head_radius, y_center - head_radius, x_center + head_radius, y_center + head_radius]     
    shell_bounds = [x_center - shell_radius, y_center - shell_radius, x_center + shell_radius, y_center + shell_radius]  

    shell_info = dict()
    head_info = dict()
    head_info['x_center'] = x_center
    head_info['y_center'] = y_center
    head_info['radius'] = head_radius
    head_info['bounds'] = head_bounds
    head_info['y_superior'] = y_center - head_radius
    head_info['y_inferior'] = y_center + head_radius
    head_info['x_medial'] = x_center - head_radius #same as x_upper_bounds_head
    head_info['x_lateral'] =  x_center + head_radius
    head_info['x_superior'] = x_center 
    head_info['x_inferior'] = x_center 
    head_info['y_medial'] = y_center #same as x_upper_bounds_head
    head_info['y_lateral'] = y_center

    shell_info['x_shell_center'] = x_center
    shell_info['y_shell_center'] = y_center
    shell_info['radius'] = shell_radius
    shell_info['bounds'] = shell_bounds
    shell_info['y_superior'] = y_center - shell_radius
    shell_info['y_inferior'] = y_center + shell_radius
    shell_info['x_medial'] = x_center - shell_radius #same as x_upper_bounds_shell
    shell_info['x_lateral'] =  x_center + shell_radius
    shell_info['x_superior'] = x_center 
    shell_info['x_inferior'] = x_center 
    shell_info['y_medial'] = y_center #same as x_upper_bounds_shell
    shell_info['y_lateral'] = y_center

    return head_info, shell_info


def get_shell_info(coords): 
    '''
    program to get the shell dimensions of the femoral head for idealized shell
    '''
    x_center, y_center =  coords['x_superior'], coords['y_medial'] #this will not work if shell has nails
    shell_radius = coords['y_medial'] - coords['y_superior']

    shell_bounds = [x_center - shell_radius, y_center - shell_radius, x_center + shell_radius, y_center + shell_radius]       

    shell_info = dict()
    shell_info['x_shell_center'] = x_center
    shell_info['y_shell_center'] = y_center
    shell_info['shell_radius'] = shell_radius
    shell_info['shell_bounds'] = shell_bounds

    return shell_info



def focus_array(img_arr, cutoff, brightest, coords, head_info):
    '''
    param:  img_arr: array of image
            cutoff: point where bright values are cut off
            brightest: brightest values
            coords: dictionary of prosthesis coords
            head_info: dictionary of info on the head of the prosthesis,
                includes x_center, y center, radius, and the upper and lower x and y values in list head_bounds
    RETURNS: 
            arr_reduced: a reduced array that frames the prosthesis and excludes the head 
            shifted_coords: dictionary of the new frame of the features within arr_reduced
            reduction_area: dictionary of the reduced area points or confines within img_arr

    THIS FUNCTION IS NOT STRICTLY NECCESSARY, cosmetic and for error solving
    -a search could analyze the area of the prosthesis without creating a new image
    -new image is done for simplicity, ease of error checking

    ALTERNATIVELY: could create function that refines buffer based upon excluded values
    '''

    x_center = head_info['x_center'] 
    y_center = head_info['y_center'] 
    
    #coordinates will skew the reduction_arr results
    #check for superior y portion in revised head
    if coords['y_lateral'] > y_center:
        y_superior = y_center 
    else:
        y_superior = coords['y_lateral']
    y_adjust = y_superior - y_center #for excluding head if the lateral coordinate is superior
    
    #check if center of head is more medial than inferior tip of stem
    if x_center < coords['x_inferior']:
        x_medial =  x_center
    else:
        x_medial = coords['x_inferior']
    x_adjust = x_medial - x_center #for head if inferior_coord is medial

    
    reduction_buffer = 10 #reduction buffer has to move in sync with head
    
    reduction_area = dict() #redction are the coords framing the reduced array
    reduction_area['y_min'] = y_superior - reduction_buffer
    reduction_area['x_min'] = x_medial - reduction_buffer
    reduction_area['y_max'] = coords['y_inferior'] + reduction_buffer
    reduction_area['x_max'] = coords['x_lateral'] + reduction_buffer

    #check that reduction area doesn't exceed value of array get rid of redcution area for viewing
    max_length = len(img_arr)
    max_width = len(img_arr[0])
    if reduction_area['y_min'] < 0:
        reduction_area['y_min'] = 0
    if reduction_area['x_min'] < 0:
        reduction_area['x_min'] = 0
    if reduction_area['y_max'] > max_length:
        reduction_area['y_max'] = max_length
    if reduction_area['x_max'] > max_width:
        reduction_area['x_max'] = max_width
    
    #arr_reduced is an array that is reduced to the area of the prosthesis
    arr_reduced = img_arr[reduction_area['y_min']:reduction_area['y_max'], reduction_area['x_min']:reduction_area['x_max']]

    #reorient coords coordinates to fit shifted_coords
    y_shift = reduction_area['y_min']
    x_shift = reduction_area['x_min']
    shifted_coords = dict()
    shifted_coords['x_lateral'] = coords['x_lateral'] - x_shift
    shifted_coords['x_inferior'] = coords['x_inferior'] - x_shift
    shifted_coords['x_medial'] = coords['x_medial'] - x_shift
    shifted_coords['x_superior'] = coords['x_superior'] - x_shift

    shifted_coords['y_lateral'] = coords['y_lateral'] - y_shift
    shifted_coords['y_inferior'] = coords['y_inferior'] - y_shift
    shifted_coords['y_medial'] = coords['y_medial'] - y_shift
    shifted_coords['y_superior'] = coords['y_superior'] - y_shift
    
    shifted_coords['x_head_center'] = x_center - x_shift
    shifted_coords['y_head_center'] = y_center - y_shift


    shifted_coords = get_derived_data(shifted_coords)

    coords['x_center'] = x_center
    coords['y_center'] = y_center
    
    #arr_reduced = exclude_head(arr_reduced,head_info, shifted_coords)
    
    brightest = np.max(arr_reduced)

    #below is redundant, consider excluding for more refined options of evaluating arr_reduced
    for y in range(len(arr_reduced)):
        for x in range(len(arr_reduced[0])):
            value = arr_reduced[y][x][0]
            if value > cutoff:
                value = int((value - cutoff)/(brightest-cutoff) * 255)
                arr_reduced[y][x] = [value]*3
            else:
                arr_reduced[y][x] = [0,0,0]
        
    return arr_reduced, reduction_area, shifted_coords


def exclude_head(arr_reduced, head_info, shifted_coords):
    """
    program excludes the head from arr_reduced
    not strictly neccessary - useful for error checking
        could be used to improve downstream functionality
    params:
        arr_reduced: array of reduced area of prothesis
        head_info: dictionary of info on the head of the prosthesis,
                includes x_center, y center, radius, and the upper and lower x and y values in list: head_bounds
        shifted_coords: position of coordinates within arr_reduced
    """

    head_buffer = 1.1 #head_info does not perfectly encapsulate head, due to ovoid features of heads
    head_radius = int(head_info['radius'] * head_buffer) #head_buffer better encapsulates head

    #head_exclusion_arr will be the array for the area of the head plus the medial and superior area away from the prosthesis
    head_exclusion_arr = []
    for x in range(head_radius + 1): #adding 1 serves to catch low value of radius distance
        for y in range(head_radius + 1):
            if head_radius ** 2 <= (x+1)**2 + (y+1)**2: #adding one is for zero values
                head_exclusion_arr.append([y, x])
                head_exclusion_arr.append([x, y])
                break

    #below are two buffers to account for the reduction array buffer (the buffer around the reduced arrays frame)
    #for less for loops could combine to arr_reduced[y][x] = arr_reduced[x][y] and make some adjustments
    arr_reduced[0:shifted_coords['y_head_center']+head_radius+1, 0:shifted_coords['x_head_center']] = [0,0,0]
    arr_reduced[0:shifted_coords['y_head_center'], shifted_coords['x_head_center']:shifted_coords['x_head_center']+head_radius+1] = [0,0,0]

    #below is to exclude the head specifically
    for i, [a,b] in enumerate(head_exclusion_arr):
        for x in range(a):
            for y in range(b):
                arr_reduced[shifted_coords['y_head_center']+ y][shifted_coords['x_head_center']+x] = [0,0,0]   
    return arr_reduced




def exclude_shell(img_arr, shell_info):#incomplete, doesn't work for all shells, come back to, along will get shell info
    """
    program excludes the shell from the image array (img_arr)
    not strictly neccessary - useful for error checking
        could be used to improve downstream functionality
    params:
        img_arr = array of prosthesis
        shell_info: dictionary of info on the shell of the prosthesis,
                includes x_center, y center, shell_radius, and the upper and lower x and y values in list: shell_bounds
  
    """

    shell_buffer = 1.1 #head_info does not perfectly encapsulate head, due to ovoid features of heads
    shell_radius = int(shell_info['shell_radius'] * shell_buffer) #shell_buffer better encapsulates shell

    #shell_exclusion_arr will be the array for the area of the shell plus the medial and superior area away from the prosthesis
    shell_exclusion_arr = []
    for x in range(shell_radius + 1): #adding 1 serves to catch low value of radius distance
        for y in range(shell_radius + 1):
            if shell_radius ** 2 <= (x+1)**2 + (y+1)**2: #adding one is for zero values
                shell_exclusion_arr.append([y, x])
                shell_exclusion_arr.append([x, y])
                break
    '''
    #below are two buffers to account for the reduction array buffer (the buffer around the reduced arrays frame)
    #for less for loops could combine to arr_reduced[y][x] = arr_reduced[x][y] and make some adjustments
    img_arr[0:shell_info['y_shell_center']+shell_radius+1, 0:shell_info['x_shell_center']] = [0,0,0]
    img_arr[0:shell_info['y_shell_center'], shell_info['x_shell_center']:shell_info['x_shell_center']+shell_radius+1] = [0,0,0]
    '''
    #below is to exclude the shell specifically
    for i, [a,b] in enumerate(shell_exclusion_arr):
        for x in range(a):
            for y in range(b):
                img_arr[shell_info['y_shell_center']+ y][shell_info['x_shell_center']+x] = [0,0,0]   
    return img_arr




def categorize_inverse_masses(ordered_inverse_masses, items, prosthesis_coords):##1
    '''
    program that categorizes areas of decreased luminosity within the prosthesis to find identifying information
    inverse masses: masses of decreased luminosity within the prosthesis, 
        -arranged from largest mass to smallest
        -allows quicker sorting, largest values are those that will most likely be evaluated
    prosthesis_coords: the coordinates of the prosthesis
    #prosthesis_coords = items['active']['features']['prosthesis_info_diff'] 

    inverse_features: nested dictionary of the features of the prosthesis and their dimensions
    '''
   
    
    x_tolerance = .1 * prosthesis_coords['width']
    y_tolerance = .1 * prosthesis_coords['height']
    
    tolerated_inv_mass_to_prosth_mass_ratio = .001
    tolerated_mass = tolerated_inv_mass_to_prosth_mass_ratio * prosthesis_coords['mass']

    #gets rid of underfined error below
    #might be able to turn below into a function, but passing variables that are undefined seems to fail

    try:
        extraction_hole
    except NameError:
        extraction_hole = {}
    try:
        stem_hollow
    except NameError:
        stem_hollow = {}


    #min is superior/medial, max is inferior/lateral
    for i, inverse_mass in enumerate(ordered_inverse_masses):
        inverse_mass_coords = mass_to_dict(inverse_mass)

        if inverse_mass_coords['mass'] < tolerated_mass: #inverse masses lower than threshold/insignificant
            break

        #this looks for a mass (an extraction hole) within the area of the lateral edge 
        if inverse_mass_coords['x_lateral'] > prosthesis_coords['x_lateral'] - x_tolerance and \
            inverse_mass_coords['y_lateral'] < prosthesis_coords['y_lateral'] + y_tolerance and extraction_hole == {}:
            extraction_hole = inverse_mass_coords
            items['active']['features']['extraction_hole'] = extraction_hole
            items['active']['features']['extraction_hole']['color'] = [255,0,255]
            if stem_hollow != {}: #cut off loop once masses are filled
                break
             
        
        #this looks for a hollowed inferior stem, could also scan for x values for error proofing
        elif inverse_mass_coords['y_superior'] > prosthesis_coords['y_inferior'] - y_tolerance and stem_hollow == {}:
            stem_hollow = inverse_mass_coords
            items['active']['features']['stem_hollow'] = stem_hollow
            items['active']['features']['stem_hollow']['color'] = [255,0,255]
            if extraction_hole != {}: #cut off loop once masses are filled
                break


    #return prosthesis_coords

def assign_undefined(var):
    try:
        var
    except NameError:
        return {}
    return var


def get_slope(y_point_A, x_point_A, y_point_B, x_point_B):
    '''
    returns the slope between two points

    y and x are sometimes reversed in order presented
    '''
    if x_point_A - x_point_B != 0: #avoid 1/0 or undefined error
        return (- y_point_A - -1* y_point_B)/(x_point_A - x_point_B) 

    return 99999 #vertical line




def get_slope_groups(groups, spacing = 1, skip = 1, sample_size= 3, angle_cutoff = .03, groups_B = []):
    '''
    consider limiting groups to area around prosthesis - could limit it before processing

    spacing is the space between two points, which make the slope
    skip is the spacing between slopes

    groups is the primary grouping of points
    groups B is a secondary grouping of points, from 90 degrees to group A

    groups in form of [y,[x start, x end],[y2,[x start 2, x end 2]]

    angle_coords_start in form of [[y midpoint, x midpoint, angle]]

    TODO review angles (had info on print)
    '''
    
    start_angles = []
    end_angles = []
    start_angles_CD = []
    end_angles_CD = []


    sample_size = sample_size//2 * 2 + 1 #ensure odd
    spacing = spacing//2 * 2 + 1 #ensure spacing is odd. 
    sample_interval = skip + spacing * 2

    angle_coords_start = [[-sample_interval*6, -100, -100]] #angle coords will be in form of [y,x, angle], angle_coords[0] will be deleted at end
    angle_coords_end = [[-sample_interval*6, -100, -100]] 

    y_length = len(groups)
    for i in range(y_length - sample_interval):
        group_A = groups[i] #A is superior group
        group_B = groups[i + spacing]

        group_C = groups[i + skip] #A is superior group
        group_D= groups[i + skip + spacing]

        y_A, x_start_A, x_end_A = get_points_from_group(group_A)
        y_B, x_start_B, x_end_B = get_points_from_group(group_B)

        y_C, x_start_C, x_end_C = get_points_from_group(group_C)
        y_D, x_start_D, x_end_D = get_points_from_group(group_D)

        start_AB = get_slope(y_A, x_start_A, y_B, x_start_B) #could reduce calculations is use spacing instead of y_A - y_B, this assumes no y values are missing
        end_AB = get_slope(y_A, x_end_A, y_B, x_end_B) 

        start_CD = get_slope(y_C, x_start_C, y_D, x_start_D)
        end_CD =  get_slope(y_C, x_end_C, y_D, x_end_D) #inferior slope

        #if flat, angle_start nad angle_end should be pi
        angle_start = get_angle(start_AB, start_CD)
        angle_end = get_angle(end_CD, end_AB)

        start_angles.append(angle_start)
        end_angles.append(angle_end)

        y_mid_point = (y_A + y_D)//2

        if abs(angle_start) > math.pi/20: #17 degrees difference - adjust value according to prosthesis
            x_mid_start = (x_start_A + x_start_D) //2
            if angle_coords_start[-1][0] < y_mid_point - sample_interval//2 and angle_coords_start[-1][2] < angle_start:
                angle_coords_start[-1] = [y_mid_point, x_mid_start, angle_start]
            else:
                angle_coords_start.append([y_mid_point, x_mid_start, angle_start])

        if abs(angle_end) > math.pi/20:
            x_mid_end = (x_end_A + x_end_D) //2
            if angle_coords_end[-1][0] < y_mid_point - sample_interval//2 and angle_coords_end[-1][2] < angle_end:
                angle_coords_end[-1] = [y_mid_point, x_mid_end, angle_end]
            else:
                angle_coords_end.append([y_mid_point, x_mid_end, angle_end])
    
    #print('start angles', start_angles[0:10])
    #print('end angles', end_angles[0:10])

    del angle_coords_start[0]
    del angle_coords_end[0]

    #print(angle_coords_start[0:4],'\n', angle_coords_end[0:4])

    return angle_coords_start, angle_coords_end

def get_angle(slope_A, slope_B):
    '''
    gets the angle between two slopes
    for start slope_A has a lower y value
    for end slope_A has a high y value
    '''
    angle_A = math.atan(slope_A)
    angle_B = math.atan(slope_B)

    if angle_A < 0:
        angle_A = math.pi + angle_A #angle A is negative
        #print('a < 0', angle_A)
    if angle_B > 0:
        angle_B = math.pi - angle_B
    
    return angle_A + angle_B



def get_points_from_group(group):
    '''
    returns points of a group from a group
    group in form of [y, [xstart, x end]]
    returns y, x_start, x_end
    '''
    return group[0], group[1][0], group[1][1]

def get_select_groupings(groupings, mass_ID):
    '''
    for error proofing
    designed to get groupings within a single mass ID
    y_groupings are returned with associated mass_ID (for error checking)
    groupings in form of [[h,[w_start, w_end, mass_ID],[w_start, w_end, mass_ID]] - (h for y, w for x)
    '''
    out_group = []
    for i, column, in enumerate(groupings):
        y = column[0]
        hold_group = [y]
        for j in range(1, len(column)):
            try:
                column[j][2]
                groupings_mass_ID = column[j][2]
                if groupings_mass_ID == mass_ID:
                    hold_group.append(column[j])
            except IndexError:
                pass
        if len(hold_group) > 0:
            out_group.append(hold_group)

    return out_group

def display_array(img_arr, title = 'image'):
    #error proofing, for easier image display

    #array is seen via save_array as image instead.
    #below three lines for vm display, don't seem to work in vm, display does work on home computer
    if not matplotlib.is_interactive():
        matplotlib.interactive(True)
    matplotlib.use('PS') 

    plt.imshow(img_arr)
    plt.title(title)
    plt.show()

def save_array_as_jpeg(img_arr, title = 'Image.jpeg'):
    im = Image.fromarray(img_arr)
    im.save(title)

def mark_rectangle(refined_arr, mass):
    '''
    marks a green rectangle around area of mass on refined array image
    used for error checking
    params:
        refined_arr - array of image closed in around the specified mass
        mass is in the form of [ mass, [[y_min],[y_max coords],[x_min coords],[x_max coords]], mass_ID]


    '''
    h_min, w_min, h_max, w_max = get_mass_coordinates(mass)
    for y in range(h_min+1, h_max): #not sure why h_min + 1 is used
        refined_arr[y][w_min] = refined_arr[y][w_max] = [0,255,0]
    for x in range(w_min, w_max+1):
        refined_arr[h_min][x] = refined_arr[h_max][x] = [0,255,0]
    return refined_arr



def mark_rectangle_from_dict(img_arr, feature, color = [0,255,0]):
    '''
    see mark_rectangle_from_mass for original code

    '''
    for y in range(feature['superior_bounds'], feature['inferior_bounds']+1): #ends on inferior bounds, need +1 to cover inferior bounds
        img_arr[y][feature['medial_bounds']] = img_arr[y][feature['lateral_bounds']] = color #feature['color']
    for x in range(feature['medial_bounds'], feature['lateral_bounds']+1):
        img_arr[feature['superior_bounds']][x] = img_arr[feature['inferior_bounds']][x] = color #feature['color']
    return img_arr

def get_inverse_group(incoming_groups):
    '''
    program to find areas of hypolucency within 
    incoming_groups has coordinates [y,[x_start, x_end], [x_start,x_end]],[y,[x_start...]]
    finds areas between x_end and next x_start. Another possibility is to simply scan for regions below the value, more efficient?
    '''
    inverse_group = []
    for group in (incoming_groups):
        hold_group = [group[0]]
        for i in (range(1,len(group)-1)):
            hold_group.append([group[i][1],group[i+1][0]])
        inverse_group.append(hold_group)
        
    return inverse_group


def isolate_large_spans(incoming_groups, width):
    '''
    program to delete smaller spans from the groups of spans
        used in inverse spans
    
    params:
        incoming_groups - spans or segments above or below a cutoff
        width - the width of the whole span
    return:
        incoming_groups are filtered groups of spans above the size of span_width (see below for span_width explanation)
    '''
    #spans below span_width will be deleted. 

    #Consider making span_width a constant, or setting a variable in place of .01
    span_width = int(width * .01)
    #this is reversed so list order is not affected by deletions
    for group in reversed(incoming_groups):
        for i in reversed(range(1, len(group))):
            if group[i][1] - group[i][0] < span_width:
                if len(group) < 2:
                    del(group)
                else:
                    del(group[i])
    return(incoming_groups)

def join_x_spans(groupings, width, permissible_gap_fraction = .05):
    '''
    program to join spans that are a certain distance away along the x axis
    groupings are the groupings within a single mass
    groupings in form of [[y,[x_start, x_end],[x_start, x_end]], [y,[x_start, x_end]]...

    could also simplify program, by creating a single span for each line.
    '''
    
    permissible_gap = int(permissible_gap_fraction * width) #this is the pixel size below which everything will be bridged
    for group in groupings: #each y level
        for j in reversed(range(2, len(group))): #scans through the x sections along y (y = group[0])
            x_start = group[j][0]
            x_end = group[j][1]
            x_prev_end = group[j-1][1]
            if x_start - x_prev_end <= permissible_gap:
                x_prev_end = x_end
                del(group[j])

    return groupings




def get_isolated_groups(superior_bounds, inferior_bounds, medial_bounds, lateral_bounds, incoming_groups):
    '''
    program designed to fill in x values if it fits a pattern of an edge
        for example, for an extraction hole, the edges may not be present along x axis
            the extraction hole could have x edges at 45 and 50
            and be along y values from 10 to 50, but the y values of 20 doesn't have any x_edges
            this will fill in the y value of 20 with x edges 45 and 50
    
    another possibility is to get x groupings (instead of y groupings) and apply the join_spans program \
        (which was written after this one)

    params:
        _bounds - the bounds of the evaluated area in each direction
        incoming_groups - the segments that will be evaluated in teh area
    return: isolated groups - groups where gaps have been filled in, that are within the permissible range
    '''
    #the permissible gap is the gap in which segments could be missing, but the program will still fill in the edges
    permissible_gap = 6 #alternatively could do int(.2 * (superior_bounds - inferior_bounds))
    isolated_groups = []
    for i, group in enumerate(incoming_groups):
        y = group[0]
        if y > inferior_bounds:
            return isolated_groups
        if y >= superior_bounds:
            #group[1:] is start because y is group[0]
            for j, x_group in enumerate(group[1:]):
                x_min = x_group[0]
                x_max = x_group[1]
                if x_max > lateral_bounds: #could have x_min > lateral_bounds instead
                    break
                if x_min > medial_bounds: 
                    try: #check if isolated_groups has been filled (specifically has a length and a 2 axis structure)
                        y_end = isolated_groups[-1][0] #y_end is the previous y value
                        gap = y - y_end   #this is the gap between the current and previous y value
                        if gap == 0: #isolated groups already has been filled by a segment
                            isolated_groups[-1][1][1] = x_max    #the previous x_max (on same y coordinate) is superceded by current (larger x max)                     
                        elif gap < permissible_gap and gap>1: #theres missing y segment(s) continaing x values
                            for y_insert_fill in range(y_end + 1, y):
                                x_prev_min = isolated_groups[-1][1][0] #finds previous x values
                                x_prev_max = isolated_groups[-1][1][1]
                                isolated_groups.append([y_insert_fill,[x_prev_min, x_prev_max]]) #could do different x values if needed (eg. averages)
                        if gap > 0: #includes situations where gap > permissible_gap
                            isolated_groups.append([y,[x_min, x_max]])
                    except: #isolated groups is empty
                        isolated_groups = [[y,[x_min, x_max]]]
    return isolated_groups



def groups_to_dict(group, group_name = 'temp_group'):
    '''
    groups in the form of [y0, [x0_start, x0_end]][[y1[x1start,x1end]][y2[x2start,x2end]]] 
    this probably doesn't do much
    DELETE WITH FINALIZED PROGRAM?
    '''
    feature = {group_name: group}
    return feature

def mass_to_dict(mass): 
    '''
    mass is in the form of [ mass, [[y_min],[y_max coords],[x_min coords],[x_max coords]], mass_ID]
    converts a masses values to dictionary

    returns dictionary of coordinates

    params:
        refined_arr - array of image closed in around the specified mass
        mass is in the form of [ mass, [[y_min],[y_max coords],[x_min coords],[x_max coords]], mass_ID]
    '''
    return  convert_coordinates_to_dictionary(get_all_mass_coordinates(mass))


def masses_to_dict(item_name, masses, itemTypeLevel, order, color = [0,255,0]):
    '''
    item_name is a string of the variable name for masses, but singular
    returns names of coordinates
    '''
    for i, mass in enumerate(masses):
        itemTypeLevel[str(item_name)+str(i)] = mass_to_dict(mass)
        itemTypeLevel[str(item_name)+str(i)]['order'] = order
        itemTypeLevel[str(item_name)+str(i)]['color'] = color
    

def primer(img_arr, rearrange):
    '''
    runs preliminary look at image to get needed data
    '''
    #img_arr = convert_to_grey_scale(img_arr)
    #brightest_fraction = .35
    #get_brightest_fraction(img_arr) #outdated program, couldn't find in initial files

    t_img_arr = np.rot90(img_arr, 1)
    #compact_img_arr = np.array(compact_array(img_arr)) #returns list, consider filling, returning an array - compacting array prob doesn't add much
    #t_compact_img_arr = np.rot90(compact_img_arr, 1)

    # edges stored as lowest difference to the highest difference, the difference is the difference between two sampled pixels
    #       [[y0,[ [diff 1, x1] ,[diff 2, x2] ,[diff 3, x3],... [diff n, xn]][y1...]] (most typical)

    edges, jump = get_edges(img_arr)
    #t_edges is transverse edges
    t_edges, jump = get_edges(t_img_arr)
  
    '''
    #not much time difference with get_edges2
    t0 = time.time()
    edges, jump = get_edges2(img_arr)
    t_edges, jump = get_edges2(t_img_arr)
    t1= time.time()
    print('edges original', t1-t0)
    '''
    #consider using variance on brightest per row
    height = len(img_arr)

    #brightest_per_segment would be more efficient, but less clean in terms of coding.
    #brightest per segment could lead to regularizing segments, then skipping edges around extremes, to better preserve data
    #TODO: consider creating get_brightest_per_segment(edges)
    brightest_per_row = get_brightest_per_row(img_arr)
    t_brightest_per_row = get_brightest_per_row(t_img_arr)

    #bright_groups_by_y arranged from low y values to hi y values
    #   #bright_groups_by_y is in form of [y, [x_start, x_end]][[y[xstart,xend]][y2[x2start,x2end]]]
    y_groups_raw = edges_around_extremes(edges, brightest_per_row) #returns edges around brightest pixel
    x_groups_raw = edges_around_extremes(t_edges, t_brightest_per_row)

    y_groups = add_avg_brightness(img_arr, y_groups_raw) #appends the average brightness of the group, this function should be combined with the above
    x_groups = add_avg_brightness(t_img_arr, x_groups_raw)
    
    dim_fraction = .2 #this is the dimmest portion that will be deleted after the sort
    y_groups = delete_dim_sort(y_groups, dim_fraction) #sorts arrays by brightness, deletes dimmest, sorts back, TODO: improve efficiency
    x_groups = delete_dim_sort(x_groups, dim_fraction)    #could keep active tally of dimmest and location when avg brightness used
    #delete_dim_sort could be made more efficient by being merged with add_avg_brightness 

    
    for group in y_groups: #this deletes the average brightness of the group, TODO: consider excluding this, DELETE/REMOVE, also check downstream
        del(group[2])
    for group in x_groups:
        del(group[2])

    #get_masses --> masses are combined amount of adjacent (conecting on either side or top and bottom) pixels
        #in form of [combined_mass, [[h_min, w_h_min], [h_max, w_h_max], [h_w_min, w_min], [h_w_max, w_max]], mass_ID]
            #combined_mass is number of adjacent pixels
            #h corresponds to height (or y when axis_0 = 'y'), w corresponds to width, lower heights are higher up
            #w_h_min is width for the minimum height
        #y_groupings are returned with associated mass_ID (for error checking)
            #[[h,[w_start, w_end, mass_ID],[w_start, w_end, mass_ID]] - h for y, w for x
        #masses in from
            #[combined_mass, [[h_min, w_h_min], [h_max, w_h_max], [h_w_min, w_min], [h_w_max, w_max]], mass_ID]
    y_masses, y_groups = get_masses(y_groups)
    x_masses, x_groups = get_masses(x_groups)
    


    width = len(img_arr[1])

    #convert masses works for image array that has been rotated left
    y_x_masses = convert_masses(x_masses, width) #converts x_masses to be realigned to y values, makes x_masses moot
    
    #order_masses orders masses in order from largest to smallest, largest mass assumed to be prosthesis
    y_x_masses_by_mass = order_masses(y_x_masses) 
    y_masses_by_mass = order_masses(y_masses)
   

    mass_cutoff = 3 #masses are not always connected, this limits the amounts of masses that are combined #INSERT variable here
    if mass_cutoff < len(y_x_masses_by_mass) and mass_cutoff < len(y_masses_by_mass):
        y_x_masses_by_mass = y_x_masses_by_mass[0:mass_cutoff] 
        y_masses_by_mass = y_masses_by_mass[0:mass_cutoff]

    combo_masses = combine_masses(y_masses_by_mass, y_x_masses_by_mass ) #combines overlapping tranvserse masses
    

    for i in reversed(range(len(combo_masses)-1)):
        combo_masses[i] = mass_combine(combo_masses[i],combo_masses[i+1]) #combines overlapping masses

   
    #ordered_distances_coords arranges the distances between the extreme coordinates (inferior, superior, lateral, and medial)
        #only side to top and side to bottom distances (eg, not top to bottom or side to side)
    ordered_distances_coords = get_coords_distances(combo_masses[0])
    
    
    #on a regular prosthesis the distances between the coords will determine the orientation
    #coords is a dictionary of the different points within the prosthesis, e.g.
    prosthesis_coords = get_orientation(ordered_distances_coords)
    prosthesis_coords['mass'] = combo_masses[0][0]
    
    #finds the coords of the prosthesis
    top_side, component_side = get_sidedness(prosthesis_coords)
    
    #map_prosthesis reorients the prosthesis
    #-TODO:? write conversion program for x_groups and y_groups for increased efficiency
    '''
    if top_side != 'superior' or component_side != 'left': #probably more efficient for individual programs to rewrite masses
        img_arr = map_prosthesis(img_arr, top_side, component_side)
        if rearrange == True: #switch to prevent infinite recursion
            print('error, multiple rearrangements')
            return 
        rearrange = True
        img_arr, t_img_arr, coords, y_masses, y_x_masses, y_masses_by_mass, y_x_masses_by_mass, combo_masses,\
        y_groups, x_groups, edges, t_edges =  \
            primer(img_arr, rearrange)
    '''
    return img_arr, t_img_arr, prosthesis_coords, y_masses, y_x_masses, y_masses_by_mass, y_x_masses_by_mass, combo_masses,\
        y_groups, x_groups, y_groups_raw, x_groups_raw, edges, t_edges



def choose_image_for_img_arr(image_number):
    '''
    program to quickly try different images that are stored
    -stored images as array to reduce time to run the program (converting an image to an array)
    
    program designed around image number 2 - other images aren't documented, could produce errors
    TODO: make work with all images

    '''
    #img_arr could come in skewed, with a buffer, to get rid of bright edges

    if image_number == 1:
        img_arr = np.load('/Users/michael/Desktop/coding/implant recognition/image arrays/implant_arr.npy')
        filename = '/Users/michael/Desktop/coding/implant recognition/ortho implant images/depuy summit xray.jpg'
    elif image_number == 2:
        img_arr = np.load('/Users/michael/Desktop/coding/implant recognition/image arrays/s&n_anthology2.jpg.npy')
        filename = '/Users/michael/Desktop/coding/implant recognition/ortho implant images/s&n_anthology2.jpg'
    elif image_number == 3:
        img_arr = np.load('/Users/michael/Desktop/coding/implant recognition/image arrays/S&N+Anthology+1.0.npy')
        filename = '/Users/michael/Desktop/coding/implant recognition/ortho implant images/S&N+Anthology+1.0.png'

    elif image_number == 4:
        img_arr = np.load('/Users/michael/Desktop/coding/implant recognition/image arrays/depuy summit xray right side.jpg.npy')
        filename = '/Users/michael/Desktop/coding/implant recognition/ortho implant images/depuy summit xray right side.jpg'
    elif image_number == 5: #image has problem lengthwise, inferior end too distal on masses, low priority - works in horizontal
        img_arr = np.load('/Users/michael/Desktop/coding/implant recognition/image arrays/depuy summit xray right lengthwise.jpg.npy')
        filename = '/Users/michael/Desktop/coding/implant recognition/ortho implant images/depuy summit xray right lengthwise.jpg'

    
    elif image_number == 7:
        img_arr = np.load('right2.npy')
        filename = '/Users/michael/Desktop/coding/implant recognition/ortho implant images/right hip2.jpg'
    elif image_number == 8:
        img_arr = np.load('Users/michael/Desktop/coding/implant recognition/image arrays/r_secur-fit_advanced.npy')
        filename = '/Users/michael/Desktop/coding/implant recognition/ortho implant images//Right Secur-Fit Advanced.jpeg'
    elif image_number == 9:
        img_arr = np.load('/Users/michael/Desktop/coding/implant recognition/image arrays/right_hip_arr.npy')
        filename = '/Users/michael/Desktop/coding/implant recognition/ortho implant images/right hip.png'
    

    return img_arr, filename


def main_exec(logger): 
    '''
    Program takes an image array and isolates the brightest, or highest values, or intensities
    It creates spans along a single axis where are the adjacent pixels are above the intensity
    It creates masses from the adjoining spans (adjoining up and down and side to side)
    it assumes the largest mass is the mass of the prosthesis
    it takes the coordinates of the largest mass to determine the orientation of the prosthesis and bounds
    the array is reframed to fit the prosthesis, to reduce the array size
    the orientation of the prosthesis is then used to exclude features that aren't as useful for identification
        this includes the prosthesis head and shell
    the orientation is used:
        to map unique features for a data table
        or if the data table is already present: to match the prosthesis with a data table and determine the prosthesis type
    
    USEFUL INFO:
    coords is a dictionary holding points of prosthesis borders 
        -ASSUMPTION - xray perfectly in coronal plane, vertical orizontal aligned with y axis, and horizontal with x axis)
        -coords['x_superior'] is x axis point of superior point, coords['y_lateral'] is y axis interception of lateral most point


    USEFUL DEFINITIONS:
        superior - towards the top of the body
        inferior - towards the feet or lower along the body
        lateral - from side to side away from the centerline of the body
        medial - from side to side towards the centerline of the body

        extraction_hole - hole used to house insert that screws into place and pulls out a femoral replacement for revision surgery

    array definitions/variables within arrays
    mass in form of [mass, [[h_min, w_h_min], [h_max, w_h_max], [h_w_min, w_min], [h_w_max, w_max]], mass_ID]


    

    '''
    #image_number = 4
    #img_arr, filename = choose_image_for_img_arr(image_number)
    #could rewrite img_arr so that it comes with buffers already there.
    #keep seperate original array for error proofing
    #img_arr = img_arr_original.copy()

    items = {} #items is a dictionary that will save all different analysis indications

    #comse from (shell_exec($analyzeArray.' '. $directoryPath.' '.$ImplantItemsFileName.' '.$imgArr))
    dirPath = sys.argv[1] #within var/www/html/picAnalysis/
    #items_file = str(sys.argv[2]) #is 'itemsTemplate.json'





    img_arr = np.load(dirPath+'imgArr.npy') # DON'T CHANGE, GETS FUNKY WITH DIFFERENT VARIABLES previously was 'ImageArray', need np.load to function as numpy file
    



    rearrange = False #rearrange is set to true within primer to avoid infinite recursion within primer
    #primer is designed to find the orientation of the prosthesis
    #TODO: consider returning a dictionary with the below values instead of this/will be better, but may require additonal alterations
    
    
    img_arr, t_img_arr, prosthesis_info_diff, y_masses_diff, y_x_masses_diff, y_masses_by_mass_diff, y_x_masses_by_mass_diff, combo_masses_diff,\
        y_groups_diff, x_groups_diff,y_groups_raw_diff, x_groups_raw_diff, edges_diff, t_edges_diff = \
        primer(img_arr, rearrange)



    items = {
    "active": {
        "masses" :{},
        "features":{},
        "edges":{
            "y_edges_diff": {
                "values":[],
                "color": [255,0,0]},
            "t_edges_diff": {
                "values":[],
                "color": [255,0,0]}},
        "groups":{
            "y_groups_diff":{
                "values":[],
                "color": [255,255,0]},
            "x_groups_diff":{
                "values":[],
                "color": [255,255,0]},
            "y_min_inverse_groups_diff":{
                "values":[],
                "color": [255,255,0]},
            "y_groups_raw_diff":{
                "values":[], 
                "color": [255,255,0]},
            "x_groups_raw_diff":{
                "values":[],
                "color": [255,255,0]}
            
        }
    },
    "inactive":
    {
        "masses" :
        {
        },
        "groups":
        {
        },
        "features":
        {

        },
        "edges":
        {     
        },
        "axes":
        {
            
        }
    }
    }






    '''
        '''



    
   
    #probably a better way to do the below calculations - could incorporate it into estimates
    max_brightness_cutoff, min_brightness_cutoff = get_brightness_cutoff(img_arr, prosthesis_info_diff) #these are set to min and max values within coords
    
    #TODO: CHANGE NAME OF 
    #y_max_groups_surrounding = get_segments_within_mass(img_arr, max_brightness_cutoff, buffer = 4, axis_0 = 'y') 
    y_min_groups_surrounding = get_segments_within_mass(img_arr, min_brightness_cutoff, buffer = 4, axis_0 = 'y')
    #t_y_max_groups_surrounding = get_segments_within_mass(t_img_arr, max_brightness_cutoff, buffer = 4, axis_0 = 'y') #axis is y because the image is transverse
    #t_y_min_groups_surrounding = get_segments_within_mass(t_img_arr, min_brightness_cutoff, buffer = 4, axis_0 = 'y')
    
    #inverse masses are canuli and darkened points
    #y_max_inverse_groups = get_inverse_group(y_max_groups_surrounding)
    y_min_inverse_groups = get_inverse_group(y_min_groups_surrounding)
    #t_y_max_inverse_groups = get_inverse_group(t_y_max_groups_surrounding)
    #t_y_min_inverse_groups = get_inverse_group(t_y_min_groups_surrounding)

 
    #inverse masses are the masses within the prosthesis that have a reduced brightness, used for detecting canuli
    inverse_masses, inverse_groupings = get_masses(y_min_inverse_groups) #inverse groupings contains mass number
    inverse_masses = order_masses(inverse_masses) #orders the inverse masses by size

    #categorize inverse masses determines if inverse masses are prosthesis features and get the coordinates, then stores features in items
    categorize_inverse_masses(inverse_masses, items, prosthesis_info_diff)##1 return used to show added features to prosthesis_info_diff
    
    '''

    #RESUME HERE
    start_angle_groups, end_angle_groups = get_slope_groups(y_max_groups_surrounding)#not sure of purpose of this 


    large_span_group = isolate_large_spans(y_min_inverse_groups, )

    mass_cutoff = 3 #mass_cutoff is the number of masses that are seen
    

    #new cutoff value created to examine values within the prosthesis
    #TODO: create function that finds minimum values within the prosthesis by scanning y values
    cutoff = min(brightest_fraction * 200, 240)
  

    #large_span_group is refined from inverse_groups to exclude smaller spans (these can result from irregularities)
    #not sure if this program is helpful, works fine without it
    large_span_group = isolate_large_spans(inverse_groups, prosthesis_coords['width'])

  
    stem_axis_variables = {} #stem axis variables will contain geometrical information about the stem axis

    stem_axis_variables['y_inferior_end_point'] = prosthesis_coords['y_inferior'] #end point of stem
    stem_axis_variables['x_inferior_end_point'] = prosthesis_coords['x_inferior'] 
    feature_coords['stem_axis'] = stem_axis_variables
    
    print(feature_coords['extraction_hole'])
    if feature_coords['extraction_hole'] != {}:
        stem_axis_variables['x_superior_end_point'] = feature_coords['extraction_hole']['x_superior']#this is mid x on superior row, not great accuracy
        stem_axis_variables['y_superior_end_point'] = feature_coords['extraction_hole']['y_superior']
    
        stem_axis_variables['stem_axis_slope'] = (stem_axis_variables['y_inferior_end_point'] - stem_axis_variables['y_superior_end_point']) \
            /(stem_axis_variables['x_inferior_end_point'] - stem_axis_variables['x_superior_end_point'])
    #below is for proofing, that the slope is along the axis of the stem
        plt.axline((stem_axis_variables['x_superior_end_point'], stem_axis_variables['y_superior_end_point']), \
            (stem_axis_variables['x_inferior_end_point'], stem_axis_variables['y_inferior_end_point']))

    #pythagoreans theorum
        stem_axis_variables['stem_length'] = int(((stem_axis_variables['y_inferior_end_point'] - stem_axis_variables['y_superior_end_point'])**2 \
                + (stem_axis_variables['x_inferior_end_point'] - stem_axis_variables['x_superior_end_point'])**2)**.5)
    else:
        print('there is no extaction hole')

    
    '''
    edges_diff = convert_edge_format_to_group_format(edges_diff)##1
    t_edges_diff = convert_edge_format_to_group_format(t_edges_diff)

    state = "active"
    item_category = "values"

    itemType = "edges"
    items[state][itemType]['y_edges_diff'][item_category] = edges_diff
    items[state][itemType]['y_edges_diff']['color'] = [255,0,0]
    items[state][itemType]['t_edges_diff'][item_category] = t_edges_diff
    items[state][itemType]['t_edges_diff']['color'] = [255,0,0]


    itemType = "groups"

    '''
    logging.info('y_groups_diff[0:10] is ', y_groups_diff[0] )
    logging.info('y_groups_raw_diff[0:10] is ', y_groups_raw_diff[0] )
    '''
    items[state][itemType]['y_groups_raw_diff'][item_category] = y_groups_raw_diff
    items[state][itemType]['y_groups_raw_diff']['order'] = 0
    
    items[state][itemType]['x_groups_raw_diff'][item_category] = x_groups_raw_diff
    items[state][itemType]['x_groups_raw_diff']['order'] = 0
    
    items[state][itemType]['y_groups_diff'][item_category] = y_groups_diff 
    items[state][itemType]['y_groups_diff']['order'] = 1
    items[state][itemType]['x_groups_diff'][item_category] = x_groups_diff
    items[state][itemType]['x_groups_diff']['order'] = 1
    items[state][itemType]['y_min_inverse_groups_diff'][item_category] = y_min_inverse_groups
    items[state][itemType]['y_min_inverse_groups_diff']['order'] = 2


    itemType = 'masses'
    #masses_to_dict autocolor is fourth option, this is green [0,255,0]
    masses_to_dict('y_masses_diff', y_masses_diff, items[state][itemType], 2) 
    masses_to_dict('y_masses_by_mass_diff', y_masses_by_mass_diff, items[state][itemType], 3)
    masses_to_dict('y_x_masses_diff', y_x_masses_diff, items[state][itemType], 2) 
    masses_to_dict('y_x_masses_by_mass_diff', y_x_masses_by_mass_diff, items[state][itemType], 3)
    masses_to_dict('combo_masses_diff', combo_masses_diff, items[state][itemType], 4) 
    masses_to_dict('inverse_masses', inverse_masses, items[state][itemType], 3, [0,255,0]) 
    #FORMAT DON'T DELETE: masses_to_dict('', , items[state][itemType]) 
    #masses_to_dict(item_name, masses, itemTypeLevel, order, color = [0,255,0]):


    '''
    itemType = 'features'
    head_info_diff, shell_info_diff = get_head_shell_info(img_arr, prosthesis_info_diff, max_brightness_cutoff) #could rename coords
    head_info_diff['color'] = [255,0,255]
    shell_info_diff['color'] = [255,255,0]
    prosthesis_info_diff['color'] = [255,0,255]
    #items[state][itemType]['head_info_diff'] = head_info_diff
    items[state][itemType]['shell_info'] = shell_info_diff
    items[state][itemType]['shell_info']['order'] = 0
    items[state][itemType]['prosthesis_info'] = prosthesis_info_diff 
    items[state][itemType]['prosthesis_info']['order'] = 0
    items[state][itemType]['extraction_hole'] = head_info_diff
    items[state][itemType]['extraction_hole']['order'] = 1
    '''
    

    with open(dirPath + 'items.json', "w") as outfile:
        json.dump(items, outfile)

    

    
    print('KEEP THIS LINE TO RETURN A SUCCESSFUL OPERATION TO PHP')
    
    '''
    TODO:

    -progam that creates a list of pointers so sort isn't used for reordering
    -program that checks for smooth edges of prostheisis
    -program that gets the slop of prosthesis edges
    -adjust for variations in extraction hole (S&N)
    -create program that runs through brightnesses to find fitting form
        -could get easy start by analyzing range of intensity values within the image array
    -consistency in describing programs?
    -account for screws anchoring acetabular shell (alter distances between coordinates)
    -account for program not working if low and high factors for brightness
    -account for brigthness refinement for threaded extraction hole
    -create a function to determine brightest fraction or cycle through brightest fractions
    -detect edges - consider using edge detection matricies
        -AND writing programs to skip adjoining x pixels, so sharper contrasts at prosthesis edge
        -this would sample from far wtihin the prosthesis and put the y matricies next to y matricies from far outside prosthesis
    -do bilateral prosthesis analysis
    -verify that it works with screws, extra hardware
    -make work with poor quality x-rays - non uniform light - spots brighter than prosthesis
    -ensure reorienting program works, so medial lateral, x,y always align in same direction
    -- less time consuming if array not rearranged, but medial/lateral definitions are, but prob not significant
    -create edge detection for base of neck features/corners
    -give the size of the prosthesis?

    EXCLUDED PROGRAMS: (see isolate_implant_scraps.py for excluded programs)
    -programs designed to exclude irregular bright segments,
        get_ordered_intensity_variance_roster
        refine_spans_del_extremes

        refined_inverse_groups = get_isolated_groups(superior_bounds, inferior_bounds, medial_bounds, lateral_bounds, large_span_group)




    COME BACK TO?
    #head info describes the location of the femoral head and the coordinates
    shell_info = get_shell_info(coords) 

    coords['shell_info'] = shell_info

    exclude_shell(img_arr, shell_info)


    #dark_edge_groups = edges_within_brightest(img_arr, y_groups, coords, number_of_diffs = 12, jump_fraction = 0)
    #y_dark_edge_groups = edges_within_brightest(t_img_arr, y_groups, coords, number_of_diffs = 4, jump_fraction = 0)

    #inverse_edges = get_inverse_edges(img_arr, dark_edge_groups)

    #darkest_segments = get_darkest_segments(img_arr, dark_edge_groups)
    #y_darkest_segments = get_darkest_segments(t_img_arr, y_dark_edge_groups)

    #mark_groupings(img_arr, darkest_segments, green)
    #mark_groupings(t_img_arr, y_darkest_segments, blue)

      #refined groups is not neccessary, will reduce array size, but makes for more conversions etc...
    #refined_inverse_groups could overide inverse_groups, but seperate variable names could be helpful for error proofing
    #refined_inverse_groups = get_isolated_groups(superior_bounds, inferior_bounds, medial_bounds, lateral_bounds, large_span_group)
    



    #focus_array reduces and frames the array around the prosthesis and cuts out the prosthesis head and shell
    #only values within the prosthesis remain within arr_reduced
    #new variables (eg. arr_reduced) are named in place of old (eg. img_arr) throughout program
    #   this is done for error proofing / easy side by side comparisons, could be changed on final program
    #DELETE FOCUS ARRAY? arr_reduced, reduction_area, prosthesis_coords = focus_array(img_arr, cutoff, brightest, coords, head_info)
    

    
    #below are colors to highlight the prosthesis
    green = [0,255, 0]
    blue = [0,0,255]
    red = [255,0,0]
    purple = [255,0,255]
    yellow = [255,255,0]

    





    '''


def main():
    '''
    consider renaming error shell
    better to run outside of this code, but potential complexity with passing sys.arg between python files.
    '''
    logging.basicConfig(filename="analyze_array.log", format='%(levelname)s:%(asctime)s %(message)s', filemode='w')
    logger = logging.getLogger()
    logger.setLevel(logging.NOTSET)

    try:
        main_exec(logger)
    except Exception as e:
        logging.exception('Unexpected exception! %s', e)



if __name__ == '__main__':
    main()
