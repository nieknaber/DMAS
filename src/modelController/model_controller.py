from src.modelController.agent import Agent
import random as rn


class ModelController:

    def __init__(self, num_agents, num_connections):
        self.num_agents = num_agents
        self.num_connections = num_connections
        self.agents = []
        self.init_agents()
        # self.agents = np.empty(self.num_agents, dtype=object)
        # self.agentsRandom = []

    def init_agents(self):
        for i in range(self.num_agents):
            self.agents.append(Agent(i, f"Init Message {i}", "Placeholder strategy", self.num_agents))
            # self.agentsRandom.append(self.agents[i])  # random list for shuffling

    def update(self, num_agents, num_connections):
        self.num_agents = num_agents
        self.num_connections = num_connections
        self.init_agents()

    def make_connections(self):
        for agent in self.agents:
            temp_list = self.agents.copy()
            temp_list.remove(agent)
            connection_agent = rn.choice(temp_list)
            self.make_single_connection(agent, connection_agent)

    def make_single_connection(self, agent1, agent2):
        arr1 = agent1.get_secrets()
        arr2 = agent2.get_secrets()

        agent1.update_secrets(arr2)
        agent2.update_secrets(arr1)


if __name__ == "__main__":
    # For testing purposes only
    mc = ModelController(num_agents=10, num_connections=1)
    mc.make_connections()
    for agent in mc.agents:
        agent.print_info()
