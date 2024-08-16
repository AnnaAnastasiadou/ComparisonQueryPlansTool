import psycopg2
import os
import sys
import json
import networkx as nx
import matplotlib.pyplot as plt
from tree_edit_distance import main as compare
from tree_visualisation import plot_trees


def preprocess_query(query, analyze=False, debug=False):
    """
    Prepares the SQL query for execution by adding the EXPLAIN (ANALYZE) command if needed.

    Parameters:
    - query (str): The SQL query to be preprocessed.
    - analyze (bool): If True, use EXPLAIN ANALYZE; otherwise use EXPLAIN.
    - debug (bool): If True, print debug information.

    Returns:
    - str: The preprocessed SQL query.
    """

    keywords = ['select', 'insert', 'update', 'delete', 'with']
    if any(query.strip().lower().startswith(stmt) for stmt in keywords):
        explain_type = "EXPLAIN (ANALYZE, FORMAT JSON)" if analyze else "EXPLAIN (FORMAT JSON)" 
        query = f" {explain_type} {query}"
    if debug:
        print(f"Preprocessed query: [{query}]")
    return query


def run_query(database, user, password, host, port, query, analyze=False, debug=False, store=False, output_file=None):
    """
    Connects to the PostgreSQL database, executes the given query, and handles EXPLAIN output.

    Parameters:
    - database (str): Database name.
    - user (str): Database user.
    - password (str): User's password.
    - host (str): Database host.
    - port (str): Database port.
    - query (str): SQL query to execute.
    - analyze (bool): Whether to use EXPLAIN ANALYZE.
    - debug (bool): If True, print debug information.
    - store (bool): If True, store the EXPLAIN output in a file.
    - output_file (str): Path to the output file for storing EXPLAIN results.

    Returns:
    - list: The results of the EXPLAIN query.
    """
    try:
        # Connect to the PostgreSQL database
        connection = psycopg2.connect(
            dbname=database,
            user=user,
            password=password,
            host=host,
            port=port
        )

        cursor = connection.cursor()

        # Split the query if it contains multiple statements
        for q in query.split(";"):
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
                        print(f"EXPLAIN output written to {output_file}")
                    if debug:
                        print(f"EXPLAIN output written to {output_file}")
                return result
            else:
                # Commit changes for non-EXPLAIN queries
                connection.commit()
                if debug:
                    print("Query executed successfully")
    except Exception as error:
        print(f"Error: {error}")
    finally:
        # Close database cursor and connection
        cursor.close()
        connection.close()

def extract_filename(file_path):
    """
    Extracts the filename from a given file path.
    
    Parameters:
    - file_path (str): Path to the file.

    Returns:
    - str: The filename extracted from the path.
    """
    return os.path.basename(file_path)

def main(query_file1, query_file2, plot=False, debug=False, store=False, analyze=False):
    """
    Main function to compare execution plans of two SQL queries.
    
    Parameters:
    - query_file1 (str): Path to the file containing the first SQL query.
    - query_file2 (str): Path to the file containing the second SQL query.
    - plot (bool): If True, generate plots of execution plans.
    - debug (bool): If True, enable debug logging.
    - store (bool): If True, store results and plots in files.
    - analyze (bool): If True, use EXPLAIN ANALYZE instead of EXPLAIN.

    Returns:
    - str: JSON string with the comparison results.
    """
    if debug:
        print(f"Running with options: Plot={plot}, Debug={debug}, Store={store}, Analyze={analyze}")

    # Load database configuration from config.json if available
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
        print("config.json file not found. Please provide database configuration.")
    
    # Read SQL queries from provided files
    with open(query_file1, 'r') as file:
        query1 = file.read().strip()
    
    with open(query_file2, 'r') as file:
        query2 = file.read().strip()

    # Determine output filenames if storing results
    output_file1 = extract_filename(query_file1).replace('.sql', '_explain.json') if store else None
    output_file2 = extract_filename(query_file2).replace('.sql', '_explain.json') if store else None
    if output_file1 == output_file2 and output_file1 is not None:
        output_file2 = output_file1.replace('.json', '_2.json')

    # Execute queries and obtain EXPLAIN results
    result1 = run_query(DATABASE, USER, PASSWORD, HOST, PORT, query1, analyze, debug, store, output_file1)
    result2 = run_query(DATABASE2, USER2, PASSWORD2, HOST2, PORT2, query2, analyze, debug, store, output_file2)
    
    if result1 and result2:
        # Calculate the Tree Edit Distance (comparison_results) between the two execution plans
        comparison_result, tree1_json, tree2_json = compare(result1[0][0][0], result2[0][0][0])

        # Extract filenames
        filename1 = extract_filename(query_file1).replace('.sql', '')
        filename2 = extract_filename(query_file2).replace('.sql', '')

        #plot the execution plans side by side if the --plot flag is given
        if plot:
            print("Plotting the execution plans")
            plot_trees(tree1_json, tree2_json,f"execution_plans_{filename1}_{filename2}.png")

        # Prepare the JSON output with comparison results
        json_output = {
            "query1": query_file1,
            "query2": query_file2,
            "TED": comparison_result
        }

        #if the --analyze flag is given include the execution times in the results
        if analyze:
            # Compute and add execution times and their difference to the output
            actual_time1 = result1[0][0][0]["Execution Time"]
            actual_time2 = result2[0][0][0]["Execution Time"]
            time_difference = abs(actual_time1 - actual_time2)
            json_output["execution_time_1"] = actual_time1
            json_output["execution_time_2"] = actual_time2
            json_output["time_difference"] = time_difference

        #if the --store flag is given the comparison result is stored in a file
        if store:
            output_file = f"comparison_result_{filename1}_{filename2}.json"
            with open(output_file, 'w') as file:
                json.dump(json_output, file)
                print(f"Results stored in {output_file}")
            if debug:
                print(f"Results stored in {output_file}")

        print(json.dumps(json_output))
        return json.dumps(json_output)

    else:
        print("Error: Query execution failed")
        return None
    

if __name__ == "__main__":
    import argparse
    # Argument parsing for command-line execution
    parser = argparse.ArgumentParser(description="Compare execution plans of SQL queries.")
    parser.add_argument("query_file1", help="File containing the first SQL query")
    parser.add_argument("query_file2", help="File containing the second SQL query")
    parser.add_argument("--plot", action="store_true", help="Plot the execution plans")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--store", action="store_true", help="Store the results in a file")
    parser.add_argument("--analyze", action="store_true", help="Use EXPLAIN ANALYZE instead of EXPLAIN")

    args = parser.parse_args()
    main(args.query_file1, args.query_file2, args.plot, args.debug, args.store, args.analyze)