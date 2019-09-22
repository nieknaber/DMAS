# Gossip Problem

This is a project made for the Design of Multi-Agent Systems course given by the University of Groningen. The gossip problem is a problem where each agent starts out with a unique secret, and the goal is for each agent to have all secrets. Each agent can communicate with one other agent during a single time-step. During this time-step, all secrets agent A knows can be given to agent B, and vice versa.

## Installation

After cloning this repository, some dependencies still need to be installed. If you do not have Python 3.7, it is possible some features of this project do not work in your environment. To download and install Python 3.7, click [this](https://www.python.org/downloads/) link.

Then use the package manager [pip](https://pip.pypa.io/en/stable/) to install the other dependencies.

```bash
pip install numpy
pip install networkx
pip install dash
```

## Usage
To run the program, navigate to the DMAS/src/ directory and run start.py.

```bash
python start.py
```