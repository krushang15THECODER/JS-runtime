from flask import Flask, render_template, request, jsonify
from main import run_javascript
import io
import contextlib

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/run", methods=["POST"])
def run_code():
    data = request.json
    js_code = data.get("code", "")

    output_buffer = io.StringIO()

    try:
        with contextlib.redirect_stdout(output_buffer):
            run_javascript(js_code)

        result = output_buffer.getvalue()

        return jsonify({
            "success": True,
            "output": result
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "output": str(e)
        })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)