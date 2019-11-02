import random as rn

class Model:

    def __init__(self, strategy):
        """Initialises the controller.

        Input arguments:
        strategy -- The strategy the agents will use.
        """
        self.agents = []
        self.num_agents = 0
        self.connections = []
        self.strategy = strategy
        self.all_secrets = set()

    def make_callable_list(self, agent_calling, called_agents):
        """Makes a list of callable agents, for an agent that is currently trying to
        make a call.

        Input arguments:
        agent_calling -- the agent trying to make a call, and who has to choose another agent
        called_agents -- the set of agents that have already made a call this iteration, and
            thus cannot be called by the currently calling agent
        Output:
            callable_agents -- The list of agents that can be called by this agent.
        """
        callable_agents = self.agents.copy()
        callable_agents.remove(agent_calling)
        callable_agents = self.remove_agents_calling(callable_agents, called_agents)
        if self.strategy == 'Call-Me-Once':
            return self.remove_called_agents(callable_agents, agent_calling)
        if self.strategy == 'Learn-New-Secrets':
            return self.remove_agents_same_secrets(callable_agents, agent_calling)
        return callable_agents

    def remove_agents_calling(self, callable_agents, called_agents):
        """Removes already calling agents from the callable agents list."""
        for called_agent in called_agents:
            if called_agent in callable_agents:
                callable_agents.remove(called_agent)
        return callable_agents

    def remove_called_agents(self, callable_agents, agent_calling):
        """Removes agents from the agent's 'already called list' (agent_calling.connections)
        This is only used for the Call-Me-Once strategy

        Input arguments: 
        callable_agents -- The list of agents that can be called
        agent_calling -- The agent that is currently trying to make a call

        Output:
        callable_agents -- The list of agents that can be called, after the operation
            of removing the already called agents from this list.
        """
        for connected_agent in agent_calling.connections:
            if connected_agent in callable_agents:
                callable_agents.remove(connected_agent)
        return callable_agents

    def remove_agents_same_secrets(self, callable_agents, agent_calling):
        """This function is only used in the Learn New Secrets strategy.
        It removes agents from the callable list if the agent trying to make a call
        already knows about their secrets.

        Input arguments: 
        callable_agents -- The list of agents that can be called
        agent_calling -- The agent that is currently trying to make a call

        Output:
        callable_agents -- The list of agents that can be called, after the operation
            of removing the already called agents from this list.
        """
        for other_agent in self.agents:
            if f"Secret {other_agent.id}" in agent_calling.secrets:
                if other_agent in callable_agents:
                    callable_agents.remove(other_agent)
        return callable_agents

    def determine_agent(self, agent_calling, callable_agents, timesteps_taken):
        """This function chooses another agent for the agent_calling based on the strategy
        the agents are using.

        For some strategies, there is a determine_agent_{strategy} function.
        In case none of these strategies are being used. The chosen agent for
        agent_calling is uniformly randomly picked from the list of callable agents.

        Input arguments:
        agent_calling -- The agent currently trying to call another agent.
        callable_agents -- The list of agents that are callable for this agent.
        timesteps_taken -- The number of timesteps the simulation is already underway.
            This argument is passed to self.determine_agent_bubble and self.determine_agent_multiply

        Output:
        connection_agent -- The agent agent_calling will exchange secrets with.
        """
        connection_agent = None
        if self.strategy == 'Bubble':
            self.determine_agent_bubble(agent_calling, timesteps_taken)
        elif self.strategy == 'Mathematical':
            self.determine_agent_multiply(agent_calling, callable_agents, timesteps_taken)
        elif self.strategy == 'Min-Secrets':
            self.determine_agent_min_secrets(agent_calling, callable_agents)
        elif self.strategy == 'Max-Secrets':
            self.determine_agent_max_secrets(agent_calling, callable_agents)
        elif self.strategy == 'Most-useful':
            self.determine_agent_balanced_secrets(agent_calling, callable_agents)
        if connection_agent is None:
            connection_agent = rn.choice(callable_agents)
        return connection_agent

    def determine_agent_bubble(self, agent_calling, timesteps_taken):
        """Determines the agent agent_calling will exchange secrets with according
        to the Bubble strategy.

        Input arguments:
        agent_calling -- The agent currently trying to make a call
        timesteps_taken -- The number of timesteps the simulation is already underway.

        Output:
        connection_agent -- The agent agent_calling will have a connection with.
        """
        connection_agent = None
        half_bubble = (2 ** timesteps_taken) / 2
        next_step = agent_calling.id % (2 ** (timesteps_taken + 1))
        if next_step <= half_bubble:
            idx = agent_calling.id + (2 ** timesteps_taken)
        else:
            idx = agent_calling.id - (2 ** timesteps_taken)
        if idx < len(self.agents):
            connection_agent = self.agents[idx]
        return connection_agent

    def determine_agent_multiply(self, agent_calling, callable_agents, timesteps_taken):
        """Determines the agent agent_calling will exchange secrets with according
        to the Multiply strategy.

        The way the index of the connection_agent is calculated:
        idx = (agent_calling.id + 1) * (timesteps_taken + 2) - 1
        If it turns out that there is no agent with this id in the callable list,
        The index will be incremented and the process repeats. If idx > self.num_agents,
        the idx is reset to 0.

        Input arguments:
        agent_calling -- The agent currently trying to make a call
        callable_agents -- The list of agents agent_calling can call.
        timesteps_taken -- The number of timesteps the simulation is already underway.

        Output:
        connection_agent -- The agent agent_calling will have a connection with.
        """
        idx = (agent_calling.id + 1) * (timesteps_taken + 2) - 1
        return self.solve_multiply(idx % self.num_agents, callable_agents)

    def find_agent_in_callable(self, callable_agents, idx):
        """Checks whether there is an agent in the callable_agents list that has
        the ID that was calculated using the Multiply strategy.

        If there is an agent whose ID is equal to the calculated ID,
        this agent will be the agent the agent_calling (in determine_agent_multiply)
        will exchange secrets with.

        Input arguments:
        callable_agents -- The list of callable agents for the agent currently trying
            to make a call
        idx -- The calculated index (according to the Multiply strategy)"""
        for agent in callable_agents:
            if agent.id == idx:
                return True
        return False

    def solve_multiply(self, idx, callable_agents):
        """Calls the find_agent_in_callable function, which checks whether the
        calculated index belongs to an agent in the callable_agents list.

        If this is the case, this agent is returned as the connection_agent, which
        will exchange secrets with the agent_calling. If this is not the case,
        the process repeats with an incremented index.

        Input arguments:
        idx -- The calculated index according to the multiply strategy.
        callable_agents -- The list of agents that can currently be called by the
            agent trying to make a call.
        """
        if self.find_agent_in_callable(callable_agents, idx):
            return self.agents[idx]
        return self.solve_multiply((idx + 1) % self.num_agents, callable_agents)

    def determine_agent_min_secrets(self, agent_calling, callable_agents):
        """Determines the connection_agent according to the Min Secrets strategy.

        The strategy determines the connection agent by looking at the secrets_known
        array that each agent has. This array stores information about other agents,
        namely the number of secrets they all know. The agent_calling will call the
        agent from callable_agents that knows the lowest number of secrets (as far
        as the agent_calling knows)

        Input arguments:
        agent_calling -- The agent currently trying to make a call
        callable_agents -- The list of agents agent_calling can call.

        Output:
        connection_agent -- The agent that the agent_calling will exchange secrets with.
        """
        connection_agent = None
        min_known = self.num_agents + 1
        for callable_agent in callable_agents:
            if agent_calling.secrets_known[callable_agent.id] < min_known:
                connection_agent = callable_agent
                min_known = agent_calling.secrets_known[callable_agent.id]
        return connection_agent

    def determine_agent_max_secrets(self, agent_calling, callable_agents):
        """Determines the connection_agent according to the Max Secrets strategy.

        The strategy determines the connection agent by looking at the secrets_known
        array that each agent has. This array stores information about other agents,
        namely the number of secrets they all know. The agent_calling will call the
        agent from callable_agents that knows the highest number of secrets (as far
        as the agent_calling knows)

        Input arguments:
        agent_calling -- The agent currently trying to make a call
        callable_agents -- The list of agents agent_calling can call.

        Output:
        connection_agent -- The agent that the agent_calling will exchange secrets with.
        """
        connection_agent = None
        max_known = 0
        for callable_agent in callable_agents:
            if agent_calling.secrets_known[callable_agent.id] > max_known:
                connection_agent = callable_agent
                max_known = agent_calling.secrets_known[callable_agent.id]
        return connection_agent

    def determine_agent_balanced_secrets(self, agent_calling, callable_agents):
        """Determines the connection_agent according to the Balanced Secrets strategy.

        The agent_calling will essentially use the Max Secrets strategy, until it knows
        all the secrets. It will then use the Min Secrets strategy.

        Input arguments:
        agent_calling -- The agent currently trying to make a call
        callable_agents -- The list of agents agent_calling can call.

        Output:
        connection_agent -- The agent that the agent_calling will exchange secrets with.
        """
        if len(agent_calling.secrets) == self.num_agents:
            return self.determine_agent_min_secrets(agent_calling, callable_agents)
        return self.determine_agent_max_secrets(agent_calling, callable_agents)

    def add_called_agents(self, agent_calling, connection_agent, called_agents):
        """Adds the currently calling agents agent_calling and connection_agent to the
        called_agents set. It also updates the 'called' list of both agents.
    
        Input arguments:
        agent_calling -- The agent that made a call
        connection_agent -- The agent that was called by agent_calling
        called_agents -- The set of agents that were called or have made a call
            This set of called agents is subtracted from the list of callable agents later.
            Every timestep, the called_agents set resets.

        Output: called_agents -- The set of called agents which cannot be called again
            during this timestep.
        """
        called_agents.add(agent_calling)
        called_agents.add(connection_agent)
        agent_calling.called.append(connection_agent)
        connection_agent.called.append(agent_calling)
        return called_agents

    def agents_interact(self, agent_calling, connection_agent):
        """Updates the incoming secrets of both the agent_calling and connection_agent.

        The incoming secrets is used so that each agent's secrets information is not updated
        until the end of the iteration. Otherwise the program's sequential nature would
        cause errors. This function also updates the 'secrets_known' arrays of both agents.
        This array is used in the Min Secrets, Max Secrets and Balanced Secrets strategies,
        and it allows each agent to keep track of how many secrets each other agent has.
        The agents will also communicate these numbers between each other.

        Input arguments:
        agent_calling -- The agent currently trying to make a call
        connection_agent -- The agent that is going to be called
        """
        agent_calling.incoming_secrets.update(connection_agent.secrets)
        connection_agent.incoming_secrets.update(agent_calling.secrets)
        agent_calling.update_secrets_known(connection_agent.secrets_known)
        connection_agent.update_secrets_known(agent_calling.secrets_known)
        if "Token" in self.strategy:
            agent_calling.give_token(connection_agent)
        if "Spider" in self.strategy:
            connection_agent.give_token(agent_calling)

    def exchange_secrets(self, timesteps_taken):
        """Exchange secrets between agents in the self.agents list.

        Initialises a set named 'called', which keeps track of which
        agents have already exchanged secrets this time-step.
        Then it shuffles the list of agents so each time-step will not
        start with the same agent. This shuffling ensures fairness.
        For each agent in the list of agents, the 'callable_agents' list is computed.
        This 'callable_agents' list will consist of the list of agents, minus the
        agents that are not eligible to be called in this time-step (for
        this particular agent). If the 'callable_agents' list still contains
        agents after pruning it, a random agent will be chosen from this list
        to exchange secrets with.
        """
        shuffled_agents = self.agents.copy()
        # Connections will store the connections between agents this timestep
        self.connections = []
        called = set()

        # We shuffle the agents to fairly determine who goes first
        rn.shuffle(shuffled_agents)
        for agent in shuffled_agents:
            # If the agent is already in the called set, we skip it
            if agent in called or agent.has_token is False:
                continue

            callable_agents = self.make_callable_list(agent, called)

            # Only try to call if there are agents to call
            if len(callable_agents) > 0:
                rn.shuffle(callable_agents)
                connection_agent = self.determine_agent(
                    agent, callable_agents, timesteps_taken)

                if connection_agent in called:
                    continue

                called = self.add_called_agents(
                    agent, connection_agent, called)
                self.agents_interact(agent, connection_agent)

                # The connection is stored for both agents,
                # so they wont call each other again if the strategy is CMO
                agent.store_connections(connection_agent)
                connection_agent.store_connections(agent)

                # Add the connection in the controller,
                # so we can highlight it in the UI
                self.connections.append(
                    (min(agent.id, connection_agent.id), max(agent.id, connection_agent.id)))

        for agent in self.agents:
            agent.update_secrets()
