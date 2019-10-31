"""start.py is the starting module for this program.

It initiates a controller and passes that controller to the UI.
"""

import view.ui as ui
from modelController.controller import Controller


DEFAULT_NUM_AGENTS = 10
mc = Controller(DEFAULT_NUM_AGENTS, "Random")
ui.run_ui(mc, DEFAULT_NUM_AGENTS)
