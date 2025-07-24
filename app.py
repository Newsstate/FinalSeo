from flask import Flask, render_template, request, jsonify
from routes.audit import audit_blueprint
from seo_analyzer import extract_seo_data

app = Flask(__name__, static_folder="static", template_folder="templates")
app.register_blueprint(audit_blueprint)


@app.route('/dashboard')
def dashboard():
    url = request.args.get("url", "")
    seo_result = extract_seo_data(url) if url else None
    return render_template("seo_dashboard.html", result=seo_result, url=url)
    
@app.route("/")
def home():
    return render_template("index.html")
@app.route("/api/scan", methods=["POST"])
def scan():
    data = request.get_json()
    url = data.get("url")
    if not url:
        return jsonify({"error": "Missing URL"}), 400
    result = extract_seo_data(url)
    return jsonify(result)
    
if __name__ == "__main__":
    app.run(debug=True)
