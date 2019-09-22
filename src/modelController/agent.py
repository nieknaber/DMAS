# Agent properties:
# Message
# Current Connection
# Connection history?
# Message completed?
# Strategy

import numpy as np


class Agent:

    def __init__(self, id, init_message, strategy, num_agents):
        self.id = id
        self.messages = {init_message}
        self.incoming_messages = set()
        self.strategy = strategy
        self.connections = np.empty(num_agents, dtype="?")
        self.completed = False

    def get_secrets(self):
        return self.messages

    def update_secrets(self,):
        self.messages.update(self.incoming_messages)

    def store_connections(self, other):
        self.connections[other.id] = True

    def check_completed(self, goal_message):
        if self.messages == goal_message:
            self.completed = True
        return self.completed

    def print_info(self):
        print(f"id: {self.id}\nmessages: {self.messages}\nstrategy: {self.strategy}\nconnections: {self.connections}")
