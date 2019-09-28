from modelController.agent import Agent
import random as rn
import threading
import time


class ModelController:

    def __init__(self, num_agents, num_connections):
        self.num_agents = num_agents
        self.num_connections = num_connections
        self.agents = []
        self.timesteps_taken = 0
        self.simulation_finished = False
        self.started = False
        self.paused = False
        self.connections = []
        self.init_agents()

    def init_agents(self):
        self.agents = []
        for i in range(self.num_agents):
            self.agents.append(Agent(i, f"Secret {i}", "Placeholder strategy", self.num_agents))

    def update(self, num_agents, num_connections):
        if not self.started:
            self.num_agents = num_agents
            self.num_connections = num_connections
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

    def print_agents_secrets(self):
        for agent in self.agents:
            print(len(agent.secrets), end='\t')
        print()

    def exchange_secrets(self):
        called = set()
        shuffled_agents = self.agents.copy()
        self.connections = []  # Connections will store the connections between agents this timestep

        # We shuffle the agents to fairly determine who goes first
        rn.shuffle(shuffled_agents)
        for agent in shuffled_agents:
            # If the agent is already in the called set, we skip it
            if agent in called:
                continue

            # We need to remove the called agents from the callable agents
            callable = self.agents.copy()  # IF we are not going for a fully connected graph, we should change this line
            callable.remove(agent)
            for called_agent in called:
                if called_agent in callable:
                    callable.remove(called_agent)

            # Only choose an agent if there is at least one callable agent
            if len(callable) > 0:
                connection_agent = rn.choice(callable)
                
                # Prevent secrets from stacking during one timestep 
                # (use incoming secrets instead of directly updating secrets)
                agent.incoming_secrets.update(connection_agent.secrets)
                connection_agent.incoming_secrets.update(agent.secrets)
                called.add(agent)
                called.add(connection_agent)
                # Add the connection, so we can highlight it in the ui
                self.connections.append((min(agent.id, connection_agent.id), max(agent.id, connection_agent.id)))

        for agent in self.agents:
            agent.update_secrets()

    def simulate_from_ui(self):
        # This function is not threaded and most likely better than simulate

        if self.started and not self.simulation_finished:
            # while not self.simulation_finished and not self.paused:
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

        return self.simulation_finished
            
            