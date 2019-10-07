# Gossip Problem - Group B20

This is a project made for the Design of Multi-Agent Systems course given by the University of Groningen. The gossip problem is a problem where each agent starts out with a unique secret, and the goal is for each agent to have all secrets. Each agent can communicate with one other agent during a single time-step. During this time-step, all secrets agent A knows can be given to agent B, and vice versa.

## Installation

After cloning this repository, some dependencies still need to be installed. If you do not have Python 3.7, it is possible some features of this project do not work in your environment. To download and install Python 3.7, click [this](https://www.python.org/downloads/) link.

Then use the package manager [pip3](https://pip.pypa.io/en/stable/) to install the other dependencies.

```bash
pip3 install numpy
pip3 install networkx
pip3 install dash
```

## Usage
To run the program, navigate to the DMAS-Gossip-Problem-B20/src/ directory and run start.py.

```bash
python3 start.py
```

This will cause the Dash app to be running on http://127.0.0.1:8050/.
Open up a browser and navigate to that URL or simply click on the link to view the current front-end.
The current front-end currently consists of some information about the project, 2 sliders that control 2 variables, a button and a graph. 
To start the simulation, press the "Start simulation" button. The simulation is not yet connected to the front-end, but there is output in the terminal.
