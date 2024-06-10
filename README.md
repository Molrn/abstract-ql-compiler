# Abstact QL Compiler  
This project is a compiler of a simple query language that could be applied to any kind of data structure. It intends to make query languages more approachable for complex data structures.

# Grammar  
```
statement           ::= select_statement
select_statement    ::= <SELECT> column_list <FROM> table 
column_list         ::= column column_list | column
column              ::= <D1 ID>
table               ::= <D1 ID> | <D2 ID> | <D3 ID>
```

