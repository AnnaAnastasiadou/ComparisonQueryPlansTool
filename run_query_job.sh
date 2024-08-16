#runs the given JOB query, using the tool and returns the TED value. Adjust the flags as necessary.
read -p "Testing query:" i
python3 tree_edit_distance_tool.py ../JOB/queries/$i.sql ../JOB/queries/$i.sql  --plot --store --debug --analyze
