#Runs all JOB queries. 
#When the analyze flag is given it runs each query 3 times and takes their average execution time. 
#Adjust the flags as necessary.
python3 run_queries_avg.py ../JOB/queries ../JOB/queries --plot --store --analyze
