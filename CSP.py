"""
This File demonstrates solving the crossword problem using constraints satisafiction 
"""

import sys

from crossword import *
from crossword_creator import *
import itertools
import timeit


class CSP():

    def __init__(self, crossword_creator):
        """
        Create new CSP crossword generate.
        """
        self.crossword_creator=crossword_creator

    def solve(self):
        """
            Enforce node and arc consistency, and then solve the CSP.
        """
        valid=self.words_variables_consistency()
        if valid==None:
            return None
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())


    def words_variables_consistency(self):
        """
            Check if there are m variables with length l then there should be m words or greater that have length l 
        """
        
        max_len=0
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

    
    def enforce_node_consistency(self):
        """
             Apply node consistency on all variables
        """
        for var in self.crossword_creator.crossword.variables:
            new_domain=[]
            for word in self.crossword_creator.domains[var]:
                if var.length == len(word):
                    new_domain.append(word)
            self.crossword_creator.domains[var]=new_domain
   


    def revise(self, x, y):
        """
             This function implements the Arc-consistency between two variables,
             it makes X arc-consistent with Y, for X to be arc consistent with respect to Y
             we should ensure that every value in X's domain has at least one possible
             choice from Y's domain
        """
        revised= False # revised indicates whether or not we made a change for x'domain
        overlap_idx=self.crossword_creator.crossword.overlaps[(x,y)]
        for x_word in self.crossword_creator.domains[x]:
            # check if there is possible value in Y's domain that statisifies the binary constraint between X and Y.
            y_words=self.crossword_creator.domains[y]
            no_match_found=any([True  if y_word[overlap_idx[1]]==x_word[overlap_idx[0]] else False for y_word in y_words])
            if no_match_found == False:
                self.crossword_creator.domains[x].remove(x_word)    # delete x_word from the domain of X
                revised=True                      # We made a change for x'domain
        return revised



    def ac3(self, arcs=None):
        """
            Enforce the arc consistency across the entire problem
        """
        queue=None
        if arcs==None:
            queue = list(itertools.product(self.crossword_creator.crossword.variables, self.crossword_creator.crossword.variables))
            queue = [arc for arc in queue if arc[0] != arc[1] and self.crossword_creator.crossword.overlaps[arc[0], arc[1]] is not None]
        else:
            queue=arcs
        
        while len(queue)!=0:
            cur_element=queue.pop(0)
            x=cur_element[0]
            y=cur_element[1]
            if self.revise(x,y)==True:
                if len(self.crossword_creator.domains[x])==0:
                    return False    # There is no way to solve the problem because we can't find a value 
                                    # for the X that statisfies all the overlapping constraint
                else:
                    """
                    after changing the x's domain, it might become not arc consistent with other variables
                    so we will check the consistency again along with x and it's neighbours except for y
                    because we have already checked it.
                    """
                    other_neighbours=self.crossword_creator.crossword.neighbors(x).remove(y)
                    if other_neighbours!=None:
                        for z in other_neighbours:
                            queue.append(tuple([x,z]))
        return True


       
    def assignment_complete(self, assignment):
        """
            check if `assignment` is complete (i.e., each variable is assigned to a value to each);
        """
        if set(assignment.keys()) == self.crossword_creator.crossword.variables and all(assignment.values()):
            return True
        else:
            return False

    def consistent(self, assignment):
        """
        The assignment will be inconsistent if it violates one of the following 3 rules
        1) the length of the value should be equal to the length of the variable ==> Node Consistency
        2) Values should be distinct for the variables ==> Arc Consistency
        3) There should be no conflicts between the neighbouring variables ==> Arc Consistency
        """


        """
                    First Rule
        """
        for var in assignment.keys():
            if len(assignment[var])!=var.length:
                return False

        """
                    Second Rule
        """
        """    
        as the elements of the set are unique so we will put the values
        of the assignment in a set and check if it's length is equal
        to the length of keys of assignment dict
        """
        if len(set(assignment.values())) != len(set(assignment.keys())):
            return False

        """
                    Third Rule
        """
        for var in assignment.keys():
            neighbors=self.crossword_creator.crossword.neighbors(var)
            for n in neighbors:
                overlap_idx=self.crossword_creator.crossword.overlaps[(var,n)]
                if n in assignment:
                    if assignment[var][overlap_idx[0]]!=assignment[n][overlap_idx[1]]:
                        return False
            
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        num_choices_avaliable = {word: 0 for word in self.crossword_creator.domains[var]}
        neighbors=self.crossword_creator.crossword.neighbors(var)
        var_words=self.crossword_creator.domains[var]
        for w in var_words:
            for neighbor in (neighbors - assignment.keys()):
                overlap = self.crossword_creator.crossword.overlaps[var, neighbor]
                # Loop through each word in neighbor's domain
                for word_n in self.crossword_creator.domains[neighbor]:
                    if w[overlap[0]]==word_n[overlap[1]]:
                        num_choices_avaliable[w]+=1

        sorted_list = sorted(num_choices_avaliable.items(), key=lambda x:x[1])
        return  reversed([x[0] for x in sorted_list])

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned_variables = self.crossword_creator.crossword.variables - assignment.keys()
        num_remaining_values = {variable: len(self.crossword_creator.domains[variable]) for variable in unassigned_variables}
        sorted_num_remaining_values = sorted(num_remaining_values.items(), key=lambda x: x[1])
        if len(sorted_num_remaining_values) == 1 or sorted_num_remaining_values[0][1] != sorted_num_remaining_values[1][1]:
            return sorted_num_remaining_values[0][0]
        
        else:
            num_degrees = {variable: len(self.crossword_creator.crossword.neighbors(variable)) for variable in unassigned_variables}
            sorted_num_degrees = sorted(num_degrees.items(), key=lambda x: x[1], reverse=True)
            return sorted_num_degrees[0][0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment)==True:
            return assignment
        var=self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var,assignment):
            new_assignment=assignment.copy()
            new_assignment[var]=value
            if self.consistent(new_assignment)==True:
                assignment[var]=value
                result=self.backtrack(assignment)
                if result !=None: # indicates failure we got stuck with this value and we have to try another one
                    return result
                assignment.pop(var, None)
        return None # indicates that There is no possible assignment for this variable 
                    # So,the problem has no solution


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
    CSP_Problem=CSP(creator)
    start = timeit.default_timer()
    assignment = CSP_Problem.solve()
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
