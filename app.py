from io import StringIO

from flask import Flask, render_template, request, jsonify

from abstract_compiler.exceptions import CompilationError
from dict_compiler import DictCompiler

app = Flask(__name__)
app.config.from_object(__name__)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/api/compile", methods=["POST"])
def compile_statement():
    statement = request.get_json().get("statement")
    if not statement:
        return "No statement provided", 400
    if (
        not isinstance(statement, list) or
        not all(isinstance(i, str) for i in statement)
    ):
        return "Invalid statement format (expected: string[])", 400

    compiler = DictCompiler()
    statement_stream = StringIO("\n".join(statement))
    try:
        results = compiler.execute(statement_stream)
        str_results = compiler.results_to_str(results)
        return jsonify({"status": "success", "results": str_results})
    except CompilationError as e:
        return jsonify({
            "status": "error",
            "error": {
                "message": f"{e}",
                "location": {
                    "from": {
                        "line": e.location.line_start,
                        "ch": e.location.column_start,
                    },
                    "to": {
                        "line": e.location.line_end,
                        "ch": e.location.column_end,
                    },
                }
            }
        })


@app.route("/api/quotation_mark_suggestions", methods=["POST"])
def get_quotation_mark_suggestions():
    args = request.get_json()
    statement = args.get("statement")
    if not statement:
        return "No statement provided", 400
    if (
        not isinstance(statement, list) or
        not all(isinstance(i, str) for i in statement)
    ):
        return "Invalid statement format (expected: string[])", 400
    cursor_line = args.get("cursor_line")
    cursor_column = args.get("cursor_column")
    if cursor_line is None or cursor_column is None:
        return (
            "No cursor position provided "
            "(expected: cursor_line, cursor_column)",
            400
        )
    previous_statement = statement[:cursor_line + 1]
    previous_statement[-1] = previous_statement[-1][:cursor_column-1]
    previous_statement_stream = StringIO("\n".join(previous_statement))
    suggestions = DictCompiler().get_quotation_mark_suggestions(
        previous_statement_stream
    )
    return jsonify(suggestions)
