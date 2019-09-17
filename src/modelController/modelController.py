import "agent.py"
import numpy as np
import random as rn

class ModelController:

    def __init__(self, numberAgents, numberConnections):
        self.numberAgents = numberAgents
        self.numberConnections = numberConnections
        self.initAgents(self)
        self.agents = np.empty(self.numberAgents, dtype=object)
        self.agentsRandom = []


    def initAgents(self):
        for i in range(self.numberAgents):
            self.agents[i] = new Agent(i, [], self.numberAgents)
            self.agentsRandom.append(self.agents[i]) ## random list for shuffeling

    def makeConnections(self):
        rn.shuffle(self.agentsRandom)

        for i in range(self.agentsRandom):
            makeSingleConnection(self.agentlist.pop(), self.agentList.pop())

        self.restoreList():

    def makeSingleConnection(agent1, agent2):
        arr1 = agent1.getSecrets
        arr2 = agent2.getSecrets

        agent1.updateSecrets(arr2)
        agent2.updateSecrets(arr1)

    def.restoreList(self):
        self.agentsRandom = self.agents.tolist()