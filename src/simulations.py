import csv
import os
import os.path
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import plotly.graph_objs as go
import sys
import time

from modelController.controller import Controller

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

def simulate_generator(num_agents, strategy, num_sim=1000):
    """Performs num_sim simulation of the program with certain values for the parameters.
    
    This function however, will not save results to a csv file. It is a generator, meaning
    it yields the timesteps counters after every iteration.
    """
    timesteps_counters = {}
    mc = Controller(num_agents, strategy)
    mc.update(num_agents, strategy)

    for i in range(num_sim):
        mc.start_simulation(print_message=False)
        while not mc.simulation_finished:
            mc.simulate(print_message=False)

        if mc.simulation_finished:
            if str(mc.timesteps_taken) in timesteps_counters:
                timesteps_counters[str(mc.timesteps_taken)] += 1
            else:
                timesteps_counters[str(mc.timesteps_taken)] = 1
            mc.reset_simulation(print_message=False)
            mc.update(num_agents, strategy)
        yield timesteps_counters

def make_histogram_for_frontend(counters):
    """Makes histograms for in the UI.
    
    These histograms are made with plotly, and is actually made by making a Bar
    Chart. This is done because we already know the exact counts.
    Arguments:
        counters -- the dictionary with as keys the timesteps taken and as values
        the counts of those timesteps taken
    """
    timesteps = tuple(counters.keys())
    counts = tuple(counters.values())
    fig = go.Figure(
        [go.Bar(x=timesteps, y=counts)],
        layout=go.Layout(
            title="Counts of #Timesteps Taken",
            xaxis_title = "Timesteps Taken",
            yaxis_title = "Counts",
            autosize=False,
            width=500,
            height=500,
        )
    )
    return fig

def simulate(num_agents, strategy, sims_filepath, num_sim=1000):
    """Perform num_sim simulations of the program with certain values for the parameters.

    Input arguments:
    num_agents -- The number of agents in a simulation
    strategy -- The strategy the agents will use
    sims_filepath -- The filepath where the dataframe is saved into
    num_sim -- The number of simulations per configuration

    This function performs the simulations, and record the number of timesteps it takes for each
    iteration, after which the average and standard deviation of the number of timesteps taken
    can be computed.
    """
    df = create_df(sims_filepath)
    new_rows = pd.DataFrame(columns=['Num Simulations', 'Num Agents', 'Strategy', 'Call Protocol', 'Timesteps Taken'])

    mc = Controller(num_agents, strategy)
    mc.update(num_agents, strategy)
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
                                 "Timesteps Taken": mc.timesteps_taken})
            new_rows = new_rows.append(new_row, ignore_index=True)
            total_timesteps_taken += mc.timesteps_taken
            mc.reset_simulation(print_message=False)
            mc.update(num_agents, strategy)

        # Prints the progress
        print(f"Num agents: {num_agents}, Strategy: {strategy} -- Iteration: {i+1} / {num_sim}", end='\r')
    print()

    df = df.append(new_rows)
    df.to_csv(sims_filepath)
    # Select the rows of the DataFrame that use the settings given as arguments to this func (simulate)
    res_df = df.loc[(df['Num Agents'] == num_agents) & (df['Strategy'] == strategy)]
    print(f"There are {len(res_df['Timesteps Taken'])} entries in the csv file, using these settings.")
    average_timesteps = res_df['Timesteps Taken'].mean(skipna=True)
    std_timesteps = res_df['Timesteps Taken'].std(skipna=True)
    print("Average timesteps taken with these settings: {:.4}".format(average_timesteps))
    print("Standard deviation of timesteps taken with these settings: {:.4}".format(std_timesteps))
    print()


def make_histogram(num_agents, strategy, df_filepath):
    """This function creates a histogram based 
    on the arguments given and saves it in the data folder.
    
    Input arguments:
    num_agents -- Num agents in the simulation (and graphs)
    strategy -- Strategy used by agents in the simulation
    df_filepath -- The DataFrame object is stored in a csv file.
        This is the filepath to that csv file.
    """
    df = pd.read_csv(df_filepath, index_col=0)
    df = df.loc[(df['Num Agents'] == num_agents) & (df['Strategy'] == strategy)]
    num_bins = max(df["Timesteps Taken"]) - min(df["Timesteps Taken"])
    fig = plt.figure()
    ax = df["Timesteps Taken"].hist(bins=num_bins, density=1, align='left', histtype='bar', rwidth=0.9)
    plt.title(f"Strategy: {strategy}, Number of agents: {num_agents}")
    plt.xlabel(f"Time-steps taken")
    plt.ylabel(f"Percentage")

    filename = f"data/{strategy}_{num_agents}_agents_hist.png"
    plt.savefig(filename)
    plt.close(fig)


if __name__ == "__main__":
    ################################################## Uncomment for simulations!
    if len(sys.argv) != 2:
        exit("wrong number of arguments, give filename as an argument")

    file_name = sys.argv[1]

    data_dir = "data"
    sims_filepath = f"{data_dir}/{file_name}.csv"
    if not os.path.isdir(data_dir):
        os.mkdir(data_dir)

    # These are the settings of the simulations that you want to test.
    num_agents_values = [5]
    strategies = ["Random", "Learn-New-Secrets", "Bubble", "Mathematical",
     "Call-Me-Once", "Most-useful" , "Min-Secrets", "Max-Secrets", "Token", "Spider"]

    for num_agents in num_agents_values:
        for strategy in strategies:
            start_time = time.time()
            try:
                simulate(num_agents, strategy, sims_filepath)
                make_histogram(num_agents, strategy, sims_filepath)
            except Exception as e:
                print(f"Something went wrong during {strategy}")
                print(e)
                continue
            end_time = time.time() - start_time
            print(f"Strat {strategy}, n = {num_agents}, took {end_time} seconds")
    #############################################################################
