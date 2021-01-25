#!/usr/bin/env python
# coding: utf-8

# In[3]:

import numpy as np

# original question


# Finish A* search function that can find path from starting point to the end
# The robot starts from start position (0,0) and finds a path to end position (4, 5)
# In the maze, 0 is open path while 1 means wall (a robot cannot pass through wall)
# please write your heuristic matrix, and fill unvisited position with -1,
# cost of each movement is 1, as shown in the example below

# example result:
# [[0, -1, -1, -1, -1, -1],
#  [1, -1, -1, -1, -1, -1],
#  [2, -1, -1, -1, -1, -1],
#  [3, -1,  8, 10, 12, 14],
#  [4,  5,  6,  7, -1, 15]]

# the maze robot need to find a path
maze = [[0, 1, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0]]

start = [0, 0]  # starting position
end = [len(maze) - 1, len(maze[0]) - 1]  # ending position
cost = 1  # cost per movement

move = [[-1, 0],  # go up
        [0, -1],  # go left
        [1, 0],  # go down
        [0, 1]]  # go right

# 1. make your own heuristic
heuristic_original = [[0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0]]

# heretic for each node = abs(End[0] - Node[0]) + abs(End[1] - Node[1])
# start and end has no cost
heuristic = [[0, 8, 7, 6, 5, 4],
             [8, 7, 6, 5, 4, 3],
             [7, 6, 5, 4, 3, 2],
             [6, 5, 4, 3, 2, 1],
             [5, 4, 3, 3, 1, 0]]

# In[4]:


# reference to https://github.com/BaijayantaRoy/Medium-Article/blob/master/A_Star.ipynb, with modification


class Node:

    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        self.g = 0
        self.h = 0


def draw_path(result, node, seq):
    count = seq
    if node.parent is not None:
        count = draw_path(result, node.parent, count)
    result[node.position[0]][node.position[1]] = count
    return count + 1


def search(maze, cost, start, end, heuristic):
    start_node = Node(None, tuple(start))
    end_node = Node(None, tuple(end))

    yet_to_visit_list = [start_node]
    visited_list = []

    no_rows, no_columns = np.shape(maze)

    while len(yet_to_visit_list) > 0:

        current_node = yet_to_visit_list[0]
        current_index = 0
        for index, item in enumerate(yet_to_visit_list):
            if item.g + item.h < current_node.g + current_node.h:
                current_node = item
                current_index = index

        yet_to_visit_list.pop(current_index)
        visited_list.append(current_node)

        if current_node.position == end_node.position:
            result = [[-1 for i in range(no_columns)] for j in range(no_rows)]
            draw_path(result, current_node, 0)
            return result

        children = []

        for new_move in move:

            new_position = (current_node.position[0] + new_move[0], current_node.position[1] + new_move[1])

            if (new_position[0] > (no_rows - 1) or
                    new_position[0] < 0 or
                    new_position[1] > (no_columns - 1) or
                    new_position[1] < 0):
                continue

            if maze[new_position[0]][new_position[1]] != 0:
                continue

            new_node = Node(current_node, new_position)
            children.append(new_node)

        for child in children:

            if len([visited_child for visited_child in visited_list if visited_child == child]) > 0:
                continue

            child.g = current_node.g + cost
            child.h = heuristic[current_node.position[0]][current_node.position[1]]

            if len([i for i in yet_to_visit_list if child.position == i.position and child.g > i.g]) > 0:
                continue

            yet_to_visit_list.append(child)

    return 'no path found'


path = search(maze, cost, start, end, heuristic)
if type(path) == 'str':
    print(path)
else:
    for row in path:
        print(row, '\n')

# In[ ]:
