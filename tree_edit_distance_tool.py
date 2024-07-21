import psycopg2
import os
import sys
import json
import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout
from tree_edit_distance import main as compare
from tree_visualisation import plot_trees
import platform

# DEBUG = False
# STORE = False
# PLOT = True
# ANALYZE = False

def preprocess_query(query, analyze=False, debug=False):
    # Check if the query is a SELECT statement or similar DML statement
    dml_statements = ['select', 'insert', 'update', 'delete', 'with']
    if any(query.strip().lower().startswith(stmt) for stmt in dml_statements):
        explain_type = "EXPLAIN (ANALYZE, FORMAT JSON)" if analyze else "EXPLAIN (FORMAT JSON)" 
        query = f" {explain_type} {query}"
    if debug:
        print(f"Preprocessed query: [{query}]")
    return query

def run_query(database, user, password, host, port, query, analyze=False, debug=False, store=False, output_file=None):
    try:
        connection = psycopg2.connect(
            dbname=database,
            user=user,
            password=password,
            host=host,
            port=port
        )

        cursor = connection.cursor()
        
        # original_query = query
        for q in query.split(";"):
            # q = q.strip()
            if not q:
                continue
            q = preprocess_query(q, analyze, debug)
            if debug:
                print(f"Executing query:<{q}>")
            cursor.execute(q)
            if q.strip().lower().startswith(('explain')):
                result = cursor.fetchall()
                if debug:
                    print("EXPLAIN output:")
                    for row in result:
                        print(row[0])
                if store and output_file:
                    with open(output_file, 'w') as outfile:
                        json.dump(result, outfile, indent=4)
                    if debug:
                        print(f"EXPLAIN output written to {output_file}")
                return result
            else:
                connection.commit()
                if debug:
                    print("Query executed successfully")
    except Exception as error:
        print(f"Error: {error}")
    finally:
        # if cursor:
        #     cursor.close()
        # if connection:
        #     connection.close()
        # return result
        cursor.close()
        connection.close()

def extract_filename(file_path):
    return os.path.basename(file_path)

# def intersection(lst1, lst2):
#     return list(set(lst1) & set(lst2))

# def visualize_plan_with_networkx(plan1, plan2, filename1, filename2, debug=False):
    def add_nodes(graph, plan, parent=None, prefix=""):
        node_id = prefix + str(id(plan))
        label = plan["Node Type"]
        graph.add_node(node_id, label=label)
        if parent:
            graph.add_edge(parent, node_id)
        for i, child in enumerate(plan.get("Plans", [])):
            add_nodes(graph, child, node_id, prefix=f"{prefix}{i}_")

    # For every node in the left tree call the function to find the matching nodes in the right tree   
    def find_matching_nodes(node, tree, other_tree, dictionary1, dictionary2, sequences1, sequences2):  
        # Iterate over all possible nodes in the right tree in a reverse topological order
        for other_node in reversed(list(nx.topological_sort(other_tree))):
            if debug:
                print(f"Currently node: {node}")
            # Check if the labels match
            if other_tree.nodes[other_node]['label'] == tree.nodes[node]['label'] and other_tree.out_degree(other_node) == tree.out_degree(node):
                if debug:
                    print(f"Testing for P1 node: {node} to match with {other_node}")
                # If the node is a leaf node for both trees then it is a match
                if tree.out_degree(node) == 0 and other_tree.out_degree(other_node) == 0:
                    if debug:
                        print(f"\t [+] Matched: {node} with {other_node}")
                        print(f"Node: {node} has sequence>>> {sequences1[node]}")
                    # Add the matching nodes to the dictionary as potential matches for eachother
                    dictionary1.setdefault(node, []).append(other_node)
                    dictionary2.setdefault(other_node, []).append(node)
                    # For a leaf node the sequence of matches is just itself i.e. 1
                    sequences1[node] = 1
                    sequences2[other_node] = 1
                    continue
                # For intermediary nodes check if the children match
                children = tree.successors(node)
                other_children = other_tree.successors(other_node)
                # Initially assume that the nodes can match unless we find a child that doesn't match
                can_match = True
                # Concurrently iterate over the children in a leftmost-first manner
                c1 = next(children)
                c2 = next(other_children)
                if debug:
                    print(f"\t Started Testing children of {node} with {other_node}")
                # Repeat until I reach the end of the children of the node or until I find a child that doesn't match
                while c1!=None and c2!=None:
                    if debug:
                        print(f"\t Testing children from P1: {c1} with children from P2: {c2}")
                    # If both children have potential matches in their corresponding dictionaries
                    if c1 in dictionary1 and c2 in dictionary2:
                        # Check if the child of the left tree is NOT a potential match with the corresponding child in the right tree and vice versa
                        if (c2 not in dictionary1[c1]) or (c1 not in dictionary2[c2]):
                            can_match = False
                            if debug:
                                print(f"\t [-] Failed to match {c1} with {c2}")
                            break
                    else:
                        # We can't match the children if one of them doesn't have a potential match
                        can_match = False
                        if debug:
                            print(f"\t [-] Testing intermediary with final node: {c1} with {c2} failed")
                        break
                    # Move to the next children
                    c1 = next(children, None)
                    c2 = next(other_children, None)
                if debug:
                    print(f"\t Finished testing children of {node} with {other_node}")
                # If all children matched then the nodes can match
                if can_match:
                    # Calculate the sequence of matches for the node
                    sequential_matches = 1
                    # Add the amount of matches of the children to the amount of matches of the current node +1
                    for child in tree.successors(node):
                        # Make sure that the child has been matched
                        assert child in sequences1
                        sequential_matches += sequences1[child]
                    dictionary1.setdefault(node,[]).append(other_node)
                    dictionary2.setdefault(other_node,[]).append(node)
                    if debug:
                        print(f"Node: {node} has sequence>>> {sequential_matches}")
                    # Add the number of matches to the sequence
                    sequences1[node] = sequential_matches
                    sequences2[other_node] = sequential_matches
                    if debug:
                        print(f"\t [+] Matched: {node} with {other_node}")
        # Return the updated dictionaries and sequences
        return dictionary1, dictionary2, sequences1, sequences2
    '''
        Downpropagate the matches from the root to the leaves
        Given a node in the left tree, find the corresponding node in the right tree
        If the node has no matches then color it red
    '''
    def downpropagate(node1, tree1, tree2, dictionary1, dictionary2, sequences1, sequences2):
        # Firstly, check if the node has any potential matches
        if node1 in dictionary1:
            can_match = False
            maxn = 0
            potential_match = None
            for vertex in dictionary1[node1]:
                # From the list of potential matches in dictionary choose the one with the highest amount of matches
                if vertex in dictionary2 and sequences2[vertex] > maxn :
                    maxn = sequences2[vertex]
                    potential_match = vertex
                    can_match = True
                    if debug:
                        print(f"Potential match: {node1} with {potential_match} with maxn {maxn}")
            if can_match:
                if debug:
                    print(f"Matched {node1} with {potential_match}")
                sequences2.pop(potential_match)
                del dictionary1[node1]
                del dictionary2[potential_match]
            else:
                try:
                    tree1.nodes[node1]['color'] = 'red'
                    tree2.nodes[potential_match]['color'] = 'red'
                except:
                    if debug:
                        print(f"Failed to color {node1} with {potential_match}")
        else:
            if debug:
                print(f"Failed to match {node1} because no [matches found]")
            tree1.nodes[node1]['color'] = 'red'
            if debug:
                print(f"Failed to match {node1} because no [matches found]")
        return sequences1, sequences2, dictionary1, dictionary2
    '''
        Use this function to give the children of a node the same sequence of matches as the parent node
        Do this so that reguardless of where a node is in any sequence we can ask for the length of the sequence it belongs to
        By doing that we can start iterating over the nodes that belong in the highest sequence of matches
    '''
    def push_sequences_to_children(tree, sequences):
        # Start from the root node and go down the tree
        for node in (list(nx.topological_sort(tree))):
            # For all non-leaf nodes push the sequence of matches to the children
            if tree.out_degree(node) > 0:
                children = tree.successors(node)
                for child in children:
                    # If the node belongs in any sequence of matches
                    if node in sequences:
                        # Then all of its children belong in the same sequence
                        sequences[child] = sequences[node]
                        if debug:
                            print(f"Node: {child} has sequence: {sequences[child]}")

    '''
        ENTRY POINT!!!
        Compare the matches of the nodes in the left tree with the nodes in the right tree
        Given tree1 and tree2, the function colors the nodes that don't have a match in the other tree
    '''
    def compare_nodes(tree1, tree2):
        # Holds potential matches for each node in the left tree
        dictionary1 = {}
        # Holds potential matches for each node in the right tree
        dictionary2 = {}

        # Holds the amount of matches for each node in the left tree
        sequences1 = {}
        # Holds the amount of matches for each node in the right tree
        sequences2 = {}

        # Iterate over the nodes in the left tree in a reverse topological order
        # i.e. starting from the leaves and going up to the root
        for node in reversed(list(nx.topological_sort(tree1))):
            if debug:
                print(f"Node: {node}")
            # For every node in the left tree find the matching nodes in the right tree
            dictionary1, dictionary2, sequences1, sequences2 = find_matching_nodes(node, tree1, tree2, dictionary1, dictionary2, sequences1, sequences2)

        if debug:
            print(f"Dictionary 1: {dictionary1}")
            print(f"Dictionary 2: {dictionary2}")    

        
        push_sequences_to_children(tree1, sequences1)
        push_sequences_to_children(tree2, sequences2)
        # Mark nodes with no matches as red
        for nodes in tree1.nodes - sequences1:
            sequences1[nodes] = 0
        for nodes in tree2.nodes - sequences2:
            sequences2[nodes] = 0
        # sort sequences1 and sequences2 based on the amount of matches of each node
        # use this information to dwonpropagate the matches starting from the nodes with the highest amount of matches
        sequences1 = {k: v for k, v in sorted(sequences1.items(), key=lambda item: item[1], reverse=True)}
        sequences2 = {k: v for k, v in sorted(sequences2.items(), key=lambda item: item[1], reverse=True)}
        for node in sequences1:
            sequences1, sequences2, dictionary1, dictionary2 = downpropagate(node, tree1, tree2, dictionary1, dictionary2, sequences1, sequences2)
        for node in sequences2:
            downpropagate(node, tree2, tree1, dictionary2, dictionary1, sequences2, sequences1)

    G1 = nx.DiGraph()
    G2 = nx.DiGraph()

    add_nodes(G1, plan1, prefix="P1_")
    add_nodes(G2, plan2, prefix="P2_")

    compare_nodes(G1, G2)

    pos1 = graphviz_layout(G1, prog='dot')
    pos2 = graphviz_layout(G2, prog='dot')

    plt.figure(figsize=(15, 10))

    plt.subplot(121)
    labels1 = nx.get_node_attributes(G1, 'label')
    colors1 = [G1.nodes[node].get('color', 'green') for node in G1]
    nx.draw(G1, pos1, labels=labels1, with_labels=True, node_size=3000, node_color=colors1, font_size=10, font_weight='bold', arrowsize=20)
    plt.title(f"Execution Plan 1: {filename1}")

    plt.subplot(122)
    labels2 = nx.get_node_attributes(G2, 'label')
    colors2 = [G2.nodes[node].get('color', 'green') for node in G2]
    nx.draw(G2, pos2, labels=labels2, with_labels=True, node_size=3000, node_color=colors2, font_size=10, font_weight='bold', arrowsize=20)
    plt.title(f"Execution Plan 2: {filename2}")

    plt.savefig(f"comparison_{filename1}_{filename2}.png")
    plt.show()

def main(query_file1, query_file2, plot=False, debug=False, store=False, analyze=False):
    # DATABASE = "tpch"
    # USER = "postgres"
    # PASSWORD = "password"
    # HOST = "localhost"
    # PORT = "5432"
    # DATABASE2 = "tpch2"
    # USER2 = "postgres"
    # PASSWORD2 = "password"
    # HOST2 = "localhost"
    # PORT2 = "5432"

    if debug:
        print(f"Running with options: Plot={plot}, Debug={debug}, Store={store}, Analyze={analyze}")

    if os.path.exists("config.json"):
        with open("config.json", "r") as file:
            config = json.load(file)
            DATABASE = config["DB1"]["DATABASE"]
            USER = config["DB1"]["USER"]
            PASSWORD = config["DB1"]["PASSWORD"]
            HOST = config["DB1"]["HOST"]
            PORT = config["DB1"]["PORT"]
            DATABASE2 = config["DB2"]["DATABASE"]
            USER2 = config["DB2"]["USER"]
            PASSWORD2 = config["DB2"]["PASSWORD"]
            HOST2 = config["DB2"]["HOST"]
            PORT2 = config["DB2"]["PORT"]
    else:
        print("config.json file not found. Using default values.")
    
    with open(query_file1, 'r') as file:
        query1 = file.read().strip()
    
    with open(query_file2, 'r') as file:
        query2 = file.read().strip()

    
    output_file1 = extract_filename(query_file1).replace('.sql', '_explain.json') if store else None
    output_file2 = extract_filename(query_file2).replace('.sql', '_explain.json') if store else None
    if output_file1 == output_file2 and output_file1 is not None:
        output_file2 = output_file1.replace('.json', '_2.json')

    
    result1 = run_query(DATABASE, USER, PASSWORD, HOST, PORT, query1, analyze, debug, store, output_file1)
    result2 = run_query(DATABASE2, USER2, PASSWORD2, HOST2, PORT2, query2, analyze, debug, store, output_file2)
    # print(f"Results: {result1} and {result2}")
    if result1 and result2:
        plan1 = result1[0][0][0]["Plan"]
        plan2 = result2[0][0][0]["Plan"]

        # Calculate Tree-Edit Distance
        comparison_result, tree1_json, tree2_json = compare(result1[0][0][0], result2[0][0][0])
        # Calculate Tree-Edit Distance
        # ted = compare(plan1, plan2)

        # separator = "/"
        # if platform.system() == "Windows":
        #     separator = "\\"
        # qq = query_file1.split(separator)

        filename1 = extract_filename(query_file1).replace('.sql', '')
        filename2 = extract_filename(query_file2).replace('.sql', '')

        if plot:
            print("Plotting the execution plans")
            plot_trees(tree1_json, tree2_json, f"execution_plans_{filename1}_{filename2}.png")
            # Visualize Combined Plans with Networkx
            # visualize_plan_with_networkx(plan1, plan2, filename1, filename2, debug) #qq[-1])

        json_output = {
            "query1": query_file1,
            "query2": query_file2,
            "comparison_result": comparison_result
        }

        if analyze:
            actual_time1 = plan1["Actual Total Time"]
            actual_time2 = plan2["Actual Total Time"]
            time_difference = abs(actual_time1 - actual_time2)
            json_output["actual_time1"] = actual_time1
            json_output["actual_time2"] = actual_time2
            json_output["time_difference"] = time_difference

        if store:
            output_file = f"comparison_result_{filename1}_{filename2}.json"
            with open(output_file, 'w') as file:
                json.dump(json_output, file)
            if debug:
                print(f"Results stored in {output_file}")

        print(json.dumps(json_output))
        return json.dumps(json_output)

    else:
        print("Error: Query execution failed")
        return None
    

if __name__ == "__main__":
    # if len(sys.argv) != 3:
    #     print("Usage: tree_edit_distance_tool.py $query_file1 $query_file2")
    #     sys.exit(1)
    
    # main(sys.argv[1], sys.argv[2])

    import argparse
    
    parser = argparse.ArgumentParser(description="Compare execution plans of SQL queries.")
    parser.add_argument("query_file1", help="File containing the first SQL query")
    parser.add_argument("query_file2", help="File containing the second SQL query")
    parser.add_argument("--plot", action="store_true", help="Plot the execution plans")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--store", action="store_true", help="Store the results in a file")
    parser.add_argument("--analyze", action="store_true", help="Use EXPLAIN ANALYZE instead of EXPLAIN")

    args = parser.parse_args()
    main(args.query_file1, args.query_file2, args.plot, args.debug, args.store, args.analyze)