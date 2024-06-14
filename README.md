# Abstract QL Compiler  

This project is a compiler of a simple query language that could be applied to
any kind of data structure. It intends to make query languages more 
approachable for complex data structures. It takes as input a string statement, 
and applies it to the data structure.

## Getting Started

This project is written in python ([download](https://www.python.org/downloads/)). 
The required python modules are listed in the requirements.txt file. 
To install them all, open a terminal in the root of the project, 
then execute the following command :
```
pip install -r requirements.txt
```
It is then possible to execute statements in the example compiler 
[DictCompiler](dict_compiler/compiler.py), which relies on the data structure 
defined in the file [dict_compiler/data.json](dict_compiler/data.json). 
To execute a statement, use the following command:
```
python main.py [-h] [--verbose] statement
```
Example:
```
python main.py 'SELECT "column2" FROM "schema1"."table1"' --verbose
```

## How it works   

Standard compilers contain the following elements:
1. Lexical analyzer (or lexer): breaks the code into tokens
2. Parser (or syntax analyzer): builds a syntax tree from the tokens according to a grammar
3. Semantic analyzer: verifies that the syntax tree complies to the language and the data sructure
4. Code generation: generate code from the verified syntax tree

The abstract compiler is made of a [lexer](abstract_compiler/lexer.py) and a 
[parser](abstract_compiler/parser.py). As semantic analysis and code generation
depend on the data structure at use, it has to be specifically defined for each
one. To do so, the abstract methods of the generic class 
[AbstractCompiler](abstract_compiler/compiler.py) has to be overridden. The class 
[DictCompiler](dict_compiler/compiler.py) is an example of that implementation.

### Example
```
STATEMENT

SELECT "column1" "column2" FROM "schema1"."table1"

TOKENS

<SELECT> <ID, "column1"> <ID, "column2"> <FROM> <ID, "schema1"> <DOT> <ID, "table1">

SYNTAX TREE

SELECT
├── <SELECT>
│   ├── <ID, "column1">
│   └── <ID, "column2">
└── <FROM>
    └── TABLE IDENTIFIER
        ├── <ID, "schema1">
        ├── <DOT>
        └── <ID, "table1">

RESULTS

[{'column1': 1, 'column2': 2}, {'column1': 2, 'column2': 1}]
```

## Language definition

The language is organized in statements, and can only process one statement 
at a time. Statements are made of clauses, and clauses take parameters. 
Language words are all case-insensitive, and can either be written in upper,
lower or mixed case.

### Statements
#### Select

Example: `SELECT "column1" "column2" FROM "schema1"."table1"`
Clauses:
- SELECT: list of column ids (depth 1)
- FROM: id of a table (depth 1, 2 or 3)

### Token table

| Token  | Regular expression       |
|--------|--------------------------|
| SELECT | case_insensitive(SELECT) |
| FROM   | case_insensitive(FROM)   |
| ID     | "[^"]\*"                 |
| DOT    | \\.                      |

### Grammar
```
statement           ::= select_statement
select_statement    ::= <SELECT> column_list <FROM> table 
column_list         ::= <ID> column_list | <ID>
table               ::= <ID> | <ID> <DOT> <ID> | <ID> <DOT> <ID> <DOT> <ID>
```

