# Agent properties:
# Message
# Current Connection
# Connection history?
# Message completed?
# Strategy


class Agent:

    def __init__(self, id, initMessage, strategy):
        self.id = id
        self.message = initMessage
        self.strategy = strategy
        self.connections = []
        self.completed = false

    def storeConnection(agent):
        self.connections.append(agent)

    def makeConnection(agent):
        self.message = self.message.append(agent.message)
        storeConnection(agent)

    def checkCompleted(goalMessage):
        if self.message == goalMessage:
            self.completed = true
        return self.completed
