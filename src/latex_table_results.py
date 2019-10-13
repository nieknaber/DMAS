"""This is a quick program to output the mean and standard deviations of the Timesteps Taken in LaTeX tabular format."""

import pandas as pd

if __name__ == "__main__":
	df_filename = "data/timesteps_data.csv"
	df = pd.read_csv(df_filename, index_col=0)

	strategies = ["Random", "Call-Me-Once", "Learn-New-Secrets",
                    "Bubble", "mathematical", "Token-improved",
                    "Spider-improved", "Call-Max-Secrets", "Call-Min-Secrets",
                    "Call-Best-Secrets", "Token", "Spider"]

	num_agents_values = [10, 50, 100, 500]

	call_protocol = "Standard"
	for strategy in strategies:
		average_timesteps = []
		std_timesteps = []
		for num_agents in num_agents_values:
			avg_sd_df = df.loc[(df['Num Agents'] == num_agents) & (df['Strategy'] == strategy) & (df['Call Protocol'] == call_protocol)]
			average_timesteps.append(f"{(avg_sd_df['Timesteps Taken'].mean(skipna=True)):.2f}")
			std_timesteps.append(f"{(avg_sd_df['Timesteps Taken'].std(skipna=True)):.2f}") 

		for num_agents, avg_timestep, std_timestep in zip(num_agents_values, average_timesteps, std_timesteps):
			print(f"{strategy}:{num_agents} \t | \t ${float(avg_timestep)} \\pm {float(std_timestep)}$")