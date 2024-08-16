import subprocess
import os
import json
import platform
import matplotlib.pyplot as plt
import numpy as np


def compare_queries_in_directories(directory1, directory2, plot=False, analyze=False, store=False, iterations=3):
    """
    Compare queries with the same name in two directories and calculate the Tree Edit Distance (TED) between them.
    Check if the TED remains the same for the same query on the same database across multiple iterations.
    Optionally, plot and analyze the results, store the results in a file, and check for consistency of the TED of each query on the same database.

    Parameters:
    - directory1 (str): Path to the first directory containing SQL files.
    - directory2 (str): Path to the second directory containing SQL files.
    - plot (bool): Whether to plot the comparison results. Default is False.
    - analyze (bool): Whether to analyze the comparison results. Default is False.
    - store (bool): Whether to store the comparison results in a file. Default is False.
    - iterations (int): Number of iterations to perform the comparison. Default is 3.

    Returns:
    - None

    Note: Make sure that nothing else is printed in the terminal other than the results.
      .i.e. Do not print any debug statements or print statements in the tree_edit_distance_tool.py script,
      the tree_edit_distance.py script, or the tree_visualisation.py script.
      The only print statement that should be present is print(json.dumps(json_output)) in the tree_edit_distance_tool.py script.

    """
    # Get the list of files in each directory
    files1 = set(os.listdir(directory1))
    files2 = set(os.listdir(directory2))

    # Filter only .sql files and find common files in both directories
    sql_files1 = {file for file in files1 if file.endswith('.sql')}
    sql_files2 = {file for file in files2 if file.endswith('.sql')}
    common_files = sql_files1.intersection(sql_files2)

    results = [] # To store the results of comparisons
    consistency_results = [] # To store consistency results for each query

    # Iterate through each common SQL file and compare them
    for file in common_files:
        file_path1 = os.path.join(directory1, file)
        file_path2 = os.path.join(directory2, file)

        comparison_results = [] # To store results for each iteration

        print(f"Comparing {file}")
        # Perform comparisons for the specified number of iterations
        for itr in range(iterations):
            print(f"Iteration: {itr}")
            command = ["python3", "tree_edit_distance_tool.py", file_path1, file_path2]
            if analyze:
                command.append("--analyze")
            
            # Execute the comparison command
            res = subprocess.run(command, capture_output=True, text=True)
            
            if res.stderr:
                print(f"Error found in query {file.split('/')[-1]} {res.stderr}")
            else:
                tpl = json.loads(res.stdout)
                separator = "/"
                if platform.system() == "Windows":
                    separator = "\\"
                query = tpl['query1'].split(separator)[-1]

                # Append the results depending on whether the --analyze flag was used
                if analyze:
                    results.append([query, tpl['comparison_result'], tpl['time_difference']])
                else:
                    results.append([query, tpl['comparison_result']])
                
                comparison_results.append(tpl['comparison_result'])

        # Check if comparison results are consistent across iterations
        is_consistent = all(result == comparison_results[0] for result in comparison_results)
        consistency_results.append([query, is_consistent])

    # Store the results in a JSON file if the --store flag is given
    if store: 
        output_file = f"comparison_result_{directory1.split('/')[1]}.json"
        with open(output_file, 'w') as file:
            json.dump(results, file)
            print(f"Results stored in {output_file}")
    
    # Generate plots if the --plot flag is given
    if plot:
        plot_explain_results(results, directory1.split('/')[1])

    # If analyze and plot are true, plot the analyze results too
    if plot and analyze:
        plot_explain_analyze_results(results, directory1.split('/')[1])
    
    # Print the results
    for result in results:
        print(result)
    
    # Print the consistency results
    print("\nConsistency Results:")
    for result in consistency_results:
        print(result)

def plot_explain_results(results, directory):
    """
    Generates and saves a histogram of Tree Edit Distance values from the results.
    
    Parameters:
    - results (list): The list of results containing Tree Edit Distance values.
    - directory (str): The directory name used in the plot title and file name.
    
    Returns:
    - None
    """
    print("plotting histogram...")
    # Extract queries and ted values
    queries = [result[0] for result in results]
    comparison_values = [result[1] for result in results]

    # Create a histogram of the ted values
    plt.figure(figsize=(10, 6))
    plt.hist(comparison_values, bins=np.arange(min(comparison_values), max(comparison_values) + 2) - 0.5, color='steelblue', edgecolor='black', align='mid')

    plt.xlabel('Tree Edit Distance')
    plt.ylabel('No. of Queries')
    plt.title(f"Comparison Results of Queries in {directory}")
    plt.xticks(rotation=90)
    plt.tight_layout()

    # Save the plot as an image file
    plt.savefig(f"comparison_results_histogram_{directory}.png")
    print(f"Plot saved as comparison_results_histogram_{directory}.png")

    plt.show()


def plot_explain_analyze_results(results, directory):
    """
    Generates and saves a scatter plot showing the correlation between Tree Edit Distance and execution time difference.
    
    Parameters:
    - results (list): The list of results containing Tree Edit Distance values and time differences.
    - directory (str): The directory name used in the plot title and file name.
    
    Returns:
    - None
    """
    print("Plotting analyze results...")

    # Extract queries, ted values and time differences
    queries = [result[0] for result in results]
    comparison_values = [result[1] for result in results]
    time_differences = [result[2] for result in results]
    querynames = [query.split('/')[-1] for query in queries]

    # Create a scatter plot of ted values vs. time differences
    plt.figure(figsize=(10, 6))
    plt.plot(comparison_values, time_differences, 'o', color='blue')
    plt.xlabel('Tree Edit Distance')
    plt.ylabel('Execution Time Difference')
    plt.title(f"Correlation of Tree Edit Distance and Execution Time Difference for Queries in {directory}")
    plt.xticks(rotation=90)
    plt.tight_layout()

    # plt.legend(querynames, loc='center left', bbox_to_anchor=(1, 0.5))
    # Save the plot as an image file
    plt.savefig(f'comparison_analyze_results_{directory}.png')
    print(f"Plot saved as comparison_analyze_results_{directory}.png")
    
    plt.show()

if __name__ == "__main__":
    import sys
    # Check if the script is being run with the correct number of arguments
    if len(sys.argv) < 3:
        print("Usage: python compare_queries_in_directories.py <directory1> <directory2>")
        sys.exit(1)
    
    directory1 = sys.argv[1]
    directory2 = sys.argv[2]
    plot = '--plot' in sys.argv
    analyze = '--analyze' in sys.argv
    store = '--store' in sys.argv
    iterations = 3
    if '--iterations' in sys.argv:
        iterations_index = sys.argv.index('--iterations') + 1
        if iterations_index < len(sys.argv):
            iterations = int(sys.argv[iterations_index])

    # Compare queries in the given directories
    compare_queries_in_directories(directory1, directory2, plot, analyze, store, iterations)
