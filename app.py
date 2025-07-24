from flask import Flask, render_template, request, jsonify
from routes.audit import audit_blueprint

app = Flask(__name__, static_folder="../frontend/static", template_folder="../frontend/templates")
app.register_blueprint(audit_blueprint)

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)