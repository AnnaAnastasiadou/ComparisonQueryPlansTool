import json
import sys
from apted import APTED, Config
import re

# Define a class to represent a tree node
class TreeNode:
    def __init__(self, label, children=None):
        """
        Initialize a tree node with a label and optional children.
        
        Args:
            label (str): The label of the tree node.
            children (list of TreeNode, optional): The child nodes of this node. Defaults to an empty list if None.
        """
        self.label = label
        self.children = children if children is not None else []

    def __repr__(self):
        """
        String representation of the TreeNode for debugging purposes.
        
        Returns:
            str: A string representation of the TreeNode.
        """
        return f"TreeNode({self.label}, {self.children})"
    

def json_to_tree(json_obj):
    """
    Convert a JSON object representing an execution plan to a TreeNode object.
    
    Args:
        json_obj (dict or list): The JSON object representing the result of the EXPLAIN (ANALYZE).
        
    Returns:
        TreeNode: The root node of the tree representing the execution plan.
    """

    # Handle the case where json_obj is a list; take the first element
    while isinstance(json_obj, list):
        print("list")
        json_obj = json_obj[0]

    # Extract the execution plan from the EXPLAIN result
    if "Plan" in json_obj:
        json_obj = json_obj["Plan"]

    # Get the type of the node and start constructing the label
    label_type = str(json_obj["Node Type"])

    label = '{"Node Type": "' + label_type + '"'
    
    # Define a list of attributes that may be present in the node
    attributes = ['CTE Name', 'Cache Key', 'Filter', 'Group Key', 'Hash Cond',
       'Hash Key', 'Index Cond', 'Index Name', 'Join Filter', 'Join Type',
       'Merge Cond', 'Output', 'Recheck Cond', 'Relation Name',
       'Sort Key', 'One-Time Filter']

    # Check for each attribute and add it to the node's JSON representation
    for attr in attributes:
        if attr not in json_obj:
            json_obj[attr] = "None" # Default value if attribute is missing
        else:
            # Replace double quotes with backticks for JSON formatting
            json_obj[attr] = re.sub(r'(?<!\\)"', r'`', str(json_obj[attr]))

    # Add attributes to the label based on the node type
    match label_type:
        case "Seq Scan":
            label += ', "Filter": "' + str(json_obj["Filter"]) + '"'
            label += ', "Relation Name": "' + str(json_obj["Relation Name"]) + '"'
            label += ', "Output": "' + str(json_obj["Output"]) + '"'
        case "Index Scan":
            label += ', "Filter": "' + str(json_obj["Filter"]) + '"'
            label += ', "Relation Name": "' + str(json_obj["Relation Name"]) + '"'
            label += ', "Output": "' + str(json_obj["Output"]) + '"'
            label += ', "Index Name": "' + str(json_obj["Index Name"]) + '"'
            label += ', "Index Cond": "' + str(json_obj["Index Cond"]) + '"'
        case "Index Only Scan":
            label += ', "Filter": "' + str(json_obj["Filter"]) + '"'
            label += ', "Relation Name": "' + str(json_obj["Relation Name"]) + '"'
            label += ', "Output": "' + str(json_obj["Output"]) + '"'
            label += ', "Index Name": "' + str(json_obj["Index Name"]) + '"'
            label += ', "Index Cond": "' + str(json_obj["Index Cond"]) + '"'
        case "Bitmap Heap Scan":
            label += ', "Filter": "' + str(json_obj["Filter"]) + '"'
            label += ', "Relation Name": "' + str(json_obj["Relation Name"]) + '"'
            label += ', "Output": "' + str(json_obj["Output"]) + '"'
            label += ', "Recheck Cond": "' + str(json_obj["Recheck Cond"]) + '"'
        case "Bitmap Index Scan":
            label += ', "Index Name": "' + str(json_obj["Index Name"]) + '"'
            label += ', "Index Cond": "' + str(json_obj["Index Cond"]) + '"'
        case "CTE Scan":
            label += ', "CTE Name": "' + str(json_obj["CTE Name"]) + '"'
            label += ', "Filter": "' + str(json_obj["Filter"]) + '"'
            label += ', "Output": "' + str(json_obj["Output"]) + '"'
        case "Hash Join":
            label += ', "Filter": "' + str(json_obj["Filter"]) + '"'
            label += ', "Join Filter": "' + str(json_obj["Join Filter"]) + '"'
            label += ', "Output": "' + str(json_obj["Output"]) + '"'
            label += ', "Hash Cond": "' + str(json_obj["Hash Cond"]) + '"'
            label += ', "Join Type": "' + str(json_obj["Join Type"]) + '"'
        case "Merge Join":
            label += ', "Filter": "' + str(json_obj["Filter"]) + '"'
            label += ', "Join Filter": "' + str(json_obj["Join Filter"]) + '"'
            label += ', "Output": "' + str(json_obj["Output"]) + '"'
            label += ', "Join Type": "' + str(json_obj["Join Type"]) + '"'
            label += ', "Merge Cond": "' + str(json_obj["Merge Cond"]) + '"'
        case "Nested Loop":
            label += ', "Filter": "' + str(json_obj["Filter"]) + '"'
            label += ', "Join Filter": "' + str(json_obj["Join Filter"]) + '"'
            label += ', "Output": "' + str(json_obj["Output"]) + '"'
            label += ', "Join Type": "' + str(json_obj["Join Type"]) + '"'
        case "Aggregate":
            label += ', "Filter": "' + str(json_obj["Filter"]) + '"'
            label += ', "Group Key": "' + str(json_obj["Group Key"]) + '"'
            label += ', "Output": "' + str(json_obj["Output"]) + '"'
            label += ', "Hash Key": "' + str(json_obj["Hash Key"]) + '"'
        case "Group":
            label += ', "Group Key": "' + str(json_obj["Group Key"]) + '"'
            label += ', "Hash Key": "' + str(json_obj["Hash Key"]) + '"'
            label += ', "Output": "' + str(json_obj["Output"]) + '"'
        case "Hash"|"Limit"| "Materialize"| "Unique"| "WindowAgg"| "SetOp":
            label += ', "Output": "' + str(json_obj["Output"]) + '"'
        case "Memoize":
            label += ', "Cache Key": "' + str(json_obj["Cache Key"]) + '"'
            label += ', "Output": "' + str(json_obj["Output"]) + '"'
        case "Sort":
            label += ', "Sort Key": "' + str(json_obj["Sort Key"]) + '"'
            label += ', "Output": "' + str(json_obj["Output"]) + '"'
        case "Incremental Sort":
            label += ', "Sort Key": "' + str(json_obj["Sort Key"]) + '"'
            label += ', "Output": "' + str(json_obj["Output"]) + '"'
        case "Subquery Scan":
            label += ', "Filter": "' + str(json_obj["Filter"]) + '"'
            label += ', "Output": "' + str(json_obj["Output"]) + '"'
        case "Append"| "BitmapAnd"| "BitmapOr":
            label = label # No additional attributes for these types
        case "Result":
            label += ', "Output": "' + str(json_obj["Output"]) + '"'
            label += ', "One-Time Filter": "' + str(json_obj["One-Time Filter"]) + '"'
        case "Merge Append":
            label += ', "Sort Key": "' + str(json_obj["Sort Key"]) + '"'
        case _:
            # Raise an exception if the node type is unsupported
            raise(Exception(f"Unsupported Node Type: [label]"))

    # print(label) 
    
    # Complete the JSON string representation of the node
    label += "}"

    # Clean up specific patterns in the string for proper formatting 
    # and standarization, otherwise TED appears to be bigger than the actual value.
    label = re.sub(r'\'\((.*?)\)\'', r"'\1'", label)
    label = re.sub(r'\(([^()\s]+)\)::date', r'\1::date', label)
    label = re.sub(r'\(([^()\s]+)\)::numeric', r'\1::numeric', label)
    label = re.sub(r'\(([^()\s]+)\)::text', r'\1::text', label)
    label = re.sub(r'\(([^()\s]+)\)::int', r'\1::int', label)
    label = label.replace("::datee", f"")
    label = label.replace("::date", f"")
    label = label.replace("::numericc", f"")
    label = label.replace("::numeric", f"")
    label = label.replace("::textt", f"")
    label = label.replace("::text", f"")
    label = label.replace("::intt", f"")
    label = label.replace("::int", f"")

    label = re.sub(r'\'([0-9]+\.[0-9]+)\'', r'\1', label)
    label = re.sub(r'\'([0-9]+)\'', r'\1', label)
    
    # Recursively convert child nodes to TreeNodes
    children = [json_to_tree(child) for child in json_obj.get("Plans", [])]
    return TreeNode(label, children)

class TreeConfig(Config):
    def rename(self, node1, node2):
        """
        Compare nodes based on their label value.
        
        Args:
            node1 (TreeNode): The first node.
            node2 (TreeNode): The second node.
        
        Returns:
            int: Return 1 if the nodes are not equal, else 0.
        """
        return 1 if node1.label != node2.label else 0

    def children(self, node):
        """
        Get the children of a node.
        
        Args:
            node (TreeNode): The node whose children are to be retrieved.
        
        Returns:
            list of TreeNode: The children of the node.
        """
        return node.children

def main(res1, res2):
    """
    Compute the tree edit distance between two execution plan JSON objects.
    
    Args:
        res1 (dict or list): The first JSON object.
        res2 (dict or list): The second JSON object.
        
    Returns:
        tuple: A tuple containing the tree edit distance and tree nodes for the first and second JSON objects.
    """

    # Convert JSON objects to TreeNode representations
    tree1 = json_to_tree(res1)
    tree2 = json_to_tree(res2)
    
    # Initialize APTED with the custom config for tree comparison
    apted = APTED(tree1, tree2, TreeConfig())

    # Compute the tree edit distance
    ted = apted.compute_edit_distance().result
    
    # Uncomment the following line if you want to print the mapping
    # mapping = apted.compute_edit_mapping()
    # print(f"Mapping: {mapping}")

    return ted, tree1, tree2
