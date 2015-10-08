import heapq
__author__ = 'redblobgames' # http://www.redblobgames.com/pathfinding/a-star/implementation.html

class PriorityQueue:
    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def get(self):
        return heapq.heappop(self.elements)[1]
       
    def size(self):
        return len(self.elements)

    def getNodes(self):
        nodes = []
        for elem in self.elements:
            nodes.append(elem[1])
        return nodes
