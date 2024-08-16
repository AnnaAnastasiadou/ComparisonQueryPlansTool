import subprocess
import os
import json
import platform
import matplotlib.pyplot as plt
import numpy as np

def compare_queries_in_directories(directory1, directory2, plot=False, analyze=False, store=False):
    """
    Compare queries in two directories and generate comparison results. 
    When analyze is true the queries are executed multiple times and the average time difference is calculated.

    Args:
        directory1 (str): Path to the first directory containing query files.
        directory2 (str): Path to the second directory containing query files.
        plot (bool, optional): Whether to plot the comparison results. Defaults to False.
        analyze (bool, optional): Whether to use explain analyze. Defaults to False.
        store (bool, optional): Whether to store the comparison results in a file. Defaults to False.

    Returns:
        None

    Note: Make sure that nothing else is printed in the terminal other than the results.
        .i.e. Do not print any debug statements or print statements in the tree_edit_distance_tool.py script,
        the tree_edit_distance.py script, or the tree_visualisation.py script.
        The only print statement that should be present is print(json.dumps(json_output)) in the tree_edit_distance_tool.py script.

    """
    # Get the list of files in each directory
    files1 = set(os.listdir(directory1))
    files2 = set(os.listdir(directory2))
    time_differences = []

    # Filter only .sql files and find common files in both directories
    sql_files1 = {file for file in files1 if file.endswith('.sql')}
    sql_files2 = {file for file in files2 if file.endswith('.sql')}
    common_files = sql_files1.intersection(sql_files2)

    # # List of file numbers to skip
    skip_file_numbers = {1,11,74,4}


    # Construct the set of filenames to skip in the TPC-DS queries
    skip_files = {f"query{num}.sql" for num in skip_file_numbers}

    # Remove the skip files from the common files set
    common_files -= skip_files

    results = []
    num_runs = 3 if analyze else 1  # Number of runs for analysis
    
    #print the files that are going to be compared
    print(common_files)

    # Iterate through each common SQL file and compare them
    for file in common_files:
        print(f"Executing query {file}")
        file_path1 = os.path.join(directory1, file)
        file_path2 = os.path.join(directory2, file)
        time_differences = []

        for run in range(num_runs):
            print(f"Run: {run}")
            command = ["python3", "tree_edit_distance_tool.py", file_path1, file_path2]
            if analyze:
                command.append("--analyze")

            # Execute the command and capture the output
            res = subprocess.run(command, capture_output=True, text=True)
            
            if res.stderr:
                print(f"Error found in query {file}: {res.stderr}")
            else:
                tpl = json.loads(res.stdout)
                if analyze and run >= 0 and 'time_difference' in tpl:
                    time_differences.append(tpl['time_difference'])
        
        # Extract and store the results
        query = tpl.get('query1', 'Unknown Query').split(os.sep)[-1]
        comparison_result = tpl.get('comparison_result', 'Unknown')
        
        # Append the results depending on whether the --analyze flag was used
        if analyze and time_differences:
            average_time_difference = sum(time_differences) / len(time_differences)
            results.append([query, comparison_result, average_time_difference])
        else:
            results.append([query, comparison_result])

        # Store the results if the flag --store was given
        if store: 
            output_file = f"comparison_result_avg_{directory1.split('/')[1]}.json"
            with open(output_file, 'w') as file:
                json.dump(results, file)
                print(f"Results stored in {output_file}")

    for result in results:
        print(result)

    # Generate plots if the --plot flag was given
    if plot:
        plot_explain_results(results, directory1.split('/')[1])

    # if analyze and plot are true, plot the analyze results too
    if plot and analyze:
        plot_explain_analyze_results(results, directory1.split('/')[1])
    
def plot_explain_results(results, directory):
    """
    Generates and saves a histogram of Tree Edit Distance values from the results.
    
    Parameters:
    - results (list): The list of results containing Tree Edit Distance values.
    - directory (str): The directory name used in the plot title and file name.
    
    Returns:
    - None
    """
    print("Plotting histogram...")
    # Extract queries and ted values
    queries = [result[0] for result in results]
    comparison_values = [result[1] for result in results]

    # Create a histogram of the ted values
    plt.figure(figsize=(10, 6))
    plt.hist(comparison_values, bins=np.arange(min(comparison_values), max(comparison_values) + 2) - 0.5, color='steelblue', edgecolor='black', align='mid')

    plt.xlabel('Tree Edit Distance')
    plt.ylabel('No. of Queries')
    plt.title(f"Tree Edit Distance Value Frequency of Queries in {directory}")
    plt.xticks(rotation=90)
    plt.tight_layout()

    # Save the plot as an image file
    plt.savefig(f"comparison_results_histogram_avg_{directory}.png")
    print(f"Plot saved as comparison_results_histogram_avg_{directory}.png")

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
    time_differences = [result[2] for result in results if len(result) > 2]

    # Create a scatter plot of ted values vs. time differences
    plt.figure(figsize=(10, 6))
    plt.plot(comparison_values, time_differences, 'o', color='blue')
    plt.xlabel('Tree Edit Distance')
    plt.ylabel('Average Execution Time Difference (ms)')
    plt.title(f"Correlation of Tree Edit Distance and Execution Time Difference for Queries in {directory}")
    plt.xticks(rotation=90)
    plt.tight_layout()

    # Save the plot as an image file
    plt.savefig(f'comparison_analyze_results_avg_{directory}.png')
    print(f"Plot saved as comparison_analyze_results_avg_{directory}.png")
    
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

    # Compare queries in the given directories
    compare_queries_in_directories(directory1, directory2, plot, analyze, store)
