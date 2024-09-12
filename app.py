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
    compiler = DictCompiler()
    try:
        results = compiler.execute(statement)
        str_results = compiler.results_to_str(results)
        return jsonify({"status": "success", "results": str_results})
    except CompilationError as e:
        return jsonify({"status": "error", "error": f"{e}"})
