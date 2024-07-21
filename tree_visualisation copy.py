import pygraphviz as pgv
from treelib import Node, Tree

class PlanNode:
    def __init__(self, label, node_type=None, str_combined=None, color='black'):
        self.label = label
        self.node_type = node_type
        self.str_combined = str_combined
        self.color = color

def convert_to_expected_format(plan, parent_id=None, tree=None, counter=[0]):
    if tree is None:
        tree = {}
    node_id = counter[0]
    plan_node = PlanNode(label=plan['Node Type'], node_type=plan.get('Node Type'), str_combined=str(plan))
    tree[node_id] = {'node': plan_node, 'children': []}
    if parent_id is not None:
        tree[parent_id]['children'].append(node_id)
    counter[0] += 1
    
    # Recursively handle sub-plans
    if 'Plans' in plan:
        for sub_plan in plan['Plans']:
            convert_to_expected_format(sub_plan, node_id, tree, counter)
    
    return tree

def create_graphviz_tree(plan, graph, offset, color='black'):

    tree = convert_to_expected_format(plan)

    for node_id, data in tree.items():
        node = data['node']
        label = f"{node.label}\n{node.str_combined}"
        graph.add_node(f"{offset}_{node_id}", label=label, color=color)
        for child_id in data['children']:
            graph.add_edge(f"{offset}_{node_id}", f"{offset}_{child_id}")
    return graph

def plot_trees(tree1, tree2, output_file='execution_plans.png'):
    graph = pgv.AGraph(strict=False, directed=True)
    graph = create_graphviz_tree(tree1, graph, "tree1", color='black')
    graph = create_graphviz_tree(tree2, graph, "tree2", color='black')

    graph.layout(prog='dot')
    graph.draw(output_file)
    print(f"Execution plans have been drawn side by side and saved as '{output_file}'.")