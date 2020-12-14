import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    @property
    def initial_state(self):
        return dict.fromkeys(self.crossword.variables)

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        #crossword feha variables meen ka list w eh words w constraints(overlapping)
        for var in self.crossword.variables:
            new_domain=[]
            for word in self.domains[var]:
                if var.length == len(word):
                    new_domain.append(word)
            self.domains[var]=new_domain


    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    # MAKE SUREEEEEEE EN THIS DOESNT CHOOSE THE SAME WORD TAKEN FOR ANOTHER UNASSIGNED VARIABLE
    def get_actions(self,state):
        print("currrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr")
        print(state)
        actions=list()
        for var in state:
            # check if the variable is unassigned if yes choose for it an assignment
            if state[var]==None:
                """
                conditions is a dict with index of chosen word as a key 
                and value of the dict=word[index]

                """
                conditions=dict.fromkeys([i for i in range(var.length)])
                # get the all other variables that are overlapping with the variable I want to assigm value to "var"
                overlaps_set=self.crossword.neighbors(var)
                for overlap_var in overlaps_set:
                    # if the overlapping variables are assigned then the overlapping constraint between "var" and "overlap_var" must be satisified
                    if state[overlap_var]!=None:
                        overlap_idx=self.crossword.overlaps[(var,overlap_var)]
                        if conditions[overlap_idx[0]] == None or conditions[overlap_idx[0]]==state[overlap_var][overlap_idx[1]]:
                            conditions[overlap_idx[0]]=state[overlap_var][overlap_idx[1]]
                        else:
                            print("Contradiction !!!!!")
                            return None # we can't proceed any more with this state because it requires different values for the same place of the variable

                # avaliable words for certain variables that won't voilate any constraint
                avaliable_actions=[]
                # get words from the domain that satisifies the conditions
                for word in self.domains[var]:
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
                    print("Contradiction !!!!!")
                    return None
                else:
                    actions.extend(avaliable_actions)

        print(actions)
        return actions

    def get_successor(self,state,action):
        new_state=[]
        return new_state

    def is_goal(self,state):
        return False



    def solve(self,state):
        if self.is_goal(state):return[]
        #remove all invalid words from domain i.e run node consistency
        print("Initial_State",state)
        self.enforce_node_consistency()
        # self.get_actions(state)
        for x in self.crossword.variables:
            state[x]='FOUR'
            self.get_actions(state)
            break;
        return []
        # frontier=[state]
        # parents={state:(None,None)}
        # while len(frontier)>0:
        #     current_state=frontier.pop(0)
        #     for action in self.get_actions(current_state):
        #         child=self.get_successor(current_state,action)
        #         if self.is_goal(child):
        #             solution=[action]
        #             while True:
        #                 current_state,action=parents[current_state]
        #                 if action is None:
        #                     return solution
        #                 else:
        #                     solution.insert(0, action)
        #             return solution
        #         if child not in parents:
        #             parents[child]=[current_state,action]
        #             frontier.append(child)
        # return None


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

    initial_state=creator.initial_state
    assignment = creator.solve(initial_state)

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)



if __name__ == "__main__":
    main()
