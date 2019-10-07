from modelController.agent import Agent
import random as rn
import threading
import time


class ModelController:

    def __init__(self, num_agents, num_connections, strategy):
        """Initialises the controller.

        Arguments:
        num_agents -- The number of agents that should be in the simulation.
        num_connections -- The number of maximum connections an agent can make
            during one time-step.
        strategy -- The strategy the agents will use.
        """
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
        """Re-initialises the agents list and fills it with num_agents agents."""
        self.agents = []
        for i in range(self.num_agents):
            self.agents.append(Agent(i, f"Secret {i}", self.strategy, self.num_agents))

    def update(self, num_agents, num_connections, strategy):
        """This function updates the num_agents, num_connections and strategy fields.
        Then it calls the self.init_agents function so it re-initialises the agents list.

        Arguments:
        num_agents -- The number of agents that should be in the simulation.
        num_connections -- The number of maximum connections an agent can make
            during one time-step.
        strategy -- The strategy the agents will use.
        """
        if not self.started:
            self.num_agents = num_agents
            self.num_connections = num_connections
            self.strategy = strategy
            self.init_agents()

    def start_simulation(self):
        """Starts the simulation.

        Outputs the starting messages to stdout and sets the started flag to True.
        """
        print("Started simulation!")
        print('Strategy = ' +  self.agents[0].strategy)
        for agent in self.agents:
            print(agent, end='\t')
        print()
        self.started = True

    def resume_simulation(self):
        """Resumes the simulation if it was paused. Sets the paused flag to False."""
        print("Resumed simulation!")
        self.paused = False

    def pause_simulation(self):
        """Pauses the simulation if it was not paused. Sets the paused flag to True."""
        print("Paused simulation!")
        self.paused = True

    def stop_simulation(self):
        """Stops the simulation if it is finished.

        Sets both the started and paused flags to False.
        """
        self.started = False
        self.paused = False
        print("Stopped simulation!")

    def reset_simulation(self):
        """Resets the simulation (there is a button on the UI calling this function).

        It resets it by calling the self.__init__ function with the current values
        for num_agents, num_connections and strategy as arguments.
        """
        self.__init__(self.num_agents, self.num_connections, self.strategy)
        print("Simulation reset!")

    def print_agents_secrets(self):
        """Outputs the number of secrets each agent has learned to stdout."""
        for agent in self.agents:
            print(len(agent.secrets), end='\t')
        print()

    # TODO: We should refactor this function later
    def exchange_secrets(self):
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
                    if len(other_agent.secrets) == len(self.agents) and other_agent in callable:
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
                connection_agent = rn.choice(callable)
                # Prevent secrets from stacking during one timestep
                # (use incoming secrets instead of directly updating secrets)
                agent.incoming_secrets.update(connection_agent.secrets)
                agent.incoming_secrets.update(connection_agent.secrets)
                connection_agent.incoming_secrets.update(agent.secrets)
                called.add(agent)
                called.add(connection_agent)

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
        """If the simulation has started and has not finished yet, this
        function will perform one time-step of the simulation.

        It exchanges secrets, prints the number of secrets to stdout,
        increases the number of time-steps taken and checks whether
        the simulation has finished during this time-step.
        The simulation is finished if every agent knows all secrets.
        """
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

