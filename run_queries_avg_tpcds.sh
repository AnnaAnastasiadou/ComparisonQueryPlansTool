#Runs all TPC-DS queries. 
#When the analyze flag is given it runs each query 3 times and takes their average execution time. 
#Adjust the flags as necessary.
python3 run_queries_avg.py ../tpcds/updated_queries/ ../tpcds/updated_queries/ --plot --store --analyze
