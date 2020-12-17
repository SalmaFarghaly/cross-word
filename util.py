
import heapq

class Node():
    def __init__(self, state,cost):
        self.state = state
        self.cost=cost

    def __lt__(self, other):
        return self

    def __le__(self,other):
        return self

    def __gt__(self, other):
        return self
    
    def __ge__(self, other):
        return self 

    def __print__(self):
        print(self.state,self.cost)
        

class PriorityQueue():
    def __init__(self):
        self.frontier = []

    def push(self, priority, x):
        heapq.heappush(self.frontier, (-priority, x))

    def pop(self):
        _, x = heapq.heappop(self.frontier)
        return x

    def empty(self):
        return len(self.frontier) == 0

    def contains_state(self,state):
        return any(node[1].state == state for node in self.frontier)


    def __print__(self):
        pass
