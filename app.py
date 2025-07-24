from flask import Flask, render_template, request, jsonify, redirect, url_for
from routes.audit import audit_blueprint
from seo_analyzer import extract_seo_data

app = Flask(__name__, static_folder="static", template_folder="templates")
app.register_blueprint(audit_blueprint)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url")
        if not url:
            return render_template("index.html", error="Please enter a URL.")
        result = extract_seo_data(url)
        return render_template("index.html", result=result, url=url)
    return render_template("index.html", result=None)

@app.route("/api/scan", methods=["POST"])
def api_scan():
    data = request.get_json()
    url = data.get("url")
    if not url:
        return jsonify({"error": "Missing URL"}), 400
    result = extract_seo_data(url)
    return jsonify(result)

@app.route("/dashboard")
def dashboard():  # Optional route if you want a separate dashboard view
    url = request.args.get("url", "")
    seo_result = extract_seo_data(url) if url else None
    return render_template("seo_dashboard.html", result=seo_result, url=url)

if __name__ == "__main__":
    app.run(debug=True)
