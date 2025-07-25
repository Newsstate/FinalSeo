from flask import Flask, render_template, request
from seo_analyzer import extract_seo_data

app = Flask(__name__, static_folder="static", template_folder="templates")

@app.route("/", methods=["GET"])
def index():
    url = request.args.get("url", "")
    seo_result = extract_seo_data(url) if url else None
    return render_template("index.html", result=seo_result, url=url)

if __name__ == "__main__":
    app.run(debug=True)
