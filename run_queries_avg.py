import subprocess
import os
import json
import platform
import matplotlib.pyplot as plt
import numpy as np

def compare_queries_in_directories(directory1, directory2, plot=False, analyze=False, store=False):
    # Get the list of files in each directory
    files1 = set(os.listdir(directory1))
    files2 = set(os.listdir(directory2))
    time_differences = []

    # Filter only .sql files and find common files in both directories
    sql_files1 = {file for file in files1 if file.endswith('.sql')}
    sql_files2 = {file for file in files2 if file.endswith('.sql')}
    common_files = sql_files1.intersection(sql_files2)

    results = []
    if analyze:
        num_runs = 4
    else:
        num_runs = 1

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
            
            res = subprocess.run(command, capture_output=True, text=True)
            
            if res.stderr:
                print(f"Error found in query {file}: {res.stderr}")
            else:
                tpl = json.loads(res.stdout)
                if analyze and run > 0 and 'time_difference' in tpl:  # Ignore the first run and check if the key exists
                    time_differences.append(tpl['time_difference'])
        
        query = tpl.get('query1', 'Unknown Query').split(os.sep)[-1]
        comparison_result = tpl.get('comparison_result', 'Unknown')
        
        if analyze and time_differences:
            average_time_difference = sum(time_differences) / len(time_differences)
            results.append([query, comparison_result, average_time_difference])
        else:
            results.append([query, comparison_result])

        if store: 
            output_file = f"comparison_result_avg_{directory1.split('/')[1]}.json"
            with open(output_file, 'w') as file:
                json.dump(results, file)
                print(f"Results stored in {output_file}")

    for result in results:
        print(result)


    if plot:
        plot_explain_results(results, directory1.split('/')[1])

    if plot and analyze:
        plot_explain_analyze_results(results, directory1.split('/')[1])
    

def plot_explain_results(results, directory):
    print("Plotting results...")
    queries = [result[0] for result in results]
    comparison_values = [result[1] for result in results]

    plt.figure(figsize=(10, 6))
    plt.hist(comparison_values, bins=np.arange(min(comparison_values), max(comparison_values) + 2) - 0.5, color='steelblue', edgecolor='black', align='mid')

    plt.xlabel('Tree Edit Distance')
    plt.ylabel('No. of Queries')
    plt.title(f"Tree Edit Distance Value Frequency of Queries in {directory}")
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig(f"comparison_results_histogram_avg_{directory}.png")
    plt.show()
    print(f"Plot saved as comparison_results_histogram__avg_{directory}.png")

def plot_explain_analyze_results(results, directory):
    print("Plotting analyze results...")
    queries = [result[0] for result in results]
    comparison_values = [result[1] for result in results]
    time_differences = [result[2] for result in results if len(result) > 2]

    plt.figure(figsize=(10, 6))
    plt.plot(comparison_values, time_differences, 'o', color='blue')
    plt.xlabel('Tree Edit Distance')
    plt.ylabel('Average Execution Time Difference (ms)')
    plt.title(f"Correlation of Tree Edit Distance and Execution Time Difference for Queries in {directory}")
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig(f'comparison_analyze_results_avg_{directory}.png')
    plt.show()
    print(f"Plot saved as comparison_analyze_results_avg_{directory}.png")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python compare_queries_in_directories.py <directory1> <directory2>")
        sys.exit(1)
    
    directory1 = sys.argv[1]
    directory2 = sys.argv[2]
    plot = '--plot' in sys.argv
    analyze = '--analyze' in sys.argv
    store = '--store' in sys.argv
    compare_queries_in_directories(directory1, directory2, plot, analyze, store)
