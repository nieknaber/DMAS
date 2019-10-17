from modelController.agent import Agent
from modelController.model import Model
import numpy as np


class Controller:

    def __init__(self, num_agents, strategy, call_protocol):
        """Initialises the controller.

        Arguments:
        num_agents -- The number of agents that should be in the simulation.
        num_connections -- The number of maximum connections an agent can make
            during one time-step.
        strategy -- The strategy the agents will use.
        """

        self.model = Model(strategy, call_protocol)
        self.timesteps_taken = 0
        self.simulation_finished = False
        self.started = False
        self.paused = False

    def init_agents(self):
        """Re-initialises the agents list and fills it with num_agents agents."""
        self.model.agents = []
        for i in range(self.model.num_agents):
            self.model.agents.append(Agent(i, f"Secret {i}", self.model.num_agents))
            self.model.all_secrets.add(f"Secret {i}")

        self.model.numpyAgents = np.array(self.model.agents)

    def update(self, num_agents, strategy, call_protocol):
        """This function updates the num_agents, num_connections and strategy fields.
        Then it calls the self.init_agents function so it re-initialises the agents list.

        Arguments:
        num_agents -- The number of agents that should be in the simulation.
        num_connections -- The number of maximum connections an agent can make
            during one time-step.
        strategy -- The strategy the agents will use.
        """
        if not self.started:
            self.model.call_protocol = call_protocol
            self.model.strategy = strategy
            self.model.all_secrets = set()
            self.model.num_agents = num_agents
            self.init_agents()

    def start_simulation(self, print_message=True):
        """Starts the simulation. Sets the started flag to True.

        Argument:
        print_message -- If True (which is the default), starting the simulation
            will also print a message to stdout.
        """
        if print_message:
            print("Started simulation!")
            print('Strategy = ' + self.model.strategy)
            for agent in self.model.agents:
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

    def reset_simulation(self, print_message=True):
        """Resets the simulation (there is a button on the UI calling this function).

        It resets it by calling the self.__init__ function with the current values
        for num_agents, num_connections and strategy as arguments.
        Argument:
        print_message -- IF set to False, the message 'Simulation reset!' will
            not be printed to stdout
        """
        self.__init__(self.model.num_agents, self.model.strategy, self.model.call_protocol)
        if print_message:
            print("Simulation reset!")

    def print_agents_secrets(self):
        """Outputs the number of secrets each agent has learned to stdout."""
        for agent in self.model.agents:
            print(len(agent.secrets), end='\t')
        print()

    def simulate(self, print_message=True):
        """If the simulation has started and has not finished yet, this
        function will perform one time-step of the simulation.

        It exchanges secrets, prints the number of secrets to stdout,
        increases the number of time-steps taken and checks whether
        the simulation has finished during this time-step.
        The simulation is finished if every agent knows all secrets.

        If the keyword argument 'print_secrets' is set to False, this function
        will not print out the secrets of all the agents to stdout. This is useful
        when doing the simulations without the use of the UI for statistical purposes.
        """
        if self.started and not self.simulation_finished and not self.paused:
            self.model.exchange_secrets(self.timesteps_taken)
            if print_message:
                self.print_agents_secrets()

            self.timesteps_taken += 1

            broken_out_of_loop = False
            # If all agents know each secret, simulation is finished
            for agent in self.model.agents:
                if len(agent.secrets) < self.model.num_agents:
                    broken_out_of_loop = True
                    break

            if not broken_out_of_loop:
                self.simulation_finished = True
                if print_message:
                    print(f"End of simulation, after {self.timesteps_taken} time-steps.")
