import view.ui as ui
from modelController.model_controller import ModelController


DEFAULT_NUM_AGENTS = 10
DEFAULT_NUM_CONNECTIONS = 1

mc = ModelController(DEFAULT_NUM_AGENTS, DEFAULT_NUM_CONNECTIONS)
ui.run_ui(mc, DEFAULT_NUM_AGENTS, DEFAULT_NUM_CONNECTIONS)



