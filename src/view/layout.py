import dash_html_components as html
import dash_core_components as dcc

def layout(default_num_agents, update_interval):
	return html.Div(
		        [html.Div(
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
		                    [dcc.Graph(
		                        id='Graph',
		                        figure={
		                            'data': [],
		                            'layout': {
		                                'xaxis': dict(showgrid=False, zeroline=False, showticklabels=False),
		                                'yaxis': dict(showgrid=False, zeroline=False, showticklabels=False)
		                            }
		                        },
		                        style={
		                            'display': 'none',
		                        }
		                    ),
		                    dcc.Graph(
		                        id='Hist',
		                        figure={
		                            'data': [],
		                            'layout': {
		                                'xaxis': dict(showgrid=False, zeroline=False, showticklabels=False),
		                                'yaxis': dict(showgrid=False, zeroline=False, showticklabels=False)
		                            }
		                        },
		                        style={
		                            "display": "none"
		                        }
		                    )],
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
		                "height": "80vh",
		                "font-size": "2.0rem"
		            },
		            className="container",
		            id="grid"
		        ),
		        html.Div(
		            [
		                dcc.Checklist(
		                    options=[
		                        {'label': 'Show histogram', 'value': 'SH', 'disabled': False},
		                    ],
		                    id="show_hist",
		                    labelStyle={
		                        "height":"20px",
		                        "width:":"20px"
		                    }
		                ),
		                html.Div(
		                    [html.Button(
		                        # "Calculating...",   
		                        id="progress_bar",
		                        style={
		                            "width":"0.1%",
		                            "min-width":"0.1%",
		                            "font-size":"2rem",
		                            "position":"relative",
		                            "background":"rgb(0,150,0)",
		                            "height":"100%",
		                            "padding":0,
		                            "margin":0,
		                            "border":0,
		                        }
		                    ),
		                    html.Button(
		                        "Compute Histogram",
		                        id="comp_hist",
		                        style={
		                            "width":"99.9%",
		                            "min-width":"0.1%",
		                            "font-size":"2rem",
		                            "position":"relative",
		                            "background":"rgb(255,255,255)",
		                            "height":"100%",
		                            "padding":0,
		                            "margin":0,
		                            "border":0,
		                        }
		                    ),
		                    dcc.Interval(
		                        id='progress_interval',
		                        interval=200, #ms
		                        n_intervals=0,
		                        max_intervals=0
		                    )],
		                    style={
		                        "display": "flex",
		                        "margin":"auto",
		                        "width":"30%",
		                        "height":"40%",
		                        "border":"1px",
		                        "border-style":"solid"
		                    }
		                )
		            ],
		            style={
		                "height": "20vh",
		                "textAlign": "center",
		                "font-size": "2.0rem"
		            }
		        )]
		    )