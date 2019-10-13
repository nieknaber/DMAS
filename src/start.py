"""start.py is the starting module for this program.

It initiates a controller and passes that controller to the UI.
"""

import view.ui as ui
from modelController.model_controller import ModelController


DEFAULT_NUM_AGENTS = 10
mc = ModelController(DEFAULT_NUM_AGENTS, "Random", "Standard")
ui.run_ui(mc, DEFAULT_NUM_AGENTS)
