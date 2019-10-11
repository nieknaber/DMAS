import networkx as nx
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import math

from simulations import simulate as sim

def run_ui(model_controller, default_num_agents):
    """Runs the Dash UI, which is displayed in a web-browser.

    The app layout is defined in app.layout. Dash allows to specify the HTML and CSS
    in pythonic ways, which is done here. There are some callback functions, denoted
    with the @app-callback decorators that change the Dash app in different ways as it
    is running. Most callbacks are called when the user interacts with the UI. The
    render_graph callback is also called every 'update_interval'.
    """

    update_interval = 2000  # 2000 ms = 2 s
    app = dash.Dash()

    # to add ability to use columns
    app.css.append_css({'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'})

    app.layout = html.Div(
                    style={
                        'padding': '30px'
                    },
                    children = [
                        html.H1(
                            children='Gossip problem',
                            style={
                                'textAlign': 'center',
                                'color': 'black'
                            }
                        ),
                        html.Div(children=[html.H3("A web application built for the Design of Multi-Agent Sytems course."),
                            html.Div("This system was built by: Arjan Jawahier (s2762161), Xabi Krant (s2955156), Roeland Lindhout (s2954524) & Niek Naber (s2515970)")],
                        style={
                            'textAlign': 'center',
                            'color': 'black'
                        }),
                        html.Div(
                            style={
                                'padding': '15px 0'
                            },
                            children = [
                            html.Label('Number of agents'),
                            dcc.Slider(id='num_nodes',
                                min=3,
                                max=100,
                                marks={i: str(i) if i%5 == 0 else str("") for i in range(3, 101)},
                                value=default_num_agents,
                            )
                        ]),
                        html.Div(
                            style={
                                'margin-top': '2%'
                            },
                            children=[
                                html.Button(
                                    children=[
                                        html.Label("Start simulation (once)")
                                    ],
                                    id="start_simulation"
                                ),
                                html.Button(
                                    children=[
                                        html.Label("Reset simulation")
                                    ],
                                    id="reset_simulation"
                                )
                            ]),
                        html.Div(
                            dcc.Dropdown(
                                id='strategy',
                                options=[
                                    {'label': 'Random', 'value': 'Random'},
                                    {'label': 'Call Me Once', 'value': 'Call-Me-Once'},
                                    {'label': 'Learn New Secrets', 'value': 'Learn-New-Secrets'},
                                    {'label': 'Call most useful', 'value': 'Most-useful'},
                                    {'label': 'Token', 'value': 'Token'},
                                    {'label': 'Spider', 'value': 'Spider'},
                                    {'label': 'Token (improved)', 'value': 'Token-improved'},
                                    {'label': 'Spider (improved)', 'value': 'Spider-improved'},
                                    {'label': 'mathematical', 'value': 'mathematical'},
                                    {'label': 'Divide', 'value': 'divide'}
                                ],
                                value = 'Random'
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
                                value = 'Standard'
                            ),
                            id="output-protocol"
                        ),
                        html.Div(
                            style={
                                'margin-top': '2%'
                            },
                            children=[
                            html.Button(
                                children=[
                                    html.Label("Start simulations")
                                    ],
                                id="start_simulation1"
                            )],
                        ),
                        html.Div(
                            dcc.Input(
                                id="number_of_simulations",
                                type="number",
                                placeholder="Choose number of simulations"
                            ),
                            id="numsim",
                        ),
                        html.Div(html.P(id='timestep')),
                        html.Div(dcc.Graph(id='Graph', animate=False,
                            style={
                                'display': 'none'
                            }
                        )),
                        dcc.Interval(
                            id='interval_component',
                            interval=update_interval, #ms
                            n_intervals=0
                        )
                    ]
                )


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

        # We also need to update the controller
        model_controller.update(num_nodes, strategy, call_protocol)
        simulation_finished = model_controller.simulate_from_ui()

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
        pos = nx.get_node_attributes(G,'pos')

        # Create Edges
        edge_trace = go.Scatter(
            x=[],
            y=[],
            line=dict(width=0.5,color='#888'),
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
                colorscale='Magma',
                reversescale=True,
                color=[],
                cmax=len(model_controller.agents),
                cmin=1,
                size=100//math.sqrt(num_nodes)+10,
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
        agents = model_controller.agents
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

        # This part adds red edges on the graph to signify which connections have been made
        additional_edge_traces = model_controller.connections
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
                'height': '800px',
                'width': '800px'
        }

        return fig, style,  'Time step: ' + str(model_controller.timesteps_taken)

    @app.callback(
        [Output(component_id='start_simulation', component_property='children'),
         Output(component_id='start_simulation', component_property='disabled')],
        [Input(component_id='start_simulation', component_property='n_clicks')])
    def start_simulation(n_clicks):
        """After clicking on the start button, the simulation will be started.

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
        if n_clicks == 1:
            model_controller.start_simulation()
            button_text = "Pause simulation"
        elif n_clicks is not None and n_clicks % 2 == 1:
            model_controller.resume_simulation()
            button_text = "Pause simulation"
        elif n_clicks is None:
            button_text = "Start simulation"
        else:
            if model_controller.simulation_finished:
                print("Simulation has already finished!")
                button_text = "Already finished!"
                button_disabled = True
            else:
                button_text = "Resume simulation"
                model_controller.pause_simulation()
        return button_text, button_disabled

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
            model_controller.reset_simulation()
        return button_disabled, None

    app.run_server(debug=True)

    @app.callback(
        [Output(component_id='numsim', component_property='children'),
        Output(component_id='start_simulation1', component_property='n_clicks')],
        [Input(component_id='start_simulation1', component_property='n_clicks'),
        Input(component_id='number_of_simulations', component_property='value'),
        Input('num_nodes','value'),
        Input('strategy','value'),
        Input('call_protocol','value')])
    def start_n_simulations(number_of_simulations, num_nodes,strategy,call_protocol):
        sim(number_of_simulations,num_nodes, strategy,call_protocol)
