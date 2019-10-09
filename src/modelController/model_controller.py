from modelController.agent import Agent
import random as rn
import threading
import time


class ModelController:

    def __init__(self, num_agents, num_connections, strategy):
        self.num_agents = num_agents
        self.num_connections = num_connections
        self.agents = []
        self.timesteps_taken = 0
        self.simulation_finished = False
        self.started = False
        self.paused = False
        self.connections = []
        self.strategy = strategy
        self.init_agents()

    def init_agents(self):
        self.agents = []
        for i in range(self.num_agents):
            self.agents.append(Agent(i, f"Secret {i}", self.strategy, self.num_agents))

    def update(self, num_agents, num_connections, strategy):
        if not self.started:
            self.num_agents = num_agents
            self.num_connections = num_connections
            self.strategy = strategy
            self.init_agents()

    def start_simulation(self):
        print("Started simulation!")
        print('Strategy = ' +  self.agents[0].strategy)
        for agent in self.agents:
            print(agent, end='\t')
        print()
        self.started = True

    def resume_simulation(self):
        print("Resumed simulation!")
        self.paused = False

    def pause_simulation(self):
        print("Paused simulation!")
        self.paused = True

    def stop_simulation(self):
        self.started = False
        self.paused = False
        print("Stopped simulation!")

    def reset_simulation(self):
        self.__init__(self.num_agents, self.num_connections, self.strategy)
        print("Simulation reset!")

    def print_agents_secrets(self):
        for agent in self.agents:
            print(len(agent.secrets), end='\t')
        print()

    # TODO: We should refactor this function later
    def exchange_secrets(self):
        called = set()
        shuffled_agents = self.agents.copy()
        self.connections = []  # Connections will store the connections between agents this timestep

        # We shuffle the agents to fairly determine who goes first
        rn.shuffle(shuffled_agents)
        for agent in shuffled_agents:
            # If the agent is already in the called set, we skip it
            if agent in called or agent.has_token == False:
                continue
                    
            # We need to remove the called agents from the callable agents
            callable = self.agents.copy()  # If we are not going for a fully connected graph, we should change this line
            callable.remove(agent)
            for called_agent in called:
                if called_agent in callable:
                    callable.remove(called_agent)

            if agent.strategy == 'Token-improved' or agent.strategy == 'Spider-improved':
                for other_agent in self.agents:
                    if agent.secrets_known[other_agent.id] == len(self.agents) and other_agent in callable:
                        callable.remove(other_agent)

            # Call-Me-Once strategy
            if agent.strategy == 'Call-Me-Once':
                # If the agent has called the other agent already
                # another agent is randomly chosen
                for connected_agent in agent.connections:
                    if connected_agent in callable:
                        callable.remove(connected_agent)

            if agent.strategy == 'Learn-New-Secrets':
                # If an agent has the same set of secrets as this agent, it is removed from the callable list
                for other_agent in self.agents:
                    if other_agent.secrets == agent.secrets and other_agent in callable:
                        callable.remove(other_agent)

            # Only try to call if there are agents to call
            if len(callable) > 0:
                rn.shuffle(callable)
                connection_agent = None
                if agent.strategy == 'Call-Max-Secrets':
                    max_known = 0
                    for callable_agent in callable:
                        if agent.secrets_known[callable_agent.id]>max_known:
                            connection_agent = callable_agent
                            max_known = agent.secrets_known[callable_agent.id]

                if agent.strategy == 'Call-Min-Secrets':
                    min_known = self.num_agents+1
                    for callable_agent in callable:
                        if agent.secrets_known[callable_agent.id]<min_known:
                            connection_agent = callable_agent
                            min_known = agent.secrets_known[callable_agent.id]

                if agent.strategy == 'Call-Best-Secrets':
                    if len(agent.secrets) == self.num_agents:
                        min_known = self.num_agents+1
                        for callable_agent in callable:
                            if agent.secrets_known[callable_agent.id]<min_known:
                                connection_agent = callable_agent
                                min_known = agent.secrets_known[callable_agent.id]
                    else:
                        max_known = 0
                        for callable_agent in callable:
                            if agent.secrets_known[callable_agent.id]>max_known:
                                connection_agent = callable_agent
                                max_known = agent.secrets_known[callable_agent.id]

                if connection_agent is None:
                    connection_agent = rn.choice(callable)

                # Prevent secrets from stacking during one timestep
                # (use incoming secrets instead of directly updating secrets)
                agent.incoming_secrets.update(connection_agent.secrets)
                connection_agent.incoming_secrets.update(agent.secrets)
                called.add(agent)
                called.add(connection_agent)
                agent.update_secrets_known(connection_agent.secrets_known)
                connection_agent.update_secrets_known(agent.secrets_known)

                if "Token" in agent.strategy:
                    agent.give_token(connection_agent)

                if "Spider" in agent.strategy:
                    connection_agent.give_token(agent)

                # The connection is stored for both agents, so they wont call each other again if the strategy is CMO
                agent.store_connections(connection_agent)
                connection_agent.store_connections(agent)

                # Add the connection in the controller, so we can highlight it in the UI
                self.connections.append((min(agent.id, connection_agent.id), max(agent.id, connection_agent.id)))

        for agent in self.agents:
            agent.update_secrets()

    def simulate_from_ui(self):
        if self.started and not self.simulation_finished:
            self.exchange_secrets()
            self.print_agents_secrets()
            self.timesteps_taken += 1

            broken_out_of_loop = False
            # If all agents know each secret, simulation is finished
            for agent in self.agents:
                if len(agent.secrets) < len(self.agents):
                    broken_out_of_loop = True
                    break

            if not broken_out_of_loop:
                self.simulation_finished = True
                print(f"End of simulation, after {self.timesteps_taken} time-steps.")