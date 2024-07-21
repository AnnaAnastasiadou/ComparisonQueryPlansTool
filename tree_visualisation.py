import matplotlib.pyplot as plt
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
from tree_edit_distance import TreeNode, json_to_tree
import json

def extract_properties(node):
    try:
        # Replace newlines and other control characters with their escaped versions
        label_str = node.label#.replace("\n", "\\n").replace("\r", "\\r")
        properties = json.loads(label_str).get("Node Type", "Unknown Type")
        details = [f"{key}: {value}" for key, value in json.loads(label_str).items() if key != "Node Type" and value != "None"]
        return f"{properties}\n" + "\n".join(details)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        print(f"Node label: {node.label}")
        return "Invalid Node"

def add_nodes(graph, node):
    if not isinstance(node, TreeNode):
        raise TypeError(f"Expected a TreeNode instance, got {type(node).__name__}")
    graph.add_node(node, label=extract_properties(node))
    for child in node.children:
        graph.add_edge(node, child)
        add_nodes(graph, child)

def get_node_size_and_font(label):
    # Calculate the node size and font size based on the length of the label
    splt = label.split('\n')
    lst = [max(len(x) for x in splt if x != None)]
    lst.append(len(splt))
    label_length = max(lst)
    print(label_length)
    node_size =  100 * label_length  # Adjust node size based on label length
    font_size = min(10 + 2 * label_length, 5)  # Adjust font size within a range
    return node_size, font_size

def plot_trees(tree1, tree2, filename):
    if isinstance(tree1, dict):
        tree1 = json_to_tree(tree1, "tree1")
    if isinstance(tree2, dict):
        tree2 = json_to_tree(tree2, "tree2")
    
    fig, axs = plt.subplots(1, 2, figsize=(18, 12))
    for ax, tree, title in zip(axs, [tree1, tree2], ["Query Execution Plan 1", "Query Execution Plan 2"]):
        G = nx.DiGraph()
        add_nodes(G, tree)
        pos = graphviz_layout(G, prog='dot')
        labels = nx.get_node_attributes(G, 'label')
        
        # Draw the graph with dynamically adjusted node sizes and font sizes
        for node, label in labels.items():
            print(f"Node: {node}, Label: {label}")
            node_size, font_size = get_node_size_and_font(label)
            nx.draw_networkx_nodes(G, pos, nodelist=[node], node_size=node_size, node_shape='o', node_color='skyblue', alpha=0.8, ax=ax)
            nx.draw_networkx_labels(G, pos, labels={node: label}, font_size=font_size, font_color='black', font_weight='bold', verticalalignment='center', horizontalalignment='center', ax=ax)
        nx.draw_networkx_edges(G, pos, ax=ax)
        
        ax.title.set_text(title)
    
    plt.tight_layout()
    plt.savefig(filename)
    plt.show()