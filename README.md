# Query-Plan-Comparison-TED

This tool compares the execution plans of two SQL queries using the tree edit distance algorithm. The option to compare two queries in two different databases is also available, which is required for comparing the execution plans for base and marked types.

## Prerequisites

- Python 3.x
- PostgreSQL
- Python packages: requirements.txt

## Installation

1. Clone the repository:
    ```sh
    git clone "https://github.com/AnnaAnastasiadou/Query-Plan-Comparison-TED-.git"
    cd <QueryPlanComparison>
    ```

2. Install the required Python packages:
    ```sh
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

## Configuration

Create a `config.json` file in the root directory of the project. The configuration file should be in the following format:

```json
{
    "DB1": {
        "DATABASE": "database1",
        "USER": "postgres",
        "PASSWORD": "password",
        "HOST": "localhost",
        "PORT": "5432"
    },
    "DB2": {
        "DATABASE": "database2",
        "USER": "postgres",
        "PASSWORD": "password",
        "HOST": "localhost",
        "PORT": "5432"
    }
}
```

Make sure to replace the values with your actual database credentials.

##Usage
Run the tool using the following command:
```sh
python3 tree_edit_distance_tool.py /path/to/query1.sql /path/to/query2.sql

```

The tool will output the tree edit distance comparison in JSON format. For example if you run the above line it would result in:

```sh
Output  {"query1": "/path/to/query1.sql", "/path/to/query2": "../JOB/queries/24b.sql", "comparison_result": ted_number}
```

## Optional arguments

* `--plot`: Plot the execution plans using NetworkX and Matplotlib.
* `--debug`: Prints some helpful commands in terminal for debugging
* `--store`: Store results in JSON files.
* `--analyze`: Use `EXPLAIN ANALYZE` instead of explain and get the actual execution times of each plan and their difference.

Example usage with flags:
```sh
python3 tree_edit_distance_tool.py /path/to/query1.sql /path/to/query2.sql --plot --analyze
```

## Optional: Compare Multiple Queries in Directories
You can also compare SQL query files from two directories using the run_queries.py script. This script will find common SQL files in both directories and compare their execution plans.

Run the script using the following command:

 ```sh
 python3 run_queries.py <directory1> <directory2>

 ```

## Code Overview

### Main Script: `tree_edit_distance_tool.py

This script reads the SQL queries from the provided files, runs them against the specified PostgreSQL databases, obtains the execution plans using the 'Explain' command in PostgreSQL, and compares them using the tree edit distance algorithm.

#### Functions

* `preprocess_query(query)`: Prepares the SQL query by adding EXPLAIN (FORMAT JSON) if necessary.

* `run_query(database, user, password, host, port, query)`: Executes the query against the specified PostgreSQL database and returns the execution plan.

* `main(query_file1, query_file2)`: Reads the queries from the files, executes them, and compares the execution plans.

#### Dependencies

* `tree_edit_distance.py`: Contains the logic for comparing two tree structures using the APTED algorithm.

## License

This project is licensed under the MIT License. See the LICENSE file for details.