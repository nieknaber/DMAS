import csv
import os.path

from modelController.model_controller import ModelController

def write_to_csv(num_sim, num_agents, strategy, call_protocol, average_timesteps):
    fieldnames = ['Number of Simulations', 'Number of Agents', 'Strategy', 'Call Protocol', 'Average Number of Timesteps']
    if os.path.exists('data.csv') :
        with open('data.csv', 'a') as csvfile:
            writer = csv.DictWriter(csvfile,fieldnames=fieldnames)
            writer.writerow({'Number of Simulations' : num_sim, 'Number of Agents' : num_agents, 'Strategy' : strategy, 'Call Protocol' : call_protocol, 'Average Number of Timesteps' : average_timesteps })

    else :
        with open('data.csv', 'w') as csvfile:
            writer = csv.DictWriter(csvfile,fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow({'Number of Simulations' : num_sim, 'Number of Agents' : num_agents, 'Strategy' : strategy, 'Call Protocol' : call_protocol, 'Average Number of Timesteps' : average_timesteps })


def simulate(num_sim, num_agents, strategy, call_protocol) :
    mc = ModelController(num_agents, strategy, call_protocol)
    timestepsTaken = 0;
    for i in range(num_sim):
        mc.start_simulation()
        while not mc.simulation_finished :
            mc.simulate_from_ui()
        if mc.simulation_finished :
            timestepsTaken += mc.timesteps_taken
            mc.reset_simulation()

    average_timesteps = timestepsTaken/num_sim

    write_to_csv(num_sim, num_agents, strategy, call_protocol, average_timesteps)
