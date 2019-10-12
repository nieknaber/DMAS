import csv
import os
import os.path
import pandas as pd

from modelController.model_controller import ModelController

# CURRENTLY NOT USED! PANDAS IS BETTER
# def write_to_csv(num_sim, num_agents, strategy, call_protocol, average_timesteps, filename='data.csv'):
#     fieldnames = ['Number of Simulations', 'Number of Agents', 'Strategy', 'Call Protocol', 'Average Number of Timesteps']
#     if os.path.exists(filename) :
#         with open(filename, 'a') as csvfile:
#             writer = csv.DictWriter(csvfile,fieldnames=fieldnames)
#             writer.writerow({'Number of Simulations' : num_sim, 'Number of Agents' : num_agents, 'Strategy' : strategy, 'Call Protocol' : call_protocol, 'Average Number of Timesteps' : average_timesteps })

#     else :
#         with open(filename, 'w') as csvfile:
#             writer = csv.DictWriter(csvfile,fieldnames=fieldnames)
#             writer.writeheader()
#             writer.writerow({'Number of Simulations' : num_sim, 'Number of Agents' : num_agents, 'Strategy' : strategy, 'Call Protocol' : call_protocol, 'Average Number of Timesteps' : average_timesteps })

def create_df(filepath):
    """Reads or creates a pandas DataFrame."""
    if not os.path.exists(filepath):
        print(f"{filepath} does not exist, making new DataFrame")
        df = pd.DataFrame(columns=['Num Simulations', 'Num Agents', 'Strategy', 'Call Protocol', 'Timesteps Taken'])
    else:
        print(f"Reading dataframe from {filepath}")
        # First column is the index column
        df = pd.read_csv(filepath, index_col=0)
    return df

def simulate(num_agents, strategy, call_protocol, num_sim=1000):
    """Perform num_sim simulations of the program with certain values for the parameters.

    Input arguments:
    num_sim -- The number of simulations per configuration
    num_agents -- The number of agents in a simulation
    strategy -- The strategy the agents will use
    call_protocol -- Can be either 'Standard' or 'Not-Standard',
        'Standard' means that an agent - after calling another agent which was unavailable -
        can still call another agent from his callable list, whereas 'Not-Standard' does not
        allow this. Calling an agent that is already calling someone else is punished this way

    This function performs the simulations, and record the number of timesteps it takes for each
    iteration, after which the average and standard deviation of the number of timesteps taken
    can be computed.
    """
    data_dir = "data"
    sims_filepath = f"{data_dir}/timesteps_data.csv"
    if not os.path.isdir(data_dir):
        os.mkdir(data_dir)
    df = create_df(sims_filepath)
    new_rows = pd.DataFrame(columns=['Num Simulations', 'Num Agents', 'Strategy', 'Call Protocol', 'Timesteps Taken'])

    mc = ModelController(num_agents, strategy, call_protocol)
    # Start the simulations and record the timesteps taken

    total_timesteps_taken = 0
    for i in range(num_sim):
        mc.start_simulation(print_message=False)
        while not mc.simulation_finished:
            mc.simulate(print_message=False)

        if mc.simulation_finished:
            new_row = pd.Series({"Num Simulations": num_sim,
                                 "Num Agents": num_agents, 
                                 "Strategy": strategy, 
                                 "Call Protocol": call_protocol,
                                 "Timesteps Taken": mc.timesteps_taken})
            new_rows = new_rows.append(new_row, ignore_index=True)
            total_timesteps_taken += mc.timesteps_taken
            mc.reset_simulation(print_message=False)

        # Prints the progress
        print(f"Num agents: {num_agents}, Strategy: {strategy} -- Iteration: {i+1} / {num_sim}", end='\r')
    print()

    df = df.append(new_rows)
    df.to_csv(sims_filepath)

    # Select the rows of the DataFrame that use the settings given as arguments to this func (simulate)
    res_df = df.loc[(df['Num Agents'] == num_agents) & (df['Strategy'] == strategy) & (df['Call Protocol'] == call_protocol)]
    print(f"Settings:\nNum Agents: {num_agents}\nStrategy: {strategy}\nCall Protocol: {call_protocol}")
    print(f"There are {len(res_df['Timesteps Taken'])} entries in the csv file, using these settings.")
    average_timesteps = res_df['Timesteps Taken'].mean(skipna=True)
    std_timesteps = res_df['Timesteps Taken'].std(skipna=True)
    print("Average timesteps taken with these settings: {:.4}".format(average_timesteps))
    print("Standard deviation of timesteps taken with these settings: {:.4}".format(std_timesteps))


def make_histogram(num_agents, strategy, call_protocol, csv_filename):
    """This function creates a histogram based on the arguments given.

    Input arguments:
    num_agents --
    strategy --
    call_protocol --
    csv_filename --
    """
    pass

if __name__ == "__main__":
    # Try the simulations for these values of num_agents
    num_agents_values = [3, 4, 5, 10, 15, 25, 50, 75, 100]
    strategies = ["Random", "Call-Me-Once", "Learn-New-Secrets"]

    for num_agents in num_agents_values:
        for strategy in strategies:
            simulate(num_agents, strategy, "Standard")
