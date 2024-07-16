read -p "Testing query:" i
python3 tree_edit_distance_tool.py ../TPC-H/TPC-H\ V3.0.1/dbgen/queries_marked/$i.sql ../TPC-H/TPC-H\ V3.0.1/dbgen/queries_marked/$i.sql --store 
