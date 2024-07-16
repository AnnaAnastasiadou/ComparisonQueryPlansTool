import psycopg2
import os
import sys
import json
import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout
from tree_edit_distance import main as compare
import platform

DEBUG = False
STORE = False

def preprocess_query(query):
    dml_statements = ['select', 'insert', 'update', 'delete']
    if any(query.strip().lower().startswith(stmt) for stmt in dml_statements):
        query = 'EXPLAIN (FORMAT JSON) ' + query
    if DEBUG:
        print(f"Preprocessed query: [{query}]")
    return query

def run_query(database, user, password, host, port, query):
    connection = None
    cursor = None
    try:
        connection = psycopg2.connect(
            dbname=database,
            user=user,
            password=password,
            host=host,
            port=port
        )
        cursor = connection.cursor()

        query = preprocess_query(query)
        
        if DEBUG:
            print(f"Executing query: {query}")
        cursor.execute(query)
        if query.strip().lower().startswith('explain'):
            result = cursor.fetchall()
            if DEBUG:
                for row in result:
                    print(row[0])
            if STORE:
                output_file = f"{query}_explain.json"
                with open(output_file, 'w') as outfile:
                    json.dump(result, outfile, indent=4)
                if DEBUG:
                    print(f"EXPLAIN output written to {output_file}")
            return result
        else:
            connection.commit()
            print("Query executed successfully")
    except Exception as error:
        print(f"Error: {error}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    return None

def node_wise_comparison(plan1, plan2):
    def compare_nodes(node1, node2):
        comparisons = []
        if node1["Node Type"] != node2["Node Type"]:
            comparisons.append(f"Node Type: {node1['Node Type']} vs {node2['Node Type']}")
        if node1.get("Total Cost") != node2.get("Total Cost"):
            comparisons.append(f"Total Cost: {node1.get('Total Cost')} vs {node2.get('Total Cost')}")
        if node1.get("Plan Rows") != node2.get("Plan Rows"):
            comparisons.append(f"Plan Rows: {node1.get('Plan Rows')} vs {node2.get('Plan Rows')}")
        return comparisons

    comparisons = compare_nodes(node1=plan1, node2=plan2)
    for child1, child2 in zip(plan1.get("Plans", []), plan2.get("Plans", [])):
        comparisons.extend(node_wise_comparison(child1, child2))
    
    return comparisons

def visualize_plan_with_networkx(plan1, plan2, filename):
    def add_nodes(graph, plan, parent=None, prefix=""):
        node_id = prefix + str(id(plan))
        label = plan["Node Type"]
        graph.add_node(node_id, label=label)
        if parent:
            graph.add_edge(parent, node_id)
        for i, child in enumerate(plan.get("Plans", [])):
            add_nodes(graph, child, node_id, prefix=f"{prefix}{i}_")

    G = nx.DiGraph()

    # Add nodes and edges for plan1
    add_nodes(G, plan1, prefix="P1_")

    # Add nodes and edges for plan2
    add_nodes(G, plan2, prefix="P2_")

    pos = graphviz_layout(G, prog='dot')

    labels = nx.get_node_attributes(G, 'label')
    plt.figure(figsize=(15, 10))
    nx.draw(G, pos, labels=labels, with_labels=True, node_size=3000, node_color='lightblue', font_size=10, font_weight='bold', arrowsize=20)
    plt.title("Comparison of Execution Plans")
    plt.savefig(f"comparison_{filename}.png")
    plt.show()

def main(query_file1, query_file2):
    DATABASE = "tpch"
    USER = "postgres"
    PASSWORD = "password"
    HOST = "localhost"
    PORT = "5432"
    DATABASE2 = "tpch2"
    USER2 = "postgres"
    PASSWORD2 = "password"
    HOST2 = "localhost"
    PORT2 = "5432"

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

    result1 = run_query(DATABASE, USER, PASSWORD, HOST, PORT, query1)
    result2 = run_query(DATABASE2, USER2, PASSWORD2, HOST2, PORT2, query2)

    if result1 and result2:
        plan1 = result1[0][0][0]["Plan"]
        plan2 = result2[0][0][0]["Plan"]

        # Calculate Tree-Edit Distance
        ted = compare(plan1, plan2)
        
        # Node-wise Comparison
        node_comparison = node_wise_comparison(plan1, plan2)
        
        separator = "/"
        if platform.system() == "Windows":
            separator = "\\"
        qq = query_file1.split(separator)
        # Visualize Combined Plans with Networkx
        visualize_plan_with_networkx(plan1, plan2, qq[-1])
        
        # Output the results
        output = {
            "Tree-Edit Distance": ted,
            "Node-wise Comparison": node_comparison
        }
        
        print(json.dumps(output, indent=4))
    else:
        print("Failed to obtain EXPLAIN results for one or both queries.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: tree_edit_distance_tool.py <query_file1> <query_file2>")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2])
