from flask import Flask, render_template, request, jsonify
from routes.audit import audit_blueprint

app = Flask(__name__, static_folder="static", template_folder="templates")
app.register_blueprint(audit_blueprint)

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
