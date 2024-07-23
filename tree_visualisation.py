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
        return node.label

def add_nodes(graph, node):
    if not isinstance(node, TreeNode):
        raise TypeError(f"Expected a TreeNode instance, got {type(node).__name__}")
    graph.add_node(node, label=extract_properties(node))
    # print(f"Label {node.label} has {len(node.children)} children ")
    for child in node.children:
        graph.add_edge(node, child)
        add_nodes(graph, child)

def get_node_size_and_font(label):
    # Calculate the node size and font size based on the length of the label
    splt = label.split('\n')
    lst = [len(x) for x in splt if x != None]
    lst.append(len(splt))
    label_length = max(lst)
    # print(label_length)
    node_size =  50 * label_length  # Adjust node size based on label length
    font_size = min(10 + 2 * label_length, 5)  # Adjust font size within a range
    return node_size, font_size

def plot_trees(tree1, tree2 ,edit_mapping , filename):
    # print (edit_mapping)
    if isinstance(tree1, dict):
        tree1 = json_to_tree(tree1, "tree1")
    if isinstance(tree2, dict):
        tree2 = json_to_tree(tree2, "tree2")
    
    fig, axs = plt.subplots(1, 2, figsize=(18, 12))
    # for ax, tree, title in zip(axs, [tree1, tree2], ["Query Execution Plan 1", "Query Execution Plan 2"]):
    #     G = nx.DiGraph()
    #     add_nodes(G, tree)
    #     pos = graphviz_layout(G, prog='dot')
    #     labels = nx.get_node_attributes(G, 'label')
    #     red = '\033[91m'
    #     white = '\033[0m'
    #     # Draw the graph with dynamically adjusted node sizes and font sizes
    #     for node, label in labels.items():
    #         color = 'red'
    #         for key, value in edit_mapping:
    #             if (node == value and key != None):# and node.label == key.label:
    #                 print(f"FOUNDDDD1 {value} {red}->{white} {key}")
    #                 color = 'green'
    #                 break
    #             if (node == key and value != None):# and node.label == value.label:
    #                 print(f"FOUNDDDD2 {value} {red}->{white} {key}")
    #                 color = 'green'
    #                 break
    #         if color == 'red':
    #             print(f"NOT FOUND {node}")
    #         print(f"Node: {node}, Label: {label}")
    #         node_size, font_size = get_node_size_and_font(label)
    #         nx.draw_networkx_nodes(G, pos, nodelist=[node], node_size=node_size, node_shape='o', node_color=color, alpha=0.8, ax=ax)
    #         nx.draw_networkx_labels(G, pos, labels={node: label}, font_size=font_size, font_color='black', font_weight='bold', verticalalignment='center', horizontalalignment='center', ax=ax)
    #     nx.draw_networkx_edges(G, pos, ax=ax)
        
    #     ax.title.set_text(title)

    G1 = nx.DiGraph()
    G2 = nx.DiGraph()
    add_nodes(G1, tree1)
    # print("Tree 1 DONE BISH")
    add_nodes(G2, tree2)
    pos1 = graphviz_layout(G1, prog='dot')
    pos2 = graphviz_layout(G2, prog='dot')
    labels1 = nx.get_node_attributes(G1, 'label')
    labels2 = nx.get_node_attributes(G2, 'label')

    for node1, label1 in labels1.items():
        color = 'red'
        for _,label2 in labels2.items():
            if label1 == label2:
                color = 'green'
                break
        node_size, font_size = get_node_size_and_font(node1.label)
        nx.draw_networkx_nodes(G1, pos1, nodelist=[node1], node_size=node_size, node_shape='o', node_color=color, alpha=0.8, ax=axs[0])
        nx.draw_networkx_labels(G1, pos1, labels={node1: label1}, font_size=font_size, font_color='black', font_weight='bold', verticalalignment='center', horizontalalignment='center', ax=axs[0])
    nx.draw_networkx_edges(G1, pos1, ax=axs[0])
    
    for node2, label2 in labels2.items():
        color = 'red'
        for _,label1 in labels1.items():
            if label1 == label2:
                color = 'green'
                break
        node_size, font_size = get_node_size_and_font(node2.label)
        nx.draw_networkx_nodes(G2, pos2, nodelist=[node2], node_size=node_size, node_shape='o', node_color=color, alpha=0.8, ax=axs[1])
        nx.draw_networkx_labels(G2, pos2, labels={node2: label2}, font_size=font_size, font_color='black', font_weight='bold', verticalalignment='center', horizontalalignment='center', ax=axs[1])
    nx.draw_networkx_edges(G2, pos2, ax=axs[1])
    # print(tree1)
    plt.tight_layout()
    plt.savefig(filename)
    plt.show()