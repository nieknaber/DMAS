"""
The app layout is defined in app.layout. Dash allows to specify the HTML and CSS
in pythonic ways, which is done here. There are some callback functions, denoted
with the @app-callback decorators that change the Dash app in different ways as it
is running. Most callbacks are called when the user interacts with the UI. The
render_graph callback is also called every 'update_interval'.
"""

import networkx as nx
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import math

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
app.layout = \
    html.Div(
        [html.Div(
            [html.H1(
                'Gossip problem',
                style={
                    'textAlign': 'center',
                    'color': 'black'
                }
            ),
            html.Div(
                [html.H3("A web application built for the Design of Multi-Agent Sytems course."),
                html.P("This system was built by:"),
                html.P("Arjan Jawahier (s2762161), Xabi Krant (s2955156),"
                         " Roeland Lindhout (s2954524) & Niek Naber (s2515970)")],
                style={
                    'textAlign': 'center',
                    'color': 'black',
                    'font-size': '1rem'
                },
                className="container"
            ),
            html.Div(
                style={
                    'padding': '15px 0'
                },
                children = [
                    html.Div('Number of agents', style={"textAlign": "center"}),
                    html.Div(
                        dcc.Slider(id='num_nodes', 
                           min=3, 
                           max=100,
                           marks={i: str(i) if i%5 == 0 else str("") for i in range(3, 101)},
                           value=default_num_agents,
                        ),
                        style={
                            "width":"90%",
                            "margin":"auto"
                        }
                    )
                ]),
            html.Div(
                style={
                    'margin-top': '2%',
                    "display": "flex",
                },
                children=[
                    html.Button(
                        children=[
                            html.Label("Start simulation")
                        ],
                        id="start_simulation"
                    ),
                    html.Button(
                        children=[
                            html.Label("Reset simulation")
                        ],
                        id="reset_simulation"
                    )
                ],
                className="container"
            ),
            html.Div(
                dcc.Dropdown(
                    id='strategy',
                    options=[
                        {'label': 'Random', 'value': 'Random'},
                        {'label': 'Call Me Once', 'value': 'Call-Me-Once'},
                        {'label': 'Learn New Secrets', 'value': 'Learn-New-Secrets'},
                        {'label': 'Call most useful', 'value': 'Most-useful'},
                        {'label': 'Call least secrets', 'value': 'Min-Secrets'},
                        {'label': 'Call most secrets', 'value': 'Max-Secrets'},
                        {'label': 'Token', 'value': 'Token'},
                        {'label': 'Spider', 'value': 'Spider'},
                        {'label': 'Token (improved)', 'value': 'Token-improved'},
                        {'label': 'Spider (improved)', 'value': 'Spider-improved'},
                        {'label': 'Mathematical', 'value': 'Mathematical'},
                        {'label': 'Divide', 'value': 'Divide'},
                        {'label': 'Bubble', 'value': 'Bubble'}
                    ],
                    value = 'Random',
                    clearable=False
                ),
                id="output-strategy"
            ),
            html.Div(
                dcc.Dropdown(
                    id='call_protocol',
                    options=[
                        {'label': 'Standard', 'value': 'Standard'},
                        {'label': 'Not Standard', 'value': 'Not-Standard'},
                    ],
                    value='Standard',
                    clearable=False
                ),
                id="output-protocol"
            ),
            html.Div(html.P(id='timestep')),
            dcc.Interval(
                id='interval_component',
                interval=update_interval, #ms
                n_intervals=0
            ),
            html.Div(
                ["Simulation speed",
                dcc.Slider(
                    id='speed_factor',
                    min=0.4,
                    max=4.0,
                    step=0.2,
                    value=1.0,
                )]
            )],
            className="six columns",
            style={
                "float": "left",
                "height": "100%"
            }
        ),
        html.Div(
            html.Div(
                dcc.Graph(
                    id='Graph',
                    style={
                        'display': 'none'
                    }
                ),
                className="container"
            ),
            className="six columns",
            style={
                "float": "left",
                "height": "100%"
            }
        )],
        style={
            'padding': '30px',
            "display": "flex",
            "height": "100vh",
            "font-size": "2.0rem"
        },
        className="container",
        id="grid"
    )

# Global variables used in render_graph, this has to be used since an output can only have 1 callback
# But we need to save the states
num_nodes_state = 0
base_figure = go.Figure()
G = nx.Graph()

# This has to be such a big function because a Dash output can only have one callback connected to it.
# And since we want to update the graph with most of what we do, we have to put all that logic in this function.
@app.callback(
    [Output('Graph','figure'),
    Output('Graph','style'),
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

    style={
    }
    # Return the figure, a new empty style for the graph and the number of time steps taken
    return fig, style, 'Time step: ' + str(controller.timesteps_taken)

def run_ui(ctrl, def_num_agents):
    """Runs the Dash UI, which is displayed in a web-browser."""
    global controller
    global default_num_agents
    controller = ctrl
    default_num_agents = def_num_agents
    app.run_server(debug=True)


@app.callback(
    [Output(component_id='start_simulation', component_property='children'),
     Output(component_id='start_simulation', component_property='disabled'),
     Output(component_id='num_nodes', component_property='disabled'),
     Output(component_id='strategy', component_property='disabled'),
     Output(component_id='call_protocol', component_property='disabled')],
    [Input(component_id='start_simulation', component_property='n_clicks')])
def start_simulation(n_clicks):
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
    button_disabled = False
    other_disabled = False

    if n_clicks is not None:
        other_disabled = True

    if n_clicks == 1:
        controller.start_simulation()
        button_text = "Pause simulation"
    elif n_clicks is not None and n_clicks % 2 == 1:
        controller.resume_simulation()
        button_text = "Pause simulation"
    elif n_clicks is None:
        button_text = "Start simulation"
    else:
        if controller.simulation_finished:
            print("Simulation has already finished!")
            button_text = "Already finished!"
            button_disabled = True
        else:
            button_text = "Resume simulation"
            controller.pause_simulation()
    return button_text, button_disabled, other_disabled, other_disabled, other_disabled

@app.callback(
    [Output(component_id='reset_simulation', component_property='disabled'),
    Output(component_id='start_simulation', component_property='n_clicks')],
    [Input(component_id='reset_simulation', component_property='n_clicks')])
def reset_simulation(n_clicks):
    """Resets the simulation -- gets triggered by clicking the reset button.

    Also resets the n_clicks variable of the start button.
    """
    button_disabled = False
    if n_clicks is not None:
        controller.reset_simulation()
    return button_disabled, None

@app.callback(
    Output('interval_component', 'interval'),
    [Input('speed_factor', 'value')])
def change_speed(speed_factor):
    new_interval = update_interval / speed_factor
    return int(new_interval)

# This commented out block of code might be used later - Arjan
# @app.callback(
#     Output('numsim','children'),
#     [Input('start_simulation1', 'n_clicks'),
#     Input('number_of_simulations', 'value'),
#     Input('num_nodes','value'),
#     Input('strategy','value'),
#     Input('call_protocol','value')])
# def start_n_simulations(n_clicks, number_of_simulations, num_nodes,strategy,call_protocol):
#     # TODO: we moeten even kijken hoe we dit precies willen doen. Vanuit de UI? - Arjan
#     if n_clicks is not None and n_clicks == 1:
#         sim(num_nodes, strategy, call_protocol, number_of_simulations=number_of_simulations)

    
