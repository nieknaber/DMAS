import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import math
import networkx as nx

from src.modelController.model_controller import ModelController

################### START OF DASH APP ###################

DEFAULT_NUM_AGENTS = 10
DEFAULT_NUM_CONNECTIONS = 1

app = dash.Dash()
mc = ModelController(DEFAULT_NUM_AGENTS, DEFAULT_NUM_CONNECTIONS)

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
                            value=DEFAULT_NUM_AGENTS,
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
                    html.Div(dcc.Graph(id='Graph'))
                ]
            )


@app.callback(
    Output(component_id='Graph', component_property='figure'),
    [Input(component_id='num_nodes',component_property='value'),
    Input(component_id='num_connections',component_property='value')])
def render_graph(num_nodes, num_connections):
    # We also need to update the controller
    mc.update(num_nodes, num_connections)

    # get a x,y position for each node
    circle_center = (0, 0)
    circle_radius = 0.8
    positions = {i: (circle_center[0] + circle_radius * math.cos(i*2 * math.pi / num_nodes),
                     circle_center[1] + circle_radius * math.sin(i*2 * math.pi / num_nodes)) for i in range(1, num_nodes + 1)}

    # Complete graph instead of random?
    G = nx.complete_graph(num_nodes)
    for node, position in zip(G.nodes, positions.values()):
        G.nodes[node]["pos"] = position

    pos = nx.get_node_attributes(G,'pos')

    dmin=1
    ncenter=0
    for n in pos:
        x, y = pos[n]
        d = (x-0.5)**2+(y-0.5)**2
        if d < dmin:
            ncenter = n
            dmin = d

    p = nx.single_source_shortest_path_length(G, ncenter)

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
            # colorscale options
            #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
            #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
            #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
            colorscale='YlGnBu',
            reversescale=True,
            color=[],
            size=10,
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            ),  
            line=dict(width=2)))

    for node in G.nodes():
        x, y = G.node[node]['pos']
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])

    # add color to node points
    for node, adjacencies in enumerate(G.adjacency()):
        node_trace['marker']['color']+=tuple([len(adjacencies[1])])
        node_info = 'Name: ' + str(adjacencies[0]) + '<br># of connections: '+str(len(adjacencies[1]))
        node_trace['text'] += tuple([node_info])

    fig = go.Figure(data=[edge_trace, node_trace],
             layout=go.Layout(
                title='<br>Network Graph of '+str(num_nodes)+' rules',
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

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)