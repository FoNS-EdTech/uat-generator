# app.py
from flask import Flask, render_template, request, send_file
import io
import csv
from uat_core.ingestion import fetch_web_docs#, fetch_pdf_docs
from uat_core.extraction import extract_actions_from_docs
from uat_core.uat_builder import build_uats_from_actions

app = Flask(__name__)

# In-memory storage for prototype
LAST_UATS = []

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    global LAST_UATS
    source_type = request.form.get("source_type")

    docs = []
    if source_type == "web":
        base_url = request.form.get("base_url", "").strip()
        if base_url:
            docs = fetch_web_docs(base_url)
    elif source_type == "pdf":
        uploaded_files = request.files.getlist("pdf_files")
        file_paths = []
        for f in uploaded_files:
            if f.filename:
                path = f"./tmp_{f.filename}"
                f.save(path)
                file_paths.append(path)
        docs = fetch_pdf_docs(file_paths)

    actions = extract_actions_from_docs(docs)
    uats = build_uats_from_actions(actions)
    LAST_UATS = uats

    return render_template("results.html", uats=uats)

@app.route("/download_csv", methods=["GET"])
def download_csv():
    global LAST_UATS
    if not LAST_UATS:
        return "No UATs generated yet.", 400

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Test Case ID", "Role", "Test Case", "Test Case Description",
                     "Steps to execute", "Expected Result(s)", "Acceptance Criteria"])

    for u in LAST_UATS:
        writer.writerow([
            u.test_case_id,
            u.role,
            u.test_case,
            u.test_case_description,
            " | ".join(u.steps_to_execute),
            " | ".join(u.expected_results),
            " | ".join(u.acceptance_criteria),
        ])

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode("utf-8")),
        mimetype="text/csv",
        as_attachment=True,
        download_name="uat_export.csv"
    )

if __name__ == "__main__":
    app.run(debug=True)