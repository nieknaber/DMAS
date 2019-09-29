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
        self.secrets = {init_message}
        self.incoming_secrets = set()
        self.strategy = strategy
        self.connections = np.full(num_agents, False)
        self.completed = False

    def get_secrets(self):
        return self.secrets

    def update_secrets(self,):
        self.secrets.update(self.incoming_secrets)

    def store_connections(self, other):
        self.connections[other.id] = True

    def check_completed(self, goal_message):
        if self.secrets == goal_message:
            self.completed = True
        return self.completed

    def __repr__ (self):
        return f"Ag({self.id})"

    def print_info(self):
        print(f"id: {self.id}\nsecrets: {self.secrets}\nstrategy: {self.strategy}\nconnections: {self.connections}")
