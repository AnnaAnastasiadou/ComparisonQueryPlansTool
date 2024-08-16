# Tree Edit Distance Tool

## Overview
This tool provides a set of Python scripts designed to calculate the tree edit distance between the execution plans of two SQL queries in PostgreSQL. The tool also offers the option to visualize these execution plans side-by-side, highlighting their similarities and differenes. These functionalities are all available to use through a command-line interface.

## Main Components

### 1. `tree_edit_distance.py`
This script contains the core algorithms for calculating the tree edit distance. It defines the functions necessary to measure the minimum number of operations required to transform one tree structure into another. It also contains the transformation of the execution plans into tree structures.

### 2. `tree_edit_distance_tool.py`
This script acts as the command-line interface for the tool. It allows users to input two SQL query files and outputs the calculated tree edit distance, utilizing functions from `tree_edit_distance.py`.

### 3. `tree_visualisation.py`
This script provides the functionality to visualize the execution plans graphically. It helps in understanding the tree structures and the similarities and differences between them.

## Installation

To use this tool, you need Python installed on your system. Clone or download this repository to your local machine, and ensure you have the necessary Python libraries installed:

```bash
pip install -r requirements.txt
```

## Configuration

Create a `config.json` file in the root directory of the project. The configuration file should be in the following format:

```json
{
    "DB1": {
        "DATABASE": "database1",
        "USER": "user1",
        "PASSWORD": "password1",
        "HOST": "host1",
        "PORT": "port1"
    },
    "DB2": {
        "DATABASE": "database2",
        "USER": "user2",
        "PASSWORD": "password2",
        "HOST": "host2",
        "PORT": "port2"
    }
}
```

Make sure to replace the values with your actual database credentials. You can use the same database twice if the queries you want to compare will be executed on the same database.


## Usage 
Execute the tool via command line by navigating to the tool's directory and running:

```bash
    python tree_edit_distance_tool.py /path/to/query1.sql /path/to/query2.sql
```

The tool will output the tree edit distance comparison in JSON format in the terminal. For example if you run the above line it would result in:

```sh
Output  {"query1": "/path/to/query1.sql", "/path/to/query2": "../JOB/queries/24b.sql", "TED": ted_number}
```

## Command-Line Options

This tool supports several command-line flags to enhance its functionality:

### `--analyze`
- **Description**: Executes the query with the EXPLAIN ANALYZE command of PostgreSQL and provides the execution times of the queries and the difference between them.

### `--debug`
- **Description**: Activates debug mode, which provides detailed logs of the computation steps, helping in troubleshooting or understanding the process flow.

### `--plot`
- **Description**: Generates and displays a graphical representation of the execution plans side-by-side in a tree structure. Nodes that appear in both trees are green and the rest are red. 

### `--store`
- **Description**: Enables the storage of results and plots into separate files for later retrieval or analysis.


## Examples

To run the tool with visualization and store information and plots locally:

```bash
python tree_edit_distance_tool.py --plot --store
```

## Additional Tools and Scripts

The following files are included in the folder and are mostly used for specific testing and analysis purposes related to my dissertation. These are not generally required for the basic operation of the tree edit distance tool, but they were useful for detailed analysis and batch processesing:

### Script Descriptions

- **`run_query_tpch`**, **`run_query_tpcds`**, **`run_query_job`**: Shell scripts that call **`tree_edit_distance_tool`** for the specified query in TPC-H, TPC-DS and JOB, assuming that you have the queries saved in local directories.

- **`run_queries_avg.py`**: Compares all common SQL queries in the two directories that are given as arguments similarly to the tool. Executes each query multiple times and calculates the average execution time if the `--analyze` flag is used. Otherwise all queries are only executed once. When the `--analyze` flag is enabled, EXPLAIN ANALYZE is used. When the `--plot` flag is used, a histogram with the frequency of the TED values across the specific benchmark is plotted. When the `--plot` and `--analyze` flags are used together an additional graph is plotted, which shows the execution time differences against the relative TED value. The `--store` flag is used when you want to store the EXPLAIN (ANALYZE) results and the plots in separate files.

- **`run_queries_avg_tpch.sh`**, **`run_queries_avg_tpcds.sh`**, **`run_queries_avg_job.sh`**: Shell scripts that call **`run_queries_avg.py`** and run all TPC-H, TPC-DS and JOB queries, assuming that you have the queries saved in local directories.

- **`run_queries.py`**: Similar to **`run_queries_avg.py`**, but each query is executed only once.

- **`run_queries_avg_tpch.sh`**, **`run_queries_avg_tpcds.sh`**, **`run_queries_avg_job.sh`**: Shell scripts that call **`run_queries.py`** and run all TPC-H, TPC-DS and JOB queries similar to **`run_queries_avg_tpch.sh`**, **`run_queries_avg_tpcds.sh`** and **`run_queries_avg_job.sh`**.

- **`data_plot_avg`**: Contains data after running all queries in the three benchmarks using **`run_queries_avg.py`**. This data is plotted, along with the best linear fit and excluding the outliers (points over 2 std).



## License

This project is licensed under the MIT License.
