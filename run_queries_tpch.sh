#Runs all TPC-H queries once, using the tool and returns the TED value. Adjust the flags as necessary.
python3 run_queries.py ../TPC-H/TPC-H\ V3.0.1/dbgen/queries_marked ../TPC-H/TPC-H\ V3.0.1/dbgen/queries_marked --plot --store --analyze
