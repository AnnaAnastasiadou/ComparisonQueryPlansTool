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

    # Filter only .sql files and find common files in both directories
    sql_files1 = {file for file in files1 if file.endswith('.sql')}
    sql_files2 = {file for file in files2 if file.endswith('.sql')}
    common_files = sql_files1.intersection(sql_files2)

    # print(directory1.split('/')[1])

    results = []
    print(common_files)
    for file in common_files:
        file_path1 = os.path.join(directory1, file)
        file_path2 = os.path.join(directory2, file)
        # print(file_path1)
        # print(f"Comparing {file}")
        # print(f"[Running]: python3 tree_edit_distance_tool.py {file_path1} {file_path2}")
        command = ["python3", "tree_edit_distance_tool.py", file_path1, file_path2]
        print(f"Executing {file}")
        if analyze:
            command.append("--analyze")
        
        res = subprocess.run(command, capture_output=True, text=True)
        
        if res.stderr:
            print(f"Error found in query {file.split('/')[-1]} {res.stderr}")
        else:
            # print("Output ",res.stdout)
            tpl = json.loads(res.stdout)
            separator = "/"
            if platform.system() == "Windows":
                separator = "\\"
            query = tpl['query1'].split(separator)[-1]
            if analyze:
                results.append([query,tpl['comparison_result'],tpl['time_difference']])
            else:
                results.append([query,tpl['comparison_result']])
    if store: 
        output_file = f"comparison_result_{directory1.split('/')[1]}.json"
        with open(output_file, 'w') as file:
            json.dump(results, file)
            print(f"Results stored in {output_file}")

    if plot:
        plot_explain_results(results,directory1.split('/')[1])

    if plot and analyze:
        plot_explain_analyze_results(results,directory1.split('/')[1])
    
    for result in results:
        print(result)

def plot_explain_results(results,directory):
    print("plotting results...")
    queries = [result[0] for result in results]
    comparison_values = [result[1] for result in results]

    plt.figure(figsize=(10, 6))
    # plt.bar(queries, comparison_values, color='blue')
    #plt.hist(comparison_values, bins=10, color='steelblue', edgecolor='black')
    plt.hist(comparison_values, bins=np.arange(min(comparison_values), max(comparison_values) + 2) - 0.5, color='steelblue', edgecolor='black', align='mid')
    # plt.figure(figsize=(10, 6))
    #plt.bar(comparison_values, width=0.8, align='center', alpha=0.7, edgecolor='black')

    plt.xlabel('Tree Edit Distance')
    plt.ylabel('No. of Queries')
    plt.title(f"Tree Edit Distance Value Frequency of Queries in {directory}")
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig(f"comparison_results_histogram_{directory}.png")
    plt.show()
    print(f"Plot saved as comparison_results_histogram_{directory}.png")

def plot_explain_analyze_results(results,directory):
    print("plot2")
    queries = [result[0] for result in results]
    comparison_values = [result[1] for result in results]
    time_differences = [result[2] for result in results]
    querynames = [query.split('/')[-1] for query in queries]
    plt.figure(figsize=(10, 6))
    plt.plot(comparison_values, time_differences, 'o', color='blue')
    plt.xlabel('Tree Edit Distance')
    plt.ylabel('Execution Time Difference')
    plt.title(f"Correlation of Tree Edit Distance and Execution Time Difference for Queries in {directory}")
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig(f'comparison_analyze_results_{directory}.png')
    plt.legend(querynames, loc='center left', bbox_to_anchor=(1, 0.5))  # Add querynames to the legend
    plt.show()
    print(f"Plot saved as comparison_analyze_results_{directory}.png")


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