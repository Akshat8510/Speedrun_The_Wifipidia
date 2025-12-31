# src/visualizer.py
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components

def create_graph(path_list):
    """
    Creates an interactive HTML graph of the path.
    path_list: ['A', 'B', 'C']
    """
    net = Network(height='400px', width='100%', bgcolor='#0E1117', font_color='white')
    
    # Add nodes and edges
    for i in range(len(path_list)):
        node = path_list[i]
        # Color start blue, end red, middle green
        color = '#00ff41' # Hacker Green
        if i == 0: color = '#00b4d8' # Blue
        if i == len(path_list) - 1: color = '#ff006e' # Pink/Red
        
        net.add_node(node, label=node, color=color, title=node)
        
        if i > 0:
            parent = path_list[i-1]
            net.add_edge(parent, node, color='white')

    # Physics settings for a cool look
    net.repulsion(node_distance=100, spring_length=200)
    
    # Save locally
    net.save_graph('path_graph.html')
    return 'path_graph.html'