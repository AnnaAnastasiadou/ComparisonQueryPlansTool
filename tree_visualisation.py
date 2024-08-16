import matplotlib.pyplot as plt
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
from tree_edit_distance import TreeNode, json_to_tree
import json

def extract_properties(node):
    """
    Extract properties from a TreeNode and format them as a string for visualization.

    Args:
        node (TreeNode): The node from which to extract properties.

    Returns:
        str: A string representing the node's properties for display.
    """
    try:
        # Convert node label from string to JSON
        label_str = node.label
        properties_json = json.loads(label_str)
        # Extract the node type of the node
        properties = properties_json.get("Node Type", "Unknown Type")
        # Extract the rest of the attributes of the label
        details = [f"{key}: {value}" for key, value in properties_json.items() if key != "Node Type" and value != "None"]
        return f"{properties}\n" + "\n".join(details)
    
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        print(f"Node label: {node.label}")
        return node.label

def add_nodes(graph, node):
    """
    Recursively add nodes and edges from a TreeNode to a NetworkX graph.

    Args:
        graph (networkx.DiGraph): The graph to which nodes and edges will be added.
        node (TreeNode): The current node to add to the graph.
    
    Raises:
        TypeError: If the node is not an instance of TreeNode.
    """
    if not isinstance(node, TreeNode):
        raise TypeError(f"Expected a TreeNode instance, got {type(node).__name__}")
    
    # Add the node to the graph with its properties label
    graph.add_node(node, label=extract_properties(node))

    # Add edges and recursively add children
    for child in node.children:
        graph.add_edge(node, child)
        add_nodes(graph, child)

def get_node_size_and_font(label):
    """
    Adjust node size and font size based on the length of the label.

    Args:
        label (str): The label of the node.

    Returns:
        tuple: A tuple containing the node size and font size.
    """

    # Split label into lines and calculate lengths
    splt = label.split('\n')
    lst = [len(x) for x in splt if x != None]
    lst.append(len(splt))
    label_length = max(lst)

    # Determine node size and font size based on the label length
    node_size =  50 * label_length  
    font_size = min(10 + 2 * label_length, 5) 

    return node_size, font_size

def plot_trees(tree1, tree2 , filename):
    """
    Plot and compare two trees using NetworkX and Matplotlib.

    Args:
        tree1 (TreeNode or dict): The first tree to plot.
        tree2 (TreeNode or dict): The second tree to plot.
        filename (str): The filename to save the plot image.
    """

    # Convert JSON objects to TreeNode if necessary
    if isinstance(tree1, dict):
        tree1 = json_to_tree(tree1, "tree1")
    if isinstance(tree2, dict):
        tree2 = json_to_tree(tree2, "tree2")
    
    # Create subplots for the two trees
    _, axs = plt.subplots(1, 2, figsize=(18, 12))

    # Initialize graphs for the two trees
    G1 = nx.DiGraph()
    G2 = nx.DiGraph()

    # Add nodes and edges to the graphs
    add_nodes(G1, tree1)
    add_nodes(G2, tree2)

    # Compute positions for nodes using Graphviz
    pos1 = graphviz_layout(G1, prog='dot')
    pos2 = graphviz_layout(G2, prog='dot')

    # Get labels for nodes
    labels1 = nx.get_node_attributes(G1, 'label')
    labels2 = nx.get_node_attributes(G2, 'label')

    # Plot first tree with node comparison
    for node1, label1 in labels1.items():
        color = 'red'
        # Check if the node is present in the second tree
        for _,label2 in labels2.items():
            if label1 == label2:
                color = 'green'
                break
        node_size, font_size = get_node_size_and_font(node1.label)
        nx.draw_networkx_nodes(G1, pos1, nodelist=[node1], node_size=node_size, node_shape='o', node_color=color, alpha=0.8, ax=axs[0])
        nx.draw_networkx_labels(G1, pos1, labels={node1: label1}, font_size=font_size, font_color='black', font_weight='bold', verticalalignment='center', horizontalalignment='center', ax=axs[0])
    nx.draw_networkx_edges(G1, pos1, ax=axs[0])
    
    # Plot second tree with node comparison
    for node2, label2 in labels2.items():
        color = 'red'
        # Check if the node is present in the first tree
        for _,label1 in labels1.items():
            if label1 == label2:
                color = 'green'
                break
        node_size, font_size = get_node_size_and_font(node2.label)
        nx.draw_networkx_nodes(G2, pos2, nodelist=[node2], node_size=node_size, node_shape='o', node_color=color, alpha=0.8, ax=axs[1])
        nx.draw_networkx_labels(G2, pos2, labels={node2: label2}, font_size=font_size, font_color='black', font_weight='bold', verticalalignment='center', horizontalalignment='center', ax=axs[1])
    nx.draw_networkx_edges(G2, pos2, ax=axs[1])

    # Adjust layout
    plt.tight_layout()
    # Save plot
    plt.savefig(filename)
    
    plt.show()