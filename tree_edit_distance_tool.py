import psycopg2
import os
import sys
import json
import networkx as nx
import matplotlib.pyplot as plt
from tree_edit_distance import main as compare
from tree_visualisation import plot_trees

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
        comparison_result, tree1_json, tree2_json, edit_mapping = compare(result1[0][0][0], result2[0][0][0])
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
            plot_trees(tree1_json, tree2_json, edit_mapping,f"execution_plans_{filename1}_{filename2}.png")
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