# Agent properties:
# Message
# Current Connection
# Connection history?
# Message completed?
# Strategy

import numpy as np

class Agent:
    def __init__(self, id, initMessage, numberAgents):
        self.id = id
        self.message = initMessage
        self.strategy = strategy
        self.connections = np.empty(numberAgents, dtype=boolean)
        self.completed = false

    def getSecrets(self):
        return self.message

    def updateSecrets(self, newMessage):
        self.message.append(newMessage)

    def storeConnection(agent):
        self.connections[agent.id] = true

    def checkCompleted(goalMessage):
        if self.message == goalMessage:
            self.completed = true
        return self.completed
