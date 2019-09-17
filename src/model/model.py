import "agent.py"
import numpy as np

class Model:

    def __init__(self, numberAgents, numberConnections):
        self.numberAgents = numberAgents
        self.numberConnections = numberConnections
        self.initAgents(self)

    def initAgents(self):
        self.agents = np.empty(self.numberAgents, dtype=object)

        for i in range(self.numberAgents):
            self.agents[i] = new Agent()

