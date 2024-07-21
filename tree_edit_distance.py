import json
import sys
from apted import APTED, Config
import re

# Define a class to represent a tree node
class TreeNode:
    def __init__(self, label, children=None):
        self.label = label
        self.children = children if children is not None else []

    def __repr__(self):
        return f"TreeNode({self.label}, {self.children})"

# Function to convert JSON to TreeNode
def json_to_tree(json_obj, file_name):
    # Debugging: Print the type and content of json_obj
    #print("json_obj type:", type(json_obj))
    #print("json_obj content:", json_obj)

    # Handle the nested list structure
    while isinstance(json_obj, list):
        json_obj = json_obj[0]

    # Debugging: Print the current json_obj after handling list
    #print("Processed json_obj type:", type(json_obj))
    #print("Processed json_obj content:", json_obj)

    # Check if the 'Plan' key exists
    if "Plan" in json_obj:
        json_obj = json_obj["Plan"]

    label = str(json_obj["Node Type"])

    str_combined = '{"Node Type": "' + label + '"'

    red = "\033[91m"
    white = "\033[0m"
    green = "\033[92m"
    yellow = "\033[93m"
    
    attributes = ['CTE Name', 'Cache Key', 'Filter', 'Group Key', 'Hash Cond',
       'Hash Key', 'Index Cond', 'Index Name', 'Join Filter', 'Join Type',
       'Merge Cond', 'Output', 'Recheck Cond', 'Relation Name',
       'Sort Key', 'One-Time Filter']

    for attr in attributes:
        if attr not in json_obj:
            json_obj[attr] = "None"#f'{red}None{white}'

    match label:
        case "Seq Scan":
            str_combined += ', "Filter": "' + str(json_obj["Filter"]) + '"'
            str_combined += ', "Relation Name": "' + str(json_obj["Relation Name"]) + '"'
            str_combined += ', "Output": "' + str(json_obj["Output"]) + '"'
        case "Index Scan":
            str_combined += ', "Filter": "' + str(json_obj["Filter"]) + '"'
            str_combined += ', "Relation Name": "' + str(json_obj["Relation Name"]) + '"'
            str_combined += ', "Output": "' + str(json_obj["Output"]) + '"'
            str_combined += ', "Index Name": "' + str(json_obj["Index Name"]) + '"'
            str_combined += ', "Index Cond": "' + str(json_obj["Index Cond"]) + '"'
        case "Index Only Scan":
            str_combined += ', "Filter": "' + str(json_obj["Filter"]) + '"'
            str_combined += ', "Relation Name": "' + str(json_obj["Relation Name"]) + '"'
            str_combined += ', "Output": "' + str(json_obj["Output"]) + '"'
            str_combined += ', "Index Name": "' + str(json_obj["Index Name"]) + '"'
            str_combined += ', "Index Cond": "' + str(json_obj["Index Cond"]) + '"'
        case "Bitmap Heap Scan":
            str_combined += ', "Filter": "' + str(json_obj["Filter"]) + '"'
            str_combined += ', "Relation Name": "' + str(json_obj["Relation Name"]) + '"'
            str_combined += ', "Output": "' + str(json_obj["Output"]) + '"'
            str_combined += ', "Recheck Cond": "' + str(json_obj["Recheck Cond"]) + '"'
        case "Bitmap Index Scan":
            str_combined += ', "Index Name": "' + str(json_obj["Index Name"]) + '"'
            str_combined += ', "Index Cond": "' + str(json_obj["Index Cond"]) + '"'
        case "CTE Scan":
            str_combined += ', "CTE Name": "' + str(json_obj["CTE Name"]) + '"'
            str_combined += ', "Filter": "' + str(json_obj["Filter"]) + '"'
            str_combined += ', "Output": "' + str(json_obj["Output"]) + '"'
        case "Hash Join":
            str_combined += ', "Filter": "' + str(json_obj["Filter"]) + '"'
            str_combined += ', "Join Filter": "' + str(json_obj["Join Filter"]) + '"'
            str_combined += ', "Output": "' + str(json_obj["Output"]) + '"'
            str_combined += ', "Hash Cond": "' + str(json_obj["Hash Cond"]) + '"'
            str_combined += ', "Join Type": "' + str(json_obj["Join Type"]) + '"'
        case "Merge Join":
            str_combined += ', "Filter": "' + str(json_obj["Filter"]) + '"'
            str_combined += ', "Join Filter": "' + str(json_obj["Join Filter"]) + '"'
            str_combined += ', "Output": "' + str(json_obj["Output"]) + '"'
            str_combined += ', "Join Type": "' + str(json_obj["Join Type"]) + '"'
            str_combined += ', "Merge Cond": "' + str(json_obj["Merge Cond"]) + '"'
        case "Nested Loop":
            str_combined += ', "Filter": "' + str(json_obj["Filter"]) + '"'
            str_combined += ', "Join Filter": "' + str(json_obj["Join Filter"]) + '"'
            str_combined += ', "Output": "' + str(json_obj["Output"]) + '"'
            str_combined += ', "Join Type": "' + str(json_obj["Join Type"]) + '"'
        case "Aggregate":
            str_combined += ', "Filter": "' + str(json_obj["Filter"]) + '"'
            str_combined += ', "Group Key": "' + str(json_obj["Group Key"]) + '"'
            str_combined += ', "Output": "' + str(json_obj["Output"]) + '"'
            str_combined += ', "Hash Key": "' + str(json_obj["Hash Key"]) + '"'
        case "Group":
            str_combined += ', "Group Key": "' + str(json_obj["Group Key"]) + '"'
            str_combined += ', "Hash Key": "' + str(json_obj["Hash Key"]) + '"'
            str_combined += ', "Output": "' + str(json_obj["Output"]) + '"'
        case "Hash"|"Limit"| "Materialize"| "Unique"| "WindowAgg"| "SetOp":
            str_combined += ', "Output": "' + str(json_obj["Output"]) + '"'
        case "Memoize":
            str_combined += ', "Cache Key": "' + str(json_obj["Cache Key"]) + '"'
            str_combined += ', "Output": "' + str(json_obj["Output"]) + '"'
        case "Sort":
            str_combined += ', "Sort Key": "' + str(json_obj["Sort Key"]) + '"'
            str_combined += ', "Output": "' + str(json_obj["Output"]) + '"'
        case "Incremental Sort":
            str_combined += ', "Sort Key": "' + str(json_obj["Sort Key"]) + '"'
            str_combined += ', "Output": "' + str(json_obj["Output"]) + '"'
        case "Subquery Scan":
            str_combined += ', "Filter": "' + str(json_obj["Filter"]) + '"'
            str_combined += ', "Output": "' + str(json_obj["Output"]) + '"'
        case "Append"| "BitmapAnd"| "BitmapOr":
            str_combined = str_combined
        case "Result":
            str_combined += ', "Output": "' + str(json_obj["Output"]) + '"'
            str_combined += ', "One-Time Filter": "' + str(json_obj["One-Time Filter"]) + '"'
        case "Merge Append":
            str_combined = ', "Sort Key": "' + str(json_obj["Sort Key"]) + '"'
        case _:
            raise(Exception(f"{red}Unsupported Node Type: [{label}]{white}"))
        
    str_combined += "}"
    str_combined = re.sub(r'\'\((.*?)\)\'', r"'\1'", str_combined)
    str_combined = re.sub(r'\(([^()\s]+)\)::date', r'\1::date', str_combined)
    str_combined = re.sub(r'\(([^()\s]+)\)::numeric', r'\1::numeric', str_combined)
    str_combined = re.sub(r'\(([^()\s]+)\)::text', r'\1::text', str_combined)
    str_combined = re.sub(r'\(([^()\s]+)\)::int', r'\1::int', str_combined)
    str_combined = str_combined.replace("::datee", f"")
    str_combined = str_combined.replace("::date", f"")
    str_combined = str_combined.replace("::numericc", f"")
    str_combined = str_combined.replace("::numeric", f"")
    str_combined = str_combined.replace("::textt", f"")
    str_combined = str_combined.replace("::text", f"")
    str_combined = str_combined.replace("::intt", f"")#f"{green}::int{white}")
    str_combined = str_combined.replace("::int", f"")#f"{green}::int{white}")

    str_combined = re.sub(r'\'([0-9]+\.[0-9]+)\'', r'\1', str_combined)
    str_combined = re.sub(r'\'([0-9]+)\'', r'\1', str_combined)
    
    # print(str_combined)
    with open(file_name, "a", encoding="utf-8") as file:
        file.write(str_combined + "\n")

    children = [json_to_tree(child,file_name) for child in json_obj.get("Plans", [])]
    return TreeNode(str_combined, children)

# Function to read JSON file and convert to TreeNode
# def read_json_file(file_path):
#     with open(file_path, "r") as file:
#         json_obj = json.load(file)
#         return json_to_tree(json_obj)

# Custom Config class to handle tree nodes
class TreeConfig(Config):
    def rename(self, node1, node2):
        """Compares attribute .value of trees"""
        return 1 if node1.label != node2.label else 0

    def children(self, node):
        """Get left and right children of binary tree"""
        return node.children

# def main(file1, file2):
#     # Read and parse the JSON files
    
#     tree1 = read_json_file(file1)
#     tree2 = read_json_file(file2)

def main(res1, res2):
    red = "\033[91m"
    white = "\033[0m"
    yellow = "\033[93m"
    # print(f"{yellow}AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA{white}")
    # clear the contexts of files query1.txt and query2.txt
    with open("query1.txt", "w") as file:
        file.write("")
    with open("query2.txt", "w") as file:
        file.write("")
    # print(f"============={red} Calling json_to_tree for TREE1 {white}=============")
    tree1 = json_to_tree(res1, "query1.txt")
    
    # print(f"============={red} Calling json_to_tree for TREE2 {white}=============")
    tree2 = json_to_tree(res2, "query2.txt")
    
    # Initialize APTED with the custom config
    apted = APTED(tree1, tree2, TreeConfig())

    # Compute the tree edit distance
    ted = apted.compute_edit_distance()
    # print(ted.delta)
    ted = ted.result
    # mapping = apted.compute_edit_mapping()

    # print(f"{ted}")
    return ted
    # Uncomment the following line if you want to print the mapping
    # print(f"Mapping: {mapping}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"FOUND: {sys.argv}<<<")
        print("Usage: python tree_edit_distance.py <file1> <file2>")
        sys.exit(1)
    
    file1 = sys.argv[1]
    file2 = sys.argv[2]
    # main(file1, file2)
