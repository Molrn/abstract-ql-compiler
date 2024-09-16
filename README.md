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

### Flask
To start the flask application, use the command:  
```
flask run
```

### Command Line Interface
To use the CLI, you have to create a file containing the statement to execute. 
Statement examples can be found in the 
[dict_compiler/statements/](dict_compiler/statements/) directory.
Then, execute the following command:
```
python main.py [-h] [--verbose] statement_file
```
Example:
```
python main.py dict_compiler/statements/simple.txt --verbose
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

SELECT "column1" FROM "table1"

TOKENS

<SELECT, SELECT, [(1,1),(1,7)]> <ID, "column1", [(1,8),(1,17)]> <FROM, FROM, [(1,18),(1,22)]> <ID, "table1", [(1,23),(1,31)]>

SYNTAX TREE

SELECT STATEMENT
├── SELECT
│   ├── <SELECT, SELECT, [(1,1),(1,7)]>
│   └── COLUMN LIST
│       └── COLUMN
│           └── <ID, "column1", [(1,8),(1,17)]>
└── FROM
    ├── <FROM, FROM, [(1,18),(1,22)]>
    └── TABLE
        └── <ID, "table1", [(1,23),(1,31)]>

RESULTS

[
    {
        "column1": 1
    },
    {
        "column1": 2
    }
]
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
