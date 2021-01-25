#!/usr/bin/env python
# coding: utf-8

# In[1]:

from matplotlib import pyplot as plt
import cv2 as cv
import numpy as np
import random
import math

np.set_printoptions(threshold=np.inf)

plt.rcParams.update({'font.size': 20})
plt.rcParams["figure.figsize"] = (200, 30)

# In[2]:


"""
First attempt was to analyze the photo using edge detection, 
try to construct lines from the result, then deduce rectangles.
However after trying different approaches and parameters, 
it was realised that the difficulty in parsing the result is beyond the level for this task. 
Therefore I decided to look for a different approach. 
An intermediate result is shown in the next cell for the line detection approach.
"""

# In[4]:


img = cv.imread('boxes2.jpg')

# resize image for better better detection
image_scale = 5
img = cv.resize(img, (img.shape[1] * image_scale, img.shape[0] * image_scale))

gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
plt.imshow(gray)
plt.show()

ret, thresh1 = cv.threshold(gray, 200, 255, cv.THRESH_BINARY)

thresh1 = cv.bitwise_not(thresh1)

plt.imshow(thresh1)
plt.show()

edges = thresh1
# trials were made to see does edge detection improves the result
# edges = cv2.Canny(thresh1, threshold1=0, threshold2=500, apertureSize = 3)

line_image = np.copy(img) * 0

# More or less magic numbers, with correlation to the resolution of the image
# these numbers are decided by trials and error
rho = 1
theta = np.pi / 180 * 1
minLineLength = 80
maxLineGap = 4
threshold = 80
lines = cv.HoughLinesP(edges, rho, theta, threshold, np.array([]), minLineLength, maxLineGap)

print_scale = 1
line_image = cv.resize(line_image, (line_image.shape[1] * print_scale, line_image.shape[0] * print_scale))
for line in lines:
    for x1, y1, x2, y2 in line:
        cv.line(line_image, (x1 * print_scale, y1 * print_scale), (x2 * print_scale, y2 * print_scale),
                (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), 5)

plt.imshow(line_image)
plt.show()

# In[5]:


"""
Although the result is quite obvious for human eyes, I am unable to find a simple and clear way to parse the result. 
An another approach is taken, in reference to a sample given by the opencv distribution.
"""


# In[6]:


# reference to the open cv example of square.c, with minor parameters changes

def angle_cos(p0, p1, p2):
    d1, d2 = (p0 - p1).astype('float'), (p2 - p1).astype('float')
    return abs(np.dot(d1, d2) / np.sqrt(np.dot(d1, d1) * np.dot(d2, d2)))


def find_rect(img):
    # img = cv.GaussianBlur(img, (5, 5), 0)
    rect = []
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    thresh = cv.threshold(gray, 150, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)[1]
    _, contours, _hierarchy = cv.findContours(thresh, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        cnt_len = cv.arcLength(cnt, True)
        cnt = cv.approxPolyDP(cnt, 0.02 * cnt_len, True)
        if len(cnt) == 4 and cv.contourArea(cnt) > 100 and cv.isContourConvex(cnt):
            cnt = cnt.reshape(-1, 2)
            max_cos = np.max([angle_cos(cnt[i], cnt[(i + 1) % 4], cnt[(i + 2) % 4]) for i in range(4)])
            if max_cos < 0.1:
                rect.append(cnt)
    return rect


# In[7]:


boxes1 = cv.imread('boxes1.jpg')
boxes2 = cv.imread('boxes2.jpg')
table1 = cv.imread('table1.jpg')

line_image_boxes1 = np.copy(boxes1) * 0
line_image_boxes2 = np.copy(boxes2) * 0
line_image_table1 = np.copy(table1) * 0

rect_boxes1 = find_rect(boxes1)
cv.drawContours(line_image_boxes1, rect_boxes1, -1, (0, 255, 0), 3)
rect_boxes2 = find_rect(boxes2)
cv.drawContours(line_image_boxes2, rect_boxes2, -1, (0, 255, 0), 3)
rect_table1 = find_rect(table1)
cv.drawContours(line_image_table1, rect_table1, -1, (0, 255, 0), 3)

plt.imshow(line_image_boxes1)
plt.show()
plt.imshow(line_image_boxes2)
plt.show()
plt.imshow(line_image_table1)
plt.show()

# In[ ]:


"""
The result is better than the previous approach in terms of simplicity.
But just two problems
Problem 1: the tiny boxes in boxes.jpg (top left and bottom right corner) is undetected. I beleive this can be solved by changing
certain parameters. But with the limited time frame, I am unable to figure out the correct parameter
Problem 2:
some boxes will contribute more than one entries in the contours list.
For each boxes, the inner contour is definitely captured. But for some boxes, the outer contour is also captured.
The following code is to eliminate these outer contour
"""

# In[109]:


print(len(rect_table1))

# In[45]:


"""
Outer Rectangle Elimination Algorithm
Paremeters:
   merging threshold: the distance in which points will be merged (contribute to the thickness of the line)
   slope threshold: the difference in which the corner is considered as same type of corner (contribute to the inaccuracy of image processing)

Idea:
   If there is rectangle which all of its 4 corner are corners of another rectangles, then this rectangle is an outer rectangle
   and should not be count as a box (this definition might not be true in all situations, 
   please refer to the last comment for elaboration)

Defination of same corner:
   Given two corner c1 and c2
   The x y coordinates of the point in c1 and the x y concatenates of the point in c2 should within the merging threshold respectively
   The combination of two slope in the corner should be approx the same (the approx is determined by slope threshold),
   note that the ordering does not matter
   The direction of the two adjacent line should be the same too

Process:
   1.Initiate list
   2.For each corner point in Countours:
        find if there is corner point in the list has the same corner, if yes, marked as merged and insert, if not, just insert
   3.After all corner point has been looped, count rectangles which at least 1 of its corner not marked as merged
"""


# In[152]:


class list_element:
    def __init__(self, x, first_y, first_rectangle_index, first_corner_index):
        self.x = x
        self.corners = [[first_y, first_rectangle_index, first_corner_index]]

    def new_rectangle(self, y, rectangle_index, corner_index):
        self.corners.append([y, rectangle_index, corner_index])
        return

    # helper function for checking if same corner
    def same_corner(self, corner, compared_corner, slope_threshold):
        #         print(corner)
        #         print(compared_corner)
        # have same slope or not (only need to check one against one as rectangle guarantee right angle)
        if abs(corner[1] - compared_corner[1]) < slope_threshold:
            # check orientation
            if corner[0] == compared_corner[0] and corner[2] == compared_corner[2]:
                return True
        # if reversed
        elif abs(corner[3] - compared_corner[1]) < slope_threshold:
            if corner[0] == compared_corner[2] and corner[2] == compared_corner[0]:
                return True
        return False

    # return 0 if not within, return 1 if within x but not y or within x and y but not same corner,
    # return 2 if within x and y and same corner

    def within(self, x, y, corner_index, threshold, slope_threshold):
        if (abs(self.x - x) < threshold):
            # there is definately a faster algorithm for searching closest element,
            # but as performance is not the first priority here, just taking the brute force way to keep it simple
            for corner in self.corners:
                if (abs(corner[0] - y) < threshold) and self.same_corner(corner[2], corner_index, slope_threshold):
                    return 2
            return 1
        else:
            return 0

    def elem_print(self):
        print('x: ', self.x)
        for corner in self.corners:
            print('y: ', corner[0], 'rect_index: ', corner[1], 'corner_index: ', corner[2])
        return

    def unique_rect(self):
        rect = []
        for corner in self.corners:
            rect.append(corner[1])
        return set(rect)


def list_insert(node_list, node, rectangle_index, corner_index, merging_threshold, slope_threshold):
    # loop at x first, find if there is element within merging_threshold, currently go for bottom limit, may change to closest later on
    within_exist = False
    for elem in node_list:
        result = elem.within(node[0], node[1], corner_index, merging_threshold, slope_threshold)
        if result == 1:
            within_exist = True
            elem.new_rectangle(node[1], rectangle_index, corner_index)
        elif result == 2:
            #             print('merged!')
            #             elem.elem_print()
            #             print(node)
            #             print(corner_index)
            within_exist = True
    # node is not merged
    if not within_exist:
        new_node = list_element(node[0], node[1], rectangle_index, corner_index)
        node_list.append(new_node)
    return


def slope(x1, y1, x2, y2):
    if x1 == x2:
        return np.Inf
    return (y2 - y1) / (x2 - x1)


def orientation(x1, y1, x2, y2, merging_threshold):
    ori = [None, None]
    xdiff = x2 - x1
    if abs(xdiff) < merging_threshold:
        ori[0] = 'same'
    elif xdiff > 0:
        ori[0] = 'pos'
    else:
        ori[0] = 'neg'

    ydiff = y2 - y1
    if abs(ydiff) < merging_threshold:
        ori[1] = 'same'
    elif ydiff > 0:
        ori[1] = 'pos'
    else:
        ori[1] = 'neg'
    return ori


def count_rect(contours, merging_threshold, slope_threshold):
    rect_index = 0
    corner_index = 0
    node_list = []
    # to tackle an exception case
    contours.sort(key=cv.contourArea)
    #     print(contours)
    for contour in contours:
        corner_index = 0
        for node in contour:
            pre_slope = slope(node[0], node[1], contour[corner_index - 1][0], contour[corner_index - 1][1])
            pre_ori = orientation(node[0], node[1], contour[corner_index - 1][0], contour[corner_index - 1][1],
                                  merging_threshold)
            nxt_slope = []
            if corner_index == len(contour) - 1:
                # I believe there is a lamda for such purpose, will need further research if refactor
                nxt_slope = slope(node[0], node[1], contour[0][0], contour[0][1])
                nxt_ori = orientation(node[0], node[1], contour[0][0], contour[0][1], merging_threshold)
            else:
                nxt_slope = slope(node[0], node[1], contour[corner_index + 1][0], contour[corner_index + 1][1])
                nxt_ori = orientation(node[0], node[1], contour[corner_index + 1][0], contour[corner_index + 1][1],
                                      merging_threshold)
            # print(pre_ori,math.atan(pre_slope),nxt_ori,math.atan(nxt_slope))
            list_insert(node_list, node, rect_index, [pre_ori, math.atan(pre_slope), nxt_ori, math.atan(nxt_slope)],
                        merging_threshold, slope_threshold)
            corner_index += 1
        rect_index += 1

    #     for node in node_list:
    #         node.elem_print()
    count_result = []

    # getting unique values in list
    for elem in node_list:
        count_result.extend(elem.unique_rect())
    count_result = set(count_result)
    return len(count_result)


# boxes1.jpg has a thinner line, therefore a smaller merging_threshold
print('boxes1.jpg box count:', count_rect(rect_boxes1, 5, 1))
print('boxes2.jpg box count:', count_rect(rect_boxes2, 10, 1))
print('table1.jpg box count:', count_rect(rect_table1, 10, 1))

# In[ ]:


"""
There is one thing which is worth exploring. In my assumption, a rectangle has to at least one of its corners not
the same corner as another rectangle to be a box. This might not be true in some situation, depends on the defination of 
what is a box. But in the limited timeframe, I will keep it this way as this is sufficient for the given samples.
"""
