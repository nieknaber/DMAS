# Agent properties:
# Message
# Current Connection
# Connection history?
# Message completed?
# Strategy

import numpy as np


class Agent:

    def __init__(self, id, init_message, strategy, num_agents):
        """Init function for an agent. It initialises all the needed fields."""
        self.id = id
        self.secrets = {init_message}
        self.incoming_secrets = set()
        self.strategy = strategy
        self.connections = np.full(num_agents, False)
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

    def store_connections(self, other):
        """Stores the other agent's id after calling it.

        This is useful for the Call-Me-Once strategy,
        where an agent can only call another agent once.
        """
        self.connections[other.id] = True

    def __repr__ (self):
        """This function lets us print out an agent in a nicer format.

        Calling print(agent) somewhere else will now print 'Ag(self.id)'.
        """
        return f"Ag({self.id})"

    def print_info(self):
        """Prints out the id, secrets, strategy and connections of an agent."""
        print(f"id: {self.id}\nsecrets: {self.secrets}\nstrategy: {self.strategy}\nconnections: {self.connections}")
