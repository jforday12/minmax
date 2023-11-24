import time
import copy


class State:

  def __init__(self, heaps, max, alpha=float('-inf'), beta=float('inf')):
    #initalises the properties of the state node
    #provides the heaps which is the current state of the heaps
    #value-indicates who is winning
    #max-determinesis true or false depending on if its max turn
    self.heaps = heaps
    self.value = None
    self.max = max
  


class Game:

  def __init__(self, n, m, k):
    self.n = n  # number of heaps
    self.m = m  # number of objects in each heap
    self.k = k  # maximum number of objects that can be removed from a
    self.heaps = []

  def initialize_game(self):
    self.heaps = [self.m] * self.n  # initialize all heaps with m
    self.current_player = 1  # player 1 starts the game

  def get_input(self):
    """
    Gets input from the player and validates it
    """
    heap_input = input("Enter heap to remove from: ")
    stick_input = input("Enter number of sticks to remove: ")
    # validate input from player
    while not self.is_valid(int(heap_input), int(stick_input)):
      print("Invalid input! Please enter legal values")
      heap_input = input("Enter heap to remove from: ")

      stick_input = input("Enter number of sticks to remove: ")
    return heap_input, stick_input

  def play(self):
    state = State(self.heaps, True)
    while not self.terminal(state):
      # draw the heaps
      self.draw_heaps()
      print("---MAX TURN---")
      # print the maximizing move
      max_move = self.max(state)
      print(f"Maximizing Move: Remove {max_move[1]} from heap {max_move[0]}")
      # get input from player
      heap_input, stick_input = self.get_input()
      # remove sticks from heap
      self.heaps[int(heap_input)] -= int(stick_input)
      # move to next game state
      state = State(self.heaps, False)
      if self.terminal(state):
        break
      print("---MIN TURN---")
      state = self.min(state)

  def draw_heaps(self):
    #draws the heaps and associated sticks
    print("Current game state:")
    for i in range(len(self.heaps)):
      print(f"Heap {i}:")
      print(self.heaps[i] * " | ")

  def max(self, state):
    start_time = time.time()
    #runs the function to get all possible actions
    actions = self.actions(state)
    #sets the current best value to -infinity to be reset on first iteration
    best_v = float('-inf')
    #loops through available actions 
    for a in actions:
      #runs the minimum value dual recursive function and passess in alpha and beta of -infinity and infinity
      v = self.min_value(self.result(state, a))
      #once the value of the current action has been determined it determines if its the best move for max
      if v > best_v:
        best_v = v
        best_action = a
      #stores and returns the best action
    print(f"max takes seconds --- {(time.time() - start_time)}")
    return best_action

  def min(self, state):
    start_time = time.time()
    #runs the function to get all possible actions
    actions = self.actions(state)
    #sets the current best value to -infinity to be rest on first iteration
    best_v = float('inf')
    #loops through available actions
    for a in actions:
      #runs the minimum value dual recursive function and passes in alpha and beta of -infinity and infinity
      v = self.max_value(self.result(state, a))
      #once the value of the current action has been determined it determines if its the best move for min
      if v < best_v:
        best_v = v
        best_action = a
    #stores and executes the best action for minimum 
    #returns the new state of the game 
    print(f"Min removes {best_action[1]} from heap {best_action[0]}")
    self.heaps[best_action[0]] = self.heaps[best_action[0]] - best_action[1]
    print(f"min takes seconds --- {(time.time() - start_time)}")
    return State(self.heaps, True)
  
  #dual recursive function to find value of action
  def max_value(self, state):
    #if an end state is returned then return the value of that state, 0 if min won, or 1 if max won
    if self.terminal(state):
      return self.utility(state)
    val = float('-inf')
    #iterate through the possible action and choose the value which maximises the current value vs the returned value
    for a in self.actions(state):
      val = max(val, self.min_value(self.result(state, a)))
    return val

  #dual recursive function to find value of action
  def min_value(self, state):
    #if at an end state it returns the value of that state, 0 if min won and 1 if max won
    if self.terminal(state):
      return self.utility(state)
    val = float('inf')
    #iterate through the possible action and choose the value which maximises the current value vs the returned value
    for a in self.actions(state):
      val = min(val, self.max_value(self.result(state, a)))
    return val

  #find the list of all valid actions given the state returning a list
  def actions(self, state):
    action_list = []
    for heap in range(len(state.heaps)):
      for removed in range(1, self.k + 1):
        if state.heaps[heap] - removed >= 0:
          action_list.append([heap, removed])
    return action_list
  #if all elements are 0 in the state then its a terminal state
  def terminal(self, state):
    return all(element == 0 for element in state.heaps)
  #check if an input is valid, (an integer)
  def is_valid(self, heap_input, stick_input):
    if heap_input < 0 or heap_input > self.n:
      return False
    if stick_input < 1 or stick_input > self.k:
      return False
    if self.heaps[heap_input] - stick_input < 0:
      return False
    return True

 #once a terminal state is reached then return 1 if max has won. 
  #if not then return 0
  def utility(self, state):
    """
    Returns value of a state node

    Args:
      state {Node} -- node representing the state
    
    """
    if state.max:
      state.value = 1
    else:
      state.value = 0
    return state.value

  #return the resulting state for a given move
  #once the move is executed the turn is fliiped to the other player (min or max)
  def result(self, state, a):
    new_heaps = copy.copy(state.heaps)
    new_heaps[a[0]] = new_heaps[a[0]] - a[1]
    return State(new_heaps, not state.max)
  
  
if __name__ == "__main__":
  game = Game(4, 4, 3)
  game.initialize_game()
  game.play()
