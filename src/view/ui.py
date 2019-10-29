"""
The app layout is defined in layout.py. Dash allows to specify the HTML and CSS
in pythonic ways, which is done here. There are some callback functions, denoted
with the @app-callback decorators that change the Dash app in different ways as it
is running. Most callbacks are called when the user interacts with the UI. The
render_graph callback is also called every 'update_interval'.
"""

import networkx as nx
import dash
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import math
from simulations import simulate_generator, make_histogram_for_frontend
import view.layout as layout

# external CSS stylesheets
external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    {
        'href': 'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css',
        'rel': 'stylesheet',
    }
]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

update_interval = 2000  # 2000 ms = 2 s
default_num_agents = 10

# HTML Layout for the Dash-app
app.layout = layout.layout(default_num_agents, update_interval)
    
# Global variables used in render_graph, this has to be used since an output can only have 1 callback
# But we need to save the states
num_nodes_state = 0
base_figure = go.Figure()
G = nx.Graph()
computing_histogram = False
generator = None
num_sims = 1000
timesteps_counter = {}                  

def run_ui(ctrl, def_num_agents):
    """Runs the Dash UI, which is displayed in a web-browser."""
    global controller
    global default_num_agents
    controller = ctrl
    default_num_agents = def_num_agents
    app.run_server(debug=True)

# This has to be such a big function because a Dash output can only have one callback connected to it.
# And since we want to update the graph with most of what we do, we have to put all that logic in this function.
@app.callback(
    [Output('Graph','figure'),
    Output('timestep', 'children')],
    [Input('num_nodes','value'),
    Input('interval_component','n_intervals'),
    Input('strategy','value'),
    Input('call_protocol','value')])
def render_graph(num_nodes, n_intervals, strategy, call_protocol):
    """Creates the nodes-and-edges graph that is displayed in the web-browser.

    The decorator specifies which inputs and outputs this function has.
    Whenever one of the inputs changes in the Dash-app, this function is called.
    The inputs are:
        num_nodes -- The number of agents in the simulation (slider in Dash-app)
        num_connections -- The maximal number of agents one agent can exchange
            secrets with in one time-step (slider in Dash-app)
        n_intervals -- A value that increases every update_interval. This is used
            in order to update the graph when the simulation is running.
        strategy -- A string chosen from a Dropdown-menu in the Dash app.
            It specifies which strategy the agents should use.
    The outputs are:
        The graph-figure -- the actual nodes-and-edges graph displayed in the app
        The graph-style -- CSS for the graph
        Number of time-steps -- The number of time-steps is displayed in a div in
            the Dash-app
    """
    global num_nodes_state
    global base_figure
    global G

    controller.update(num_nodes, strategy, call_protocol)
    simulation_finished = controller.simulate()

    # We only need to recompute the base graph whenever the number of agents changes
    if num_nodes_state != num_nodes:
        num_nodes_state = num_nodes
        # Calculate positions for the nodes of the graph
        circle_center = (0, 0)
        circle_radius = 0.8
        positions = {i: (circle_center[0] + circle_radius * math.cos(i*2 * math.pi / num_nodes),
                         circle_center[1] + circle_radius * math.sin(i*2 * math.pi / num_nodes)) for i in range(1, num_nodes + 1)}

        # Make a complete graph
        if(num_nodes < 11):
            G = nx.complete_graph(num_nodes)
        else:
            G = nx.Graph()
            for i in range(num_nodes):
                G.add_node(i)
        for node, position in zip(G.nodes, positions.values()):
            G.nodes[node]["pos"] = position
        pos = nx.get_node_attributes(G, 'pos')

        # Create Edges
        edge_trace = go.Scatter(
            x=[],
            y=[],
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines')

        for edge in G.edges():
            x0, y0 = G.node[edge[0]]['pos']
            x1, y1 = G.node[edge[1]]['pos']
            edge_trace['x'] += tuple([x0, x1, None])
            edge_trace['y'] += tuple([y0, y1, None])

        node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode='markers',
            hoverinfo='text',
            marker=dict(
                showscale=True,
                colorscale='Viridis',
                reversescale=False,
                color=[],
                cmax=len(controller.model.agents),
                cmin=1,
                size=100 // math.sqrt(num_nodes) + 10,
                colorbar=dict(
                    thickness=15,
                    title='Secrets known',
                    xanchor='left',
                    titleside='right'
                ),
                line=dict(width=2)))

        for node in G.nodes():
            x, y = G.node[node]['pos']
            node_trace['x'] += tuple([x])
            node_trace['y'] += tuple([y])

        # add color to node points, based on the number of secrets the agents know
        # This only gets called if num_nodes has changed
        agents = controller.model.agents
        for node in G.nodes:
            agent = agents[node]
            num_secrets_known = len(agent.secrets)
            node_trace['marker']['color'] += (num_secrets_known, )
            node_info = 'Name: ' + str(agent) + '<br># of secrets: ' + str(num_secrets_known)
            node_trace['text'] += (node_info,)

        fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                    # title='<br>Network Graph of ' + str(num_nodes) + ' agents',
                    title='',
                    titlefont=dict(size=16),
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20, l=5, r=5, t=40),
                    annotations=[ dict(
                        showarrow=False,
                        xref="paper", yref="paper",
                        x=0.005, y=-0.002 ) ],
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))
        base_figure = fig
    else:
        fig = base_figure
        fig.data = fig.data[0:2] # Only take the edge and node traces

    # Change the colors and information of the fig here
    # This gets called every interval
    marker_colors = []
    marker_information = []
    agents = controller.model.agents
    for agent in agents:
        marker_colors.append(len(agent.secrets))
        marker_information.append('Name: ' + str(agent) + '<br># of secrets: ' + str(len(agent.secrets)))
    fig.data[1].marker.color = tuple(marker_colors)
    fig.data[1].text = tuple(marker_information)

    # This part adds red edges on the graph to signify which connections have been made
    additional_edge_traces = controller.model.connections
    for aet in additional_edge_traces:
        node1, node2 = aet
        x1, y1 = G.nodes[node1]['pos']
        x2, y2 = G.nodes[node2]['pos']
        line = go.Scatter(x=[x1, x2],
                          y=[y1, y2],
                          mode='lines',
                          line=go.scatter.Line(color='red'))
        fig.add_trace(line)

    # Return the figure and the number of time steps taken
    return fig, 'Time step: ' + str(controller.timesteps_taken)

@app.callback(
    Output('start_simulation', 'disabled'),
    [Input('start_simulation', 'n_clicks'),
    Input("comp_hist", "n_clicks")])
def disable_start_button(start_clicks, comp_clicks):
    """Disables the start button, based on any input that needs to block the start button"""
    if start_clicks is not None or comp_clicks is not None:
        return True
    else:
        return False

@app.callback(
    Output('num_nodes', 'disabled'),
    [Input('start_simulation', 'n_clicks'),
    Input("comp_hist", "n_clicks")])
def disable_num_nodes_slider(start_clicks, comp_clicks):
    """Disables the num_nodes slider, based on any input that needs to block it"""
    if start_clicks is not None or comp_clicks is not None:
        return True
    else:
        return False

@app.callback(
    Output('strategy', 'disabled'),
    [Input('start_simulation', 'n_clicks'),
    Input("comp_hist", "n_clicks")])
def disable_num_nodes_slider(start_clicks, comp_clicks):
    """Disables the strategy menu, based on any input that needs to block it"""
    if start_clicks is not None or comp_clicks is not None:
        return True
    else:
        return False

@app.callback(
    Output('call_protocol', 'disabled'),
    [Input('start_simulation', 'n_clicks'),
    Input("comp_hist", "n_clicks")])
def disable_num_nodes_slider(start_clicks, comp_clicks):
    """Disables the call protocol menu, based on any input that needs to block it"""
    if start_clicks is not None or comp_clicks is not None:
        return True
    else:
        return False

@app.callback(
    Output('comp_hist', 'disabled'),
    [Input('start_simulation', 'n_clicks'),
    Input("comp_hist", "n_clicks")])
def disable_num_nodes_slider(start_clicks, comp_clicks):
    """Disables the call protocol menu, based on any input that needs to block it"""
    if start_clicks is not None or comp_clicks is not None:
        return True
    else:
        return False

@app.callback(
    Output('show_hist', 'options'),
    [Input('start_simulation', 'n_clicks'),
    Input("comp_hist", "n_clicks")])
def disable_num_nodes_slider(start_clicks, comp_clicks):
    """Disables the show histogram checkbox, based on any input that needs to block it"""
    if start_clicks is not None:
        return [{'label': 'Show histogram', 'value': 'SH', 'disabled': True}]
    else:
        return [{'label': 'Show histogram', 'value': 'SH', 'disabled': False}]


@app.callback(
    Output('start_simulation', 'children'),
    [Input('start_simulation', 'n_clicks')])
def start_simulation(start_clicks):
    """After clicking on the start button in the Dash-app, the simulation will be started.

    If the simulation has not been started yet, this function will start it.
    If the simulation has started already, and the button is pressed again,
    the simulation will be paused.
    If the simulation has been paused, and the button is pressed again,
    the simulation will be resumed.
    If the simulation has ended already, and the button is pressed again,
    the button will be disabled (grayed out) and display the text:
    'Already finished!'.
    """
    if start_clicks == 1:
        controller.start_simulation()
        button_text = "Pause simulation"
    elif start_clicks is not None and start_clicks % 2 == 1:
        controller.resume_simulation()
        button_text = "Pause simulation"
    elif start_clicks is None:
        button_text = "Start simulation"
    else:
        if controller.simulation_finished:
            button_text = "Already finished!"
        else:
            button_text = "Resume simulation"
            controller.pause_simulation()
    return button_text

@app.callback(
    [Output('start_simulation', 'n_clicks'),
    Output('progress_interval', 'n_intervals'),
    Output('comp_hist', 'n_clicks')],
    [Input('reset_simulation', 'n_clicks')])
def reset_simulation(n_clicks):
    """Resets the simulation -- gets triggered by clicking the reset button.

    Also resets the n_clicks variable of the start button and comp hist button.
    This in turn resets a lot of the disabled buttons and other HTML elements.
    """
    global computing_histogram
    computing_histogram = False

    if n_clicks is not None:
        controller.reset_simulation()
    return None, 0, None

@app.callback(
    Output('interval_component', 'interval'),
    [Input('speed_factor', 'value')])
def change_speed(speed_factor):
    new_interval = update_interval / speed_factor
    return int(new_interval)


@app.callback(
    [Output('Graph', 'style'),
    Output('Hist', 'style')],
    [Input('show_hist', 'value')])
def show_histogram(show_hist):
    if show_hist:
        graph_style = {"display":"none"}
        hist_style = {"display":"block"}
    else:
        graph_style = {"display":"block"}
        hist_style = {"display":"none"}
    return graph_style, hist_style

@app.callback(
    [Output('comp_hist', 'children'),
    Output('progress_interval', 'max_intervals')],
    [Input('comp_hist', 'n_clicks'),
    Input('num_nodes','value'),
    Input('strategy','value'),
    Input('call_protocol','value')])
def compute_histogram(n_clicks, num_nodes, strategy, call_protocol):
    if n_clicks is not None:
        global computing_histogram
        global generator
        global num_sims
        num_sims = 1000
        computing_histogram = True
        generator = simulate_generator(num_nodes, strategy, call_protocol, num_sim=num_sims)
        t = next(generator)
        return "Computing...", num_sims
    return "Compute Histogram", 0

@app.callback(
    [Output('progress_bar', 'children'),
    Output('progress_bar', 'style'),
    Output('comp_hist', 'style'),
    Output('Hist', 'figure')],
    [Input('progress_interval', 'n_intervals')],
    [State('Hist', 'figure')])
def update_progress_bar(n_intervals, old_fig):
    global computing_histogram
    global generator
    global num_sims
    global timesteps_counter

    hist = old_fig
    if computing_histogram:
        try:
            timesteps_counter = next(generator)
        except StopIteration:
            computing_histogram = False

    # Only make a histogram every 3 intervals (or when the end is reached,
    # otherwise it starts to lag hard
    if n_intervals % 3 == 0 or not computing_histogram:
        hist = make_histogram_for_frontend(timesteps_counter)

    prog_bar_width = 100*n_intervals/num_sims
    comp_hist_width = 100 - prog_bar_width
    prog_bar_style = {
        "width":f"{prog_bar_width}%",
        "min-width":"0.1%",
        "font-size":"2rem",
        "position":"relative",
        "background":"rgb(0,200,0)",
        "height":"100%",
        "padding":0,
        "margin":0,
        "border":0,
    }
    comp_hist_style = {
        "width":f"{comp_hist_width}%",
        "min-width":"0.1%",
        "font-size":"2rem",
        "position":"relative",
        "background":"rgb(255,255,255)",
        "height":"100%",
        "padding":0,
        "margin":0,
        "border":0,
        "overflow":"hidden",
        "text-overflow": "ellipsis"
    }

    return str(math.ceil(prog_bar_width))+"%", prog_bar_style, comp_hist_style, hist
