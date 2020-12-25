"""
This File demonstrates solving the crossword problem using A* search Algorithms
"""



import sys

from crossword import *
from crossword_creator import *
from util import PriorityQueue
from util import Node
import timeit


class general_search():

    def __init__(self, crossword_creator):
        self.crossword_creator=crossword_creator
        self._countActions=0


    @property
    def countActions(self):
        return self._countActions

    @countActions.setter
    def all_avaliable_actions(self):
        self._countActions=len(self.get_actions(self.initial_state))


    @property
    def initial_state(self):
        return dict.fromkeys(self.crossword_creator.crossword.variables)

    def enforce_node_consistency(self):
        for var in self.crossword_creator.crossword.variables:
            new_domain=[]
            for word in self.crossword_creator.domains[var]:
                if var.length == len(word):
                    new_domain.append(word)
            self.crossword_creator.domains[var]=new_domain

    """
        Check if there are m variables with length l then there should be m words or greater that have length l 
    """

    def words_variables_consistency(self):
        
        max_len=-1
        for word in self.crossword_creator.crossword.words:
            if max_len<len(word):
                max_len=len(word)
        
        occ_word=[0 for i in range(max_len+1)]
        occ_variables=[0 for i in range(max_len+1)]

        for var in self.crossword_creator.crossword.variables:
            occ_variables[var.length]+=1
        
        for word in self.crossword_creator.crossword.words:
            occ_word[len(word)]+=1


        for idx,word in enumerate(occ_word):
            if occ_variables[idx]>occ_word[idx]:
                return None
        return True 

    def get_actions(self,state):
        actions=list()
        for var in state:
            """
            check if the variable is unassigned if yes choose for it an assignment
            """
            if state[var]==None:
                """
                conditions is a dict with index of chosen word as a key 
                and value of the dict=word[index]

                """
                conditions=dict.fromkeys([i for i in range(var.length)])
                """
                get the all other variables that are overlapping with the variable "var"
                I want to assigm value to 
                """
                overlaps_set=self.crossword_creator.crossword.neighbors(var)
                for overlap_var in overlaps_set:
                    """
                    if the overlapping variables are assigned then the overlapping 
                    constraint between "var" and "overlap_var" must be satisified
                    """
                    if state[overlap_var]!=None:
                        overlap_idx=self.crossword_creator.crossword.overlaps[(var,overlap_var)]
                        if conditions[overlap_idx[0]] == None or conditions[overlap_idx[0]]==state[overlap_var][overlap_idx[1]]:
                            conditions[overlap_idx[0]]=state[overlap_var][overlap_idx[1]]
                        else:
                            """
                            we can't proceed any more with this state because it requires 
                            different values for the same place of the variable
                            that means we reach a contradiction
                            """
                            return []

                # avaliable words for certain variables that won't voilate any constraint
                avaliable_actions=[]
                # get words from the domain that satisifies the conditions
                for word in self.crossword_creator.domains[var]:
                    valid=True
                    # if the word is already assigned to another variable in we can't chose it 
                    if word in state.values():
                        continue
                    for i in conditions:
                        if conditions[i]!=None and conditions[i]!=word[i]:
                            valid=False
                            break
                    """
                    if this word satisifies all the conditions then it can be assigned to the variable
                    so we will put as an valid action in the tuple of "avaliable_actions"
                    """
                    if valid==True:
                        avaliable_actions.append(tuple([var,word]))
                """
                if there is no word in the domain of the unassigned variable that statisifies the condition 
                then we reached a contradiction and we can't proceed with this state

                """
                if len(avaliable_actions)==0:
                    return []
                else:
                    actions.extend(avaliable_actions)

        return actions

    
    
    def get_successor(self,state,action):
        new_state=state.copy()
        new_state[action[0]]=action[1]
        return new_state

    """
    check all variables are assigned 
     """
    def is_goal(self,state):
        return all(state.values())
    

    """
    choose a state that results in a minimum number of conflicts with other variables.
    """
    def min_conflict_heuristic(self,state):
        """
        return the number of actions that are avaliable in this state and choose the state that 
        will be have mon conflicts with other states
        """
        return self.countActions-len(self.get_actions(state))


    # A* search algorithm is used to solve the crossword as a search problem
    def solve(self,state):
        if self.is_goal(state):return[]
        # remove all invalid words from domain i.e run node consistency
        self.enforce_node_consistency()
        valid=self.words_variables_consistency()
        if valid==None:
            return None
        frontier=PriorityQueue()
        start_Node=Node(state,0)
        frontier.push(self.min_conflict_heuristic(start_Node.state),start_Node)
        exploredSet=[]

        while frontier.empty() is False:
            node=frontier.pop()
            if self.is_goal(node.state):
                return node.state
            else:
                exploredSet.append(node.state)
                actions=self.get_actions(node.state)
                for action in actions:
                    successor=self.get_successor(node.state,action)
                    if successor not in exploredSet and not frontier.contains_state(successor):
                        priority=self.min_conflict_heuristic(successor)+node.cost+1
                        successor_Node=Node(successor,node.cost+1)
                        frontier.push(priority,successor_Node)


def main():
    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    search_problem=general_search(creator)
    initial_state=search_problem.initial_state
    start = timeit.default_timer()
    assignment = search_problem.solve(initial_state)
    stop = timeit.default_timer()
    print('Time Taken to solve the problem: ', stop - start)

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)



if __name__ == "__main__":
    main()
