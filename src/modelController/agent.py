# Agent properties:
# Message
# Current Connection
# Connection history?
# Message completed?
# Strategy

import numpy as np


class Agent:

    def __init__(self, id, init_message, num_agents):
        """Init function for an agent. It initialises all the needed fields."""
        self.id = id
        self.secrets = {init_message}
        self.incoming_secrets = set()
        self.connections = np.full(num_agents, False)
        self.secrets_known = np.zeros(num_agents, dtype=int)
        self.called = []
        self.call_targets = dict()
        # If an agent has a token, it can make a call
        self.has_token = True

    def give_token(self, other_agent):
        """Gives an agent token to another agent.

        Argument: other_agent -- the agent this agent
        will give its token to.
        """
        self.has_token = False
        other_agent.has_token = True

    def update_secrets(self):
        """Updates the current set of secrets with the incoming secrets."""
        self.secrets.update(self.incoming_secrets)
        self.secrets_known[self.id] = len(self.secrets)

    def update_secrets_known(self, other_agent_secrets_known):
        for i in range(len(self.secrets_known) - 1):
            self.secrets_known[i] = max(self.secrets_known[i], other_agent_secrets_known[i])

    def store_connections(self, other):
        """Stores the other agent's id after calling it.

        This is useful for the Call-Me-Once strategy,
        where an agent can only call another agent once.
        """
        self.connections[other.id] = True

    def call_target_solved(self):
        targets = set()
        for target_agent in self.call_targets:
            solved = True
            for target_secret in target_agent.secrets:
                if target_secret not in self.secrets:
                    solved = False
                    break
            if solved:
                targets.add(target_agent)
        return targets

    def target_secrets(self):
        targets = set()
        for target_agent in self.call_targets:
            for target_secret in target_agent.secrets:
                if target_secret not in self.secrets:
                    targets.add(target_secret)
        return targets

    def __repr__(self):
        """This function lets us print out an agent in a nicer format.

        Calling print(agent) somewhere else will now print 'Ag(self.id)'.
        """
        return f"Ag({self.id})"

    def print_info(self):
        """Prints out the id, secrets, strategy and connections of an agent."""
        print(f"id: {self.id}\nsecrets: {self.secrets}\nstrategy: {self.strategy}\nconnections: {self.connections}")