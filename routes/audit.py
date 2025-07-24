from flask import Blueprint, request, jsonify
from services.audit import run_audit

audit_blueprint = Blueprint("audit", __name__)

@audit_blueprint.route("/api/audit", methods=["POST"])
def audit():
    data = request.json
    url = data.get("url")
    results = run_audit(url)
    return jsonify(results)