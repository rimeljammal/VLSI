#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 13 20:37:08 2020

@author: rim
"""

import numpy as np

class Node:
    
    def __init__(self, var_name):
        self.var_name = var_name
        
    def printNode(self):
        print(self.var_name)
        
        
n1 = Node('n1')
n2 = Node('n2')
n3 = Node('n3')
n4 = Node('n4')
n5 = Node('n5')
        
        
main_graph = {"n1": [n2],
              "n2": [n1, n3],
              "n3": [n2, n4],
              "n4": [n3, n5],
              "n5": [n4]}

right_graph = {"n2": [n1, n3],
               "n4": [n3, n5], 
               "n5": [n4]}

left_graph = {"n1": [n2],
              "n3": [n2, n4]}

ratio_factor = 0.375

areas = {"n1": 2,
        "n2": 4,
        "n3": 1,
        "n4": 4,
        "n5": 5}


def getBalanceCriterion():
    sum_areas = sum(areas.values())
    max_area = max(areas.values())
    
    left_side = float(ratio_factor * sum_areas - max_area)
    right_side = float(ratio_factor * sum_areas + max_area)
    
    area_A = 0
    
    for value in left_graph:
        area_A += areas[value]
        
    if left_side <= area_A and area_A <= right_side:
        print('Balance criterion met:', area_A)
        return True
    else:
        print('Balance criterion violated :(')
        return False

def getGain():
    
    gain_map = {}
    
    for key, values in main_graph.items():
        same = 0
        out = 0
        if key in right_graph:
            for v in right_graph[key]:
                if v.var_name in right_graph:
                    same -= 1
                else:
                    out += 1
            gain_map[key] = same + out
        if key in left_graph:
            for v in left_graph[key]:
                if v.var_name in left_graph:
                    same -= 1
                else:
                    out += 1
            gain_map[key] = out + same
                    
    return gain_map
    
    
def fid_math_algo():
    iterations = {}
    fixed = {}
    print('i =', 0)
    print('In partition A: ', left_graph.keys())
    print('In partition B: ', right_graph.keys())
    new_gain_map = getGain()
    max_gain = max(new_gain_map.items(), key = lambda x: x[1])[0]
    max_gain_value = max(new_gain_map.items(), key = lambda x: x[1])[1]
    print('Gains:', new_gain_map)
    print('Max gain:', max_gain)
    
    i = 1
    
    while len(fixed) != len(main_graph):
        print('\n i =', i)
        if max_gain not in fixed and getBalanceCriterion():
            fixed[max_gain] = max_gain_value
            if max_gain in left_graph:
                right_graph[max_gain] = left_graph[max_gain]
                del left_graph[max_gain]
            elif max_gain in right_graph:
                left_graph[max_gain] = right_graph[max_gain]
                del right_graph[max_gain]
            
            new_gain_map = getGain()
            print('In partition A: ', left_graph.keys())
            iterations[str(i)] = list(left_graph.keys())
            print('In partition B: ', right_graph.keys())
            print('Gains:', new_gain_map)
            for v in fixed:
                del new_gain_map[v]
            if len(new_gain_map) != 0:
                max_gain = max(new_gain_map.items(), key = lambda x: x[1])[0]
                max_gain_value = max(new_gain_map.items(), key = lambda x: x[1])[1]
                print('Max gain (not in fixed cells):', max_gain)
            
        i += 1
        
    G = getCumulativeGain(fixed)
    max_elements = [i for i, x in enumerate(G) if x == max(G)]
    print('\n Cumulative gain:', G)
    
    if len(max_elements) == 1:
        print('Best was at iteration:', max_elements[0], 'with G =', G[0])
    else: 
        print('Iterations with equal max gain:', max_elements)
        max_area = -99
        best_iteration = 0
        for v in max_elements:
            area = getAreaA(iterations[str(v)])
            if area > max_area:
                best_iteration = v
                max_area = area
        print('Iteration', str(v), 'is selected due to its better area:', max_area)
        print('In partition A: ', iterations[str(v)])
        print('In partition B: ', set(list(main_graph)).difference(iterations[str(v)]))
        
        
    
def getCumulativeGain(fixed):
    G = []
    cumulative_sum = 0
    
    for i in main_graph:
        cumulative_sum += fixed[i]
        G.append(cumulative_sum)
    
    return G

def getAreaA(elements):
    area_A = 0
    
    for v in elements:
        area_A += areas[v]
        
    return area_A

#################### Calling the algorithm ####################
    
fid_math_algo()
