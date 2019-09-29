import networkx as nx
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import math



def run_ui(model_controller, default_num_agents, default_num_connections):
    ################### START OF DASH APP ###################

    app = dash.Dash()

    # to add ability to use columns
    app.css.append_css({
        'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
    })

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
                                'padding': '15px 0'
                            },
                            children = [
                            html.Label('Number of connections per agent'),
                            dcc.Slider(id='num_connections',
                                min=0,
                                max=5,
                                marks={i: str(i) for i in range(0, 6)},
                                value=1,
                            )
                        ]),
                        html.Div(
                            style={
                                'margin-top': '2%'
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
                            ]),
                        html.Div(
                            dcc.Dropdown(
                                id='strategy',
                                options=[
                                    {'label': 'Random', 'value': 'Random'},
                                    {'label': 'Call Me Once', 'value': 'Call-Me-Once'},
                                    {'label': 'Learn New Secrets', 'value': 'Learn-New-Secrets'}
                                ],
                                placeholder = 'Select a strategy (not working ATM)'
                            ),
                            id="output-strategy"
                        ),
                        html.Div(dcc.Graph(id='Graph', animate=True)),
                        dcc.Interval(
                            id='interval_component',
                            interval=2000, #ms
                            n_intervals=0
                        )
                    ]
                )


    # This has to be such a big function because a Dash output can only have one callback connected to it.
    # And since we want to update the graph with most of what we do, we have to put all that logic in this function.
    @app.callback(
        Output('Graph','figure'),
        [Input('num_nodes','value'),
        Input('num_connections','value'),
        Input('interval_component','n_intervals')])
    def render_graph(num_nodes, num_connections, n_intervals):
        # We also need to update the controller
        model_controller.update(num_nodes, num_connections)
        simulation_finished = model_controller.simulate_from_ui()

        # Calculate positions for the nodes of the graph
        circle_center = (0, 0)
        circle_radius = 0.8
        positions = {i: (circle_center[0] + circle_radius * math.cos(i*2 * math.pi / num_nodes),
                         circle_center[1] + circle_radius * math.sin(i*2 * math.pi / num_nodes)) for i in range(1, num_nodes + 1)}

        # Make a complete graph
        G = nx.complete_graph(num_nodes)
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
                size=40,
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
                    title='<br>Network Graph of ' + str(num_nodes) + ' agents<br>Time step: ' +  str(model_controller.timesteps_taken),
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

        return fig

    # This callback is linked to the button on the webpage. It starts and pauses the simulation
    @app.callback(
        [Output(component_id='start_simulation', component_property='children'),
         Output(component_id='start_simulation', component_property='disabled')],
        [Input(component_id='start_simulation', component_property='n_clicks')])
    def start_simulation(n_clicks):
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
    def start_simulation(n_clicks):
        button_disabled = False
        if n_clicks is not None:
            model_controller.reset_simulation()
        return button_disabled, None

    app.run_server(debug=True)
