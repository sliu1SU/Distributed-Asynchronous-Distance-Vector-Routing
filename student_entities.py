"""
CPSC 5510, Seattle University, Project #3

This assignment includes extra credit. Please note that 2 versions common_update and
common_link_cost_change are implemented. Both versions are functional.
Regular version does not use routing table (@ a given node, for each destination in the graph,
where the next hop (must be one of the neighbors) should be).
Version #2 does use routing table.
By default, regular version will be called to execute the assignment. However, if you wish to
try out version #2, please simply go into each class to call the corresponding version #2 of
functions.
COST/graph is included as global variable to reduce the length of codes. Basically, this allows
me to move most initialization codes to common_init. Please note that every node ONLY has
access to its corresponding cost vector (DV). For example, node 0 ONLY has access to cost[0]!

NOTE: rarely, when version #2 is executed, node0 final answer when link cost is changed from
20 to 1 (at the bottom of the console output) can be printed in the wrong order. This is due
to the randomness of Async nature of this algo based on my observation and debugging.
To be specific, node0's right answer can be printed before the last node0 appearance on the
console output. This happens very rarely and if it does happen, feel free to rerun the program.
This will always fix the problem. Again, this is due to the randomness of Asyn, NOT because of
any error associated with the implementation.

:Author: Sizhe Liu # FIXME fill in _your_name
:Version: s23
"""

# YOU MAY NOT ADD ANY IMPORTS
from entity import Entity
from student_utilities import to_layer_2

# include cost here to simplify code - can move more code to common_init, reduce
# repeated codes in Entity classes
INF = float('inf')
cost = [[0, 1, 3, 7], [1, 0, 1, INF], [3, 1, 0, 2], [7, INF, 2, 0]]


def common_init(self):
    """
    You may call a common function like this from your individual __init__ 
    methods if you want.
    """
    # pass  # FIXME (optional)
    # initialize distance table
    self.distance_table[self.node] = cost[self.node].copy()

    # initialize neighbour list
    for i in range(len(self.distance_table[self.node])):
        number = self.distance_table[self.node][i]
        if number == 0 or number == INF:
            continue
        self.neighbourList.append(i)

    # initialize routing table
    for i in range(4):
        if i == self.node:
            self.routingTable[i] = self.node
        elif i in self.neighbourList:
            self.routingTable[i] = i
        else:
            self.routingTable[i] = -1

    # send the initial DV to all neighbours
    for i in range(len(self.neighbourList)):
        # source node #, dest node#, DV
        to_layer_2(self.node, self.neighbourList[i], self.distance_table[self.node])


def common_update2(self, packet):
    """
    You may call a common function like this from your individual update
    methods if you want.
    """
    # pass  # FIXME
    print(f'node {self.node}: update from {packet.src} received')

    # update dist table with the incoming DV
    self.distance_table[packet.src] = packet.mincost.copy()

    # remember old DV
    oldDV = self.distance_table[self.node].copy()

    # check routing table - if next hop is packet.src - revert entry to default cost!
    # this is because if the cost of a neighbor is changed, a node can no longer rely
    # on that neighbor as the next hop, re-computation and verification are required
    for i in self.routingTable:
        if self.routingTable[i] == packet.src:
            # overwrite this entry to the default value!
            self.distance_table[self.node][i] = cost[self.node][i]
            # revert routing table entry to default
            if i in self.neighbourList:
                self.routingTable[i] = i
            else:
                # if this destination node is not a neighbor - set to -1
                self.routingTable[i] = -1

    # compute the shortest distance from this node to every other node in the graph
    # only use the newly-received DV (info) to compute
    for i in range(len(self.distance_table[self.node])):
        if i == self.node:
            continue
        current = self.distance_table[self.node][i]
        new = self.distance_table[self.node][packet.src] + self.distance_table[packet.src][i]

        # this portion is for routing table update - needed for extra credit
        if new < current:
            # update next hop in routing table
            # if self.node going to the src node need to go through another
            # node to get to the src node, next hop to node i == next hop to the src node
            # otherwise, next hop is the src node itself
            if self.routingTable[packet.src] == packet.src:
                self.routingTable[i] = packet.src
            else:
                self.routingTable[i] = self.routingTable[packet.src]

        self.distance_table[self.node][i] = min(current, new)

    # if dv is updated, send updates to all neighbours
    # printing to match sample output
    if self.distance_table[self.node] != oldDV:
        print('changes based on update')
        print('sending mincost updates to neighbours')
        for i in range(len(self.neighbourList)):
            to_layer_2(self.node, self.neighbourList[i], self.distance_table[self.node])
    else:
        print(f'no changes in node {self.node}, so nothing to do')
    print(self, 'routing table:', self.routingTable, '\n')


def common_link_cost_change2(self, to_entity, new_cost):
    """
    You may call a common function like this from your individual
    link_cost_change methods if you want.
    Note this is only for extra credit and only required for Entity0 and
    Entity1.
    """
    # pass  # FIXME (optional)
    print(f'*** cost of node {self.node} -> node {to_entity} has been changed to {new_cost} ***')

    # update graph and dist table entry
    cost[self.node][to_entity] = new_cost

    # revert DV to default value
    self.distance_table[self.node] = cost[self.node].copy()

    # revert routing table to default value
    for i in self.routingTable:
        if i == self.node:
            continue
        if i in self.neighbourList:
            self.routingTable[i] = i
        else:
            self.routingTable[i] = -1

    # send update to all neighbors
    print(f'node {self.node} sending mincost updates to neighbours\n')
    for neighbor in self.neighbourList:
        to_layer_2(self.node, neighbor, self.distance_table[self.node])


def common_update(self, packet):
    """
    You may call a common function like this from your individual update
    methods if you want.
    """
    # pass  # FIXME
    print(f'node {self.node}: update from {packet.src} received')

    # update dist table with the incoming DV
    self.distance_table[packet.src] = packet.mincost.copy()

    # remember old DV
    oldDV = self.distance_table[self.node].copy()

    # text book version of the algo - always recompute min cost to every node in the graph
    # via the info all the neighbors as long as there is an update coming in from one neighbor
    for i in range(len(self.distance_table[self.node])):
        if i == self.node:
            continue
        list = []
        for neighbor in self.neighbourList:
            list.append(cost[self.node][neighbor] + self.distance_table[neighbor][i])
        self.distance_table[self.node][i] = min(list)

    # if dv is updated, send updates to all neighbours
    # printing to match sample output
    if self.distance_table[self.node] != oldDV:
        print('changes based on update')
        print('sending mincost updates to neighbours')
        for i in range(len(self.neighbourList)):
            to_layer_2(self.node, self.neighbourList[i], self.distance_table[self.node])
    else:
        print(f'no changes in node {self.node}, so nothing to do')
    print(self)


def common_link_cost_change(self, to_entity, new_cost):
    """
    You may call a common function like this from your individual 
    link_cost_change methods if you want.
    Note this is only for extra credit and only required for Entity0 and 
    Entity1.
    """
    # pass  # FIXME (optional)
    print(f'*** cost of node {self.node} -> node {to_entity} has been changed to {new_cost} ***')

    # update graph and dist table entry
    cost[self.node][to_entity] = new_cost

    # text book way: throw away the old DV - recompute based on the info of all neighbors
    for i in range(len(self.distance_table)):
        # no need to compute cost to yourself
        if i == self.node:
            continue
        list = []
        for neighbor in self.neighbourList:
            list.append(cost[self.node][neighbor] + self.distance_table[neighbor][i])
        self.distance_table[self.node][i] = min(list)

    # send update to all neighbors
    print(f'node {self.node} sending mincost updates to neighbours\n')
    for neighbor in self.neighbourList:
        to_layer_2(self.node, neighbor, self.distance_table[self.node])


class Entity0(Entity):
    """Router running a DV algorithm at node 0"""

    # constructor here: make necessary changes to fields
    def __init__(self):
        super().__init__()
        self.node = 0
        self.neighbourList = []
        self.routingTable = {}
        common_init(self)

    def update(self, packet):
        common_update(self, packet)

    def link_cost_change(self, to_entity, new_cost):
        common_link_cost_change(self, to_entity, new_cost)


class Entity1(Entity):
    """Router running a DV algorithm at node 1"""

    # constructor here: make necessary changes to fields
    def __init__(self):
        super().__init__()
        self.node = 1
        self.neighbourList = []
        self.routingTable = {}
        common_init(self)

    def update(self, packet):
        common_update(self, packet)

    def link_cost_change(self, to_entity, new_cost):
        common_link_cost_change(self, to_entity, new_cost)


class Entity2(Entity):
    """Router running a DV algorithm at node 2"""

    # constructor here: make necessary changes to fields
    def __init__(self):
        super().__init__()
        self.node = 2
        self.neighbourList = []
        self.routingTable = {}
        common_init(self)

    def update(self, packet):
        common_update(self, packet)


class Entity3(Entity):
    """Router running a DV algorithm at node 3"""

    # constructor here: make necessary changes to fields
    def __init__(self):
        super().__init__()
        self.node = 3
        self.neighbourList = []
        self.routingTable = {}
        common_init(self)

    def update(self, packet):
        common_update(self, packet)
