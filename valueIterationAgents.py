# valueIterationAgents.py
# -----------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


# valueIterationAgents.py
# -----------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


import mdp, util

from learningAgents import ValueEstimationAgent
import collections

class ValueIterationAgent(ValueEstimationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A ValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100):
        """
          Your value iteration agent should take an mdp on
          construction, run the indicated number of iterations
          and then act according to the resulting policy.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state, action, nextState)
              mdp.isTerminal(state)
        """
        self.mdp = mdp
        self.discount = discount
        self.iterations = iterations
        self.values = util.Counter() # A Counter is a dict with default 0
        self.runValueIteration()

    def runValueIteration(self):
        # Write value iteration code here
        "*** YOUR CODE HERE ***"

        for iteration in range(self.iterations):
            new_values = self.values.copy() #chatGPT helped me figure out storing the copies - was editing directly and giving me issues
            for state in self.mdp.getStates():
                if self.mdp.isTerminal(state):
                    continue  #skip terminal states
                max_value = float('-inf')
                for action in self.mdp.getPossibleActions(state):
                    q_value = self.getQValue(state, action)
                    max_value = max(max_value, q_value)
                new_values[state] = max_value
            self.values = new_values  


    def getValue(self, state):
        """
          Return the value of the state (computed in __init__).
        """
        return self.values[state]


    def computeQValueFromValues(self, state, action):
        """
          Compute the Q-value of action in state from the
          value function stored in self.values.
        """
        "*** YOUR CODE HERE ***"

        #equation from class slide
        q_value = 0
        for nextState, prob in self.mdp.getTransitionStatesAndProbs(state, action):
            reward = self.mdp.getReward(state, action, nextState)
            q_value += prob * (reward + self.discount * self.values[nextState])
        return q_value

        util.raiseNotDefined()

    def computeActionFromValues(self, state):
        """
          The policy is the best action in the given state
          according to the values currently stored in self.values.

          You may break ties any way you see fit.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return None.
        """
        "*** YOUR CODE HERE ***"

        if self.mdp.isTerminal(state):
            return None  
        best_action = None
        best_value = float('-inf')
        for action in self.mdp.getPossibleActions(state):
            q_value = self.getQValue(state, action)
            if q_value > best_value:
                best_value = q_value
                best_action = action
        return best_action

        util.raiseNotDefined()

    def getPolicy(self, state):
        return self.computeActionFromValues(state)

    def getAction(self, state):
        "Returns the policy at the state (no exploration)."
        return self.computeActionFromValues(state)

    def getQValue(self, state, action):
        return self.computeQValueFromValues(state, action)

class AsynchronousValueIterationAgent(ValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        An AsynchronousValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs cyclic value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 1000):
        """
          Your cyclic value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy. Each iteration
          updates the value of only one state, which cycles through
          the states list. If the chosen state is terminal, nothing
          happens in that iteration.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state)
              mdp.isTerminal(state)
        """
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        states = self.mdp.getStates()  
        num_states = len(states)
        state_index = 0 #which state to update

        for iteration in range(self.iterations):
            state = states[state_index]

            if not self.mdp.isTerminal(state):
                max_value = float('-inf') #get max q value
                for action in self.mdp.getPossibleActions(state):
                    q_value = self.computeQValueFromValues(state, action)
                    max_value = max(max_value, q_value)
                
                self.values[state] = max_value
            
            #go to next state
            state_index += 1
  
            #once at end of list, go back to start - chatGPT helped me debug this as I was missing this restart for the subsequent iteration
            if state_index >= num_states:
                state_index = 0

class PrioritizedSweepingValueIterationAgent(AsynchronousValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A PrioritizedSweepingValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs prioritized sweeping value iteration
        for a given number of iterations using the supplied parameters.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100, theta = 1e-5):
        """
          Your prioritized sweeping value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy.
        """
        self.theta = theta
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        "*** YOUR CODE HERE ***"

        #1 - Compute predecessors for all states
        predecessors = {}
        for state in self.mdp.getStates():
            predecessors[state] = set()

        for state in self.mdp.getStates():
            if not self.mdp.isTerminal(state):
                for action in self.mdp.getPossibleActions(state):
                    for nextState, prob in self.mdp.getTransitionStatesAndProbs(state, action):
                        if prob > 0:
                            predecessors[nextState].add(state)

        #2 - Initialize the priority queue
        priority_queue = util.PriorityQueue()

        for state in self.mdp.getStates():
            if not self.mdp.isTerminal(state):
                max_q_value = max([self.computeQValueFromValues(state, action)
                                   for action in self.mdp.getPossibleActions(state)]) #chatGPT helped me condense finding the max q value
                diff = abs(self.values[state] - max_q_value)
                priority_queue.push(state, -diff)

        #3 - Perform iterations to update the values
        for iteration in range(self.iterations):
            if priority_queue.isEmpty():
                break

            state = priority_queue.pop()

            if not self.mdp.isTerminal(state):
                max_q_value = max([self.computeQValueFromValues(state, action)
                                   for action in self.mdp.getPossibleActions(state)])
                self.values[state] = max_q_value
            
            #4 - Update all predecessors of the popped state
            for p in predecessors[state]:

                max_q_value = max([self.computeQValueFromValues(p, action)
                                   for action in self.mdp.getPossibleActions(p)])
                diff = abs(self.values[p] - max_q_value)

                if diff > self.theta:
                    priority_queue.update(p, -diff)
