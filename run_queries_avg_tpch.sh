#Runs all TPC-H queries. 
#When the analyze flag is given it runs each query 3 times and takes their average execution time. 
#Adjust the flags as necessary.
python3 run_queries_avg.py ../TPC-H/TPC-H\ V3.0.1/dbgen/queries_marked ../TPC-H/TPC-H\ V3.0.1/dbgen/queries_marked --plot --store --analyze
