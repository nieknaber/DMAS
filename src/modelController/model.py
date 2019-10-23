import random as rn


class Model:

    def __init__(self, strategy, call_protocol):
        """Initialises the controller.

        Arguments:
        num_agents -- The number of agents that should be in the simulation.
        num_connections -- The number of maximum connections an agent can make
            during one time-step.
        strategy -- The strategy the agents will use.
        """
        self.agents = []
        self.num_agents = 0
        self.connections = []
        self.strategy = strategy
        self.call_protocol = call_protocol
        self.all_secrets = set()

    def make_callable_set(self, agent_calling, called_agents):
        callable_agents = self.agents.copy()
        callable_agents.remove(agent_calling)
        if self.call_protocol == 'Standard':
            return self.remove_agents_calling(callable_agents, called_agents)
        # TODO: Either remove or improve/change this strategy
        # if self.strategy == 'Token-improved' or self.strategy == 'Spider-improved':
        #     return self.remove_completed_agents(callable_agents, agent_calling)
        if self.strategy == 'Call-Me-Once':
            return self.remove_called_agents(callable_agents, agent_calling)
        if self.strategy == 'Learn-New-Secrets':
            return self.remove_agents_same_secrets(callable_agents, agent_calling)
        return callable_agents

    def remove_agents_calling(self, callable_agents, called_agents):
        for called_agent in called_agents:
            if called_agent in callable_agents:
                callable_agents.remove(called_agent)
        return callable_agents

    # TODO: Remove this function or change it so that it is distributed
    def remove_completed_agents(self, callable_agents, agent_calling):
        for other_agent in self.agents:
            if agent_calling.secrets_known[other_agent.id] == self.num_agents:
                if other_agent in callable_agents:
                    callable_agents.remove(other_agent)
        return callable_agents

    # Call-Me-Once strategy
    def remove_called_agents(self, callable_agents, agent_calling):
        for connected_agent in agent_calling.connections:
            if connected_agent in callable_agents:
                callable_agents.remove(connected_agent)
        return callable_agents

    # Learn new secrets strategy
    def remove_agents_same_secrets(self, callable_agents, agent_calling):
        # If an agent has the same set of secrets as this agent, it is removed from the callable list
        for other_agent in self.agents:
            if f"Secret {other_agent.id}" in agent_calling.secrets:
                if other_agent in callable_agents:
                    callable_agents.remove(other_agent)
        return callable_agents

    def determine_agent(self, agent_calling, callable_agents, timesteps_taken):
        connection_agent = None
        if self.strategy == 'Bubble':
            self.determine_agent_bubble(agent_calling, timesteps_taken)
        elif self.strategy == 'Mathematical':
            self.determine_agent_math(
                agent_calling, callable_agents, timesteps_taken)
        elif self.strategy == 'Min-Secrets':
            self.determine_agent_min_secrets(agent_calling, callable_agents)
        elif self.strategy == 'Max-Secrets':
            self.determine_agent_max_secrets(agent_calling, callable_agents)
        elif self.strategy == 'Most-useful':
            self.determine_agent_best_secrets(agent_calling, callable_agents)
        elif self.strategy == 'Divide':
            self.determine_agent_divide(agent_calling, callable_agents)
        if connection_agent is None:
            connection_agent = rn.choice(callable_agents)
        return connection_agent

    def determine_agent_bubble(self, agent_calling, timesteps_taken):
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

    # idx of agent that is going to be called
    # agent.id + 1 because we want to do math with indexes > 0. In the end we correct by subtracting 1.
    # timesteps_taken + 2 because 0 results in idx = 0 every time, and if we would do plus 1, all agents
    # would try to call themselves in the first time step
    def determine_agent_math(self, agent_calling, callable_agents, timesteps_taken):
        idx = (agent_calling.id + 1) * (timesteps_taken + 2) - 1
        # get first agent, starting from this id, that is still available
        return self.solve(idx % self.num_agents, callable_agents)

    def find(self, callable, idx):
        for agent in callable:
            if agent.id == idx:
                return True
        return False

    def solve(self, idx, callable):
        if self.find(callable, idx):
            return self.numpyAgents[idx]
        return self.solve((idx + 1) % self.num_agents, callable)

    def determine_agent_min_secrets(self, agent_calling, callable_agents):
        connection_agent = None
        min_known = self.num_agents + 1
        for callable_agent in callable_agents:
            if agent_calling.secrets_known[callable_agent.id] < min_known:
                connection_agent = callable_agent
                min_known = agent_calling.secrets_known[callable_agent.id]
        return connection_agent

    def determine_agent_max_secrets(self, agent_calling, callable_agents):
        connection_agent = None
        max_known = 0
        for callable_agent in callable_agents:
            if agent_calling.secrets_known[callable_agent.id] > max_known:
                connection_agent = callable_agent
                max_known = agent_calling.secrets_known[callable_agent.id]
        return connection_agent

    def determine_agent_best_secrets(self, agent_calling, callable_agents):
        if len(agent_calling.secrets) == self.num_agents:
            return self.determine_agent_min_secrets(agent_calling, callable_agents)
        return self.determine_agent_max_secrets(agent_calling, callable_agents)

    def determine_agent_divide(self, agent_calling, callable_agents):
        for target_agent in agent_calling.call_target_solved():
            if target_agent in callable_agents:
                return target_agent
        for target_agent in agent_calling.call_targets:
            if target_agent in callable_agents:
                return target_agent

    def add_called_agents(self, agent_calling, connection_agent, called_agents):
        called_agents.add(agent_calling)
        called_agents.add(connection_agent)
        agent_calling.called.append(connection_agent)
        connection_agent.called.append(agent_calling)
        return called_agents

    def agents_interact(self, agent_calling, connection_agent):
        # Prevent secrets from stacking during one timestep
        # (use incoming secrets instead of directly updating secrets)
        agent_calling.incoming_secrets.update(connection_agent.secrets)
        connection_agent.incoming_secrets.update(agent_calling.secrets)
        agent_calling.update_secrets_known(connection_agent.secrets_known)
        connection_agent.update_secrets_known(agent_calling.secrets_known)
        if self.strategy == 'Divide':
            self.interact_divide()
        if "Token" in self.strategy:
            agent_calling.give_token(connection_agent)
        if "Spider" in self.strategy:
            connection_agent.give_token(agent_calling)

    def interact_divide(self, agent_calling, connection_agent):
        needed_secrets_agent = set()
        needed_secrets_connection_agent = set()
        overlap = []

        for secret_needed in self.all_secrets:
            if secret_needed not in agent_calling.secrets:
                overlap.append(secret_needed)
            elif secret_needed in agent_calling.target_secrets():
                if secret_needed in connection_agent.target_secrets():
                    overlap.append(secret_needed)
                else:
                    needed_secrets_agent.add(secret_needed)
            else:
                needed_secrets_connection_agent.add(secret_needed)

        overlap = tuple(overlap)
        needed_secrets_agent.add(overlap[:len(overlap) // 2])
        needed_secrets_connection_agent.add(overlap[len(overlap) // 2:])

        agent_calling.call_targets.update(
            {connection_agent: needed_secrets_agent})
        connection_agent.call_targets.update(
            {agent_calling: needed_secrets_connection_agent})

    def exchange_secrets(self, timesteps_taken):
        """Exchange secrets between agents in the self.agents list.

        Initialises a set named 'called', which keeps track of which
        agents have already exchanged secrets this time-step.
        Then it shuffles the list of agents so each time-step will not
        start with the same agent. This way is more fair.
        For each agent in the list of agents, the 'callable' list is computed.
        This 'callable' list will consist of the list of agents, minus the
        agents that are not eligible to be called in this time-step (for
        this particular agent). If the 'callable' list still contains
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

            callable = self.make_callable_set(agent, called)

            # Only try to call if there are agents to call
            if len(callable) > 0:
                rn.shuffle(callable)
                connection_agent = self.determine_agent(
                    agent, callable, timesteps_taken)

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
