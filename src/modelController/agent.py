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
        self.has_token = True
        self.secrets_known = np.zeros(num_agents, dtype=int)

    def give_token(self, other_agent):
        self.has_token = False
        other_agent.has_token = True

    def update_secrets(self):
        self.secrets.update(self.incoming_secrets)
        self.secrets_known[self.id] = len(self.secrets)

    def update_secrets_known(self, other_agent_secrets_known):
        for i in range(0, len(self.secrets_known)-1):
            self.secrets_known[i] = max(self.secrets_known[i], other_agent_secrets_known[i])

    def store_connections(self, other):
        self.connections[other.id] = True

    def __repr__ (self):
        return f"Ag({self.id})"

    def print_info(self):
        print(f"id: {self.id}\nsecrets: {self.secrets}\nstrategy: {self.strategy}\nconnections: {self.connections}")