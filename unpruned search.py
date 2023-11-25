import time
import copy
import matplotlib.pyplot as plt


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
    self.heaps = [] # current state of heaps 

    self._visited = 0 # number of visited states (used for benchmark)

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
    """
    Allows player to play vs Min with Maximizing moves suggested 
    """
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

  def benchmark(self):
    """
    Simulates Max vs Min with selection time and 
    nodes visited being benchmarked.
    """
    turn = 1
    times = {}
    nodes_visited = {}

    state = State(self.heaps, True)
    while not self.terminal(state):
      t = time.time()
      heap, remove = self.max(state)
      self.heaps[heap] -= remove
      times[turn] = time.time() - t
      nodes_visited[turn] = self._visited
      turn+=1
      state = State(self.heaps, False)
      if self.terminal(state):
        break
      t = time.time()
      state = self.min(state)
      times[turn] = time.time() - t
      nodes_visited[turn] = self._visited
      turn+=1

    return times, nodes_visited
    
  def draw_heaps(self):
    #draws the heaps and associated sticks
    print("Current game state:")
    for i in range(len(self.heaps)):
      print(f"Heap {i}:")
      print(self.heaps[i] * " | ")

  def max(self, state):
    # reset nodes visited on new call
    self._visited = 0
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
    return best_action

  def min(self, state):
    # reset nodes visited on new call
    self._visited = 0
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
    self._visited += 1 # increment to track visited nodes
    new_heaps = copy.copy(state.heaps)
    new_heaps[a[0]] = new_heaps[a[0]] - a[1]
    return State(new_heaps, not state.max)
  
  
def performance_evaluation(n_max, m_max, k_max) :
  """
  Runs performance evaluation varying the number of objects, heaps and
  objects that can removed. 

  Args:
    n_max {int} -- max number of heaps to iterate to;
    m_max {int} -- max number of objects per heap to iterate to;
    k_max {int} -- max number of objects that can be removed to iterate to;
  """
  n_range = [i for i in range(1, n_max+1)]
  m_range = [i for i in range(5, m_max+1)]
  k_range = [i for i in range(1, k_max+1)]

  _n_evaluation(n_range, 5, 3)
  _m_evaluation(1, m_range, 3)
  _k_evaluation(1, 10, k_range)

def _n_evaluation(n_range, m_def, k_def):
      n_fig = plt.figure()
      times_plot = n_fig.add_subplot(1, 2, 1)
      times_plot.set_xlabel("Turn")
      times_plot.set_ylabel("Average selection time (seconds)")
      visited_plot = n_fig.add_subplot(1, 2, 2)
      visited_plot.set_xlabel("Turn")
      visited_plot.set_ylabel("Average nodes visited (log)")

      for n in n_range:
        print(f"n = {n}")
        game = Game(n, m_def, k_def)
        game.initialize_game()
        times, visited = game.benchmark()
        times_plot.plot(times.keys(), times.values(), label=f"n = {n}")
        times_plot.legend()
        visited_plot.plot(visited.keys(), visited.values(), label=f"n = {n}")
        visited_plot.set_yscale('log')
        visited_plot.legend()
      plt.show()

def _m_evaluation(n_def, m_range, k_def):
      m_fig = plt.figure()
      times_plot = m_fig.add_subplot(1, 2, 1)
      times_plot.set_xlabel("Turn")
      times_plot.set_ylabel("Average selection time (seconds)")
      visited_plot = m_fig.add_subplot(1, 2, 2)
      visited_plot.set_xlabel("Turn")
      visited_plot.set_ylabel("Average nodes visited (log)")

      for m in m_range:
        game = Game(n_def,m, k_def)
        game.initialize_game()
        times, visited = game.benchmark()
        times_plot.plot(times.keys(), times.values(), label=f"m = {m}")
        times_plot.legend()
        visited_plot.plot(visited.keys(), visited.values(), label=f"m = {m}")
        visited_plot.set_yscale('log')
        visited_plot.legend()
      plt.show()

def _k_evaluation(n_def, m_def, k_range):
      k_fig = plt.figure()
      times_plot = k_fig.add_subplot(1, 2, 1)
      times_plot.set_xlabel("Turn")
      times_plot.set_ylabel("Average selection time (seconds)")
      visited_plot = k_fig.add_subplot(1, 2, 2)
      visited_plot.set_xlabel("Turn")
      visited_plot.set_ylabel("Average nodes visited (log)")

      for k in k_range:
        game = Game(n_def, m_def, k)
        game.initialize_game()
        times, visited = game.benchmark()
        times_plot.plot(times.keys(), times.values(), label=f"k = {k}")
        times_plot.legend()
        visited_plot.plot(visited.keys(), visited.values(), label=f"k = {k}")
        visited_plot.set_yscale('log')
        visited_plot.legend()
      plt.show()

  
if __name__ == "__main__":
  performance_evaluation(3, 10, 5)
