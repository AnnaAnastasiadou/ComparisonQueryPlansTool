#runs the given TPC-DS query, using the tool and returns the TED value. Adjust the flags as necessary.
read -p "Testing query:" i
python3 tree_edit_distance_tool.py ../tpcds/updated_queries/query$i.sql ../tpcds/updated_queries/query$i.sql --store --plot

