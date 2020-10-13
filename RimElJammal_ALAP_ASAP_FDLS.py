

######################## Classes used for the ASAP and ALAP implementation ########################

class Node:
    predecessors = []
    time_stamp = 0
    
    def __init__(self, var_name, predecessors, successors, time_stamp, op_type, scheduled):
        self.var_name = var_name
        self.predecessors = predecessors
        self.successors = successors
        self.time_stamp = time_stamp
        self.op_type = op_type
        self.scheduled = scheduled
        
    def printNode(self):
        print(self.var_name, self.predecessors, self.time_stamp, self.op_type, self.scheduled)
        

class Predecessor:
    def __init__(self, var_name, time_stamp):
        self.var_name = var_name
        self.time_stamp = time_stamp
        
    def printPredecessor(self):
        print(self.var_name, self.time_stamp)
        
class Successor:
    def __init__(self, var_name, time_stamp):
        self.var_name = var_name
        self.time_stamp = time_stamp
        
    def printSuccessor(self):
        print(self.var_name, self.time_stamp)

###################################################################################################

import re, math

asap_graph = {}

op_succ = {}

ops = []

def parseFile(filename):

    file = open(filename)
    lines = file.readlines()

    operators = []

    for index, line in enumerate(lines):
        list = line.split(':=')
        left_side = list[0].strip()
        right_side = list[1].strip()
        right_side = right_side.replace(" ", "")
        op = getOperator(right_side, index)
        if getPredecessorsLength(right_side) == 0:
            time_stamp = 1
            scheduled = True
        else:
            time_stamp = 0
            scheduled = False 
        preds = getPredecessors(left_side, right_side)
        operators.append(op)
        if 'outport' not in left_side and '_o' not in left_side:
            n = Node(left_side, preds, [], time_stamp, op, scheduled)
            ops.append(n)
            asap_graph[left_side] = time_stamp
    return [asap_graph, operators]

def getOperator(line, index):
    if len(line.split('*')) > 1:
        return '*'
    if len(line.split('+')) > 1:
        return '+'
    if len(line.split('-')) > 1:
        return '-'
    
def getPredecessorsLength(right_side):
    variables = re.split('[+ * -]', right_side)
    preds = []
    for var in variables:
        if var in asap_graph:
            preds.append(var)
    return len(preds)
    
def getPredecessors(left_side, right_side):
    variables = re.split('[+ * -]', right_side)
    preds = []
    for var in variables:
        if var in asap_graph:
            pred = Predecessor(var, asap_graph[var])
            preds.append(pred)
            if var not in op_succ:
                op_succ[var] = []
            if 'outport' in left_side and var not in op_succ:
                op_succ[var].append('')
            if '_o' in left_side and var not in op_succ:
                op_succ[var].append('')
            if 'outport' not in left_side and '_o' not in left_side:
                op_succ[var].append(left_side)
    return preds

####################################### ASAP and ALAP ###############################################

def asap_algo(asap_graph):

    scheduled = dict.fromkeys(asap_graph)

    for node in ops:
        sched = True
        for pred in node.predecessors:
            if not scheduled[pred.var_name]:
                sched = False
        if sched:
            scheduled[node.var_name] = True
        if sched and node.time_stamp != 1:
            max_time_stamp = 1
            for i in node.predecessors:
                if max_time_stamp < asap_graph[i.var_name]:
                    max_time_stamp = asap_graph[i.var_name]
            asap_graph[node.var_name] = max_time_stamp + 1
            node.time_stamp = max_time_stamp + 1
            scheduled[node.var_name] = True
            
def alap_algo(asap_graph):
    alap_graph = dict(asap_graph)
    time_stamps = alap_graph.values()
    max_time_stamp = max(time_stamps)
    
    scheduled = dict.fromkeys(alap_graph)
    has_no_succ = getSuccList()

    for node in ops:
        if node.var_name in has_no_succ:
            # node.time_stamp = max_time_stamp
            alap_graph[node.var_name] = max_time_stamp
            scheduled[node.var_name] = True
            
    for i in range(0, len(asap_graph) - 1):
        for node in ops:
            sched = True
            for pred in node.predecessors:
                if not scheduled[pred.var_name]:
                    sched = False
            if sched:
                scheduled[node.var_name] = True
            if sched and node.time_stamp != max_time_stamp:
                min_time_stamp = max_time_stamp
                if node.var_name in op_succ:
                    node.successors = op_succ[node.var_name]
                    for succ in node.successors:
                        if succ in alap_graph:
                            if min_time_stamp > alap_graph[succ]:
                                min_time_stamp = alap_graph[succ]
                            alap_graph[node.var_name] = min_time_stamp - 1
                            # node.time_stamp = min_time_stamp - 1
                            scheduled[node.var_name] = True

    return alap_graph

###################################################################################################
            
def getSuccList():
    has_no_succ = []
    
    for key, values in op_succ.items():
        if len(values) == 0:
            has_no_succ.append(key)

    return has_no_succ

def getMaxTimeStamp(alap_graph):
    
    time_stamps = alap_graph.values()
    max_time_stamp = max(time_stamps)
    
    return max_time_stamp


def getMobility(asap_graph, alap_graph):

    mobility_map = {}
    time_stamps = alap_graph.values()
    max_time_stamp = max(time_stamps)

    for key in asap_graph:
        difference = abs(asap_graph[key] - alap_graph[key])
        mobility_map[key] = difference

    return mobility_map

def getProbability(mobility_map):
    probability_map = {}

    for key in mobility_map:
        if mobility_map[key] != 0:
            prob = format(float(1 / (mobility_map[key] + 1)), '.1f')
            probability_map[key] = prob
        else:
            probability_map[key] = 1

    return probability_map

def getTypeDistribution(probability_map):
    type_dist = {}
    
    for i in range(1, getMaxTimeStamp(alap_graph) + 1):
        for j in ops:
            if j.time_stamp == i and j.var_name in probability_map:
                if str(i) in type_dist:
                    type_dist[str(i)] += float(probability_map[j.var_name])
                else:
                    type_dist[str(i)] = float(probability_map[j.var_name])

    return type_dist


def fdls(asap_graph, alap_graph):
    mobility_map = getMobility(asap_graph, alap_graph)
    probability_map = getProbability(mobility_map)
    type_dist = getTypeDistribution(probability_map)

    print("Mobility map:\n", mobility_map)
    print("Probability: \n", probability_map)
    print("Type Distribution: \n", type_dist)

    return type_dist


def printAnswer(graph):
    for key, value in graph.items():
        print(key, 'at time stamp:', value)

parseFile('/Users/rim/Desktop/Fall 2020/Algorithms for VLSI/assignment 1/data/diffeq.dfg')
asap_algo(asap_graph)
print("ASAP:\n",asap_graph)
alap_graph = alap_algo(asap_graph)
print("##############################################################################################################")
print("ALAP:\n", alap_graph)
print("##############################################################################################################")
print("FDLS:")
fdls(asap_graph, alap_graph)