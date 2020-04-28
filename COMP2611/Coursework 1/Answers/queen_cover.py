## Definition of Queen's Cover problem
## Coursework 1 of Hollow Man
## For use with queue_search.py

from __future__ import print_function

from copy import deepcopy

# Representation of a state:
# (full_board_state)
# Queen is 2 in value,
# 1 value represents that this square has already been covered,
# if the square isn't covered, it will have a 0 in value. 
# So on a small 3x3 board we have a goal state such as:
#
# ( [[1,1,1],
#    [1,2,1],
#    [1,1,1]]  )

# Will print info about problem
def qc_print_problem_info():
    print( "The Queen's Cover (", BOARD_X, "x", BOARD_Y, "board)" )

# Get all the possible moves
def qc_possible_actions(state):
      moves = []
      for y in range(BOARD_Y):
            for x in range(BOARD_X):
				  # If the quare isn't queen, append it to possible moves
                  if state[y][x] != 2:
                        moves.append((y,x))
      return moves

# Get covered when queen moves
def qc_successor_state(action, state):
      RightDown_Y=LeftDown_Y = RightUp_Y = LeftUp_Y = action[0]
      RightDown_X=LeftDown_X = RightUp_X = LeftUp_X = action[1]
      newstate = deepcopy(state)
      newstate[action[0]][action[1]] = 2
      # Cover every square on y axis
      for x in range(BOARD_X):
            newstate[action[0]][x] = 1
      # Cover every square on x axis
      for y in range(BOARD_Y):
            newstate[y][action[1]] = 1
      # Cover every square on right down diagonal line
      while RightDown_Y < BOARD_Y-1 and RightDown_X < BOARD_X-1:
          newstate[RightDown_Y+1][RightDown_X+1] = 1
          RightDown_Y += 1
          RightDown_X += 1
      # Cover every square on right up diagonal line
      while RightUp_Y < BOARD_Y-1 and RightUp_X > 0:
          newstate[RightUp_Y+1][RightUp_X-1] = 1
          RightUp_Y += 1
          RightUp_X -= 1
      # Cover every square on left down diagonal line
      while LeftDown_Y > 0 and LeftDown_X < BOARD_X-1:
          newstate[LeftDown_Y-1][LeftDown_X+1] = 1
          LeftDown_Y -= 1
          LeftDown_X += 1
      # Cover every square on left up diagonal line
      while LeftUp_Y > 0 and LeftUp_X > 0:
          newstate[LeftUp_Y-1][LeftUp_X-1] = 1
          LeftUp_Y -= 1
          LeftUp_X -= 1
      return newstate

# Go through the whole board and check if any square hasn't been covered
# If any square hasn't been covered, the goal state hasn't been reached,the function will return false, else it has.
def qc_test_goal_state(state):
    for x in range(BOARD_Y):
        for y in range(BOARD_X):
            if state[x][y] == 0:
                return False
    return True

## Return a problem spec tuple for a given board size
def make_qc_problem(X,Y):
	# global variables of board size
    global BOARD_X, BOARD_Y
    BOARD_X = X
    BOARD_Y = Y
    # get the initial state matrix x*y filled with 0
    qc_initial_state = [[0 for x in range(X)] for y in range(Y)]
    return  ( None,
              qc_print_problem_info,
              qc_initial_state,
              qc_possible_actions,
              qc_successor_state,
              qc_test_goal_state
            )
