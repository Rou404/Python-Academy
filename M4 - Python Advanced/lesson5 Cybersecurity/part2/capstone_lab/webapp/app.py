from flask import Flask, request, jsonify, send_from_directory
app = Flask(__name__)
BANNER = "SimpleDemo/0.1"
FLAG = "FLAG{web}"
@app.after_request
def add_headers(resp):
    resp.headers["Server"] = BANNER
    return resp
@app.route("/")
def index():
    return """<h1>Welcome</h1>
<p>This is a demo app. Nothing to see here.</p>
<p>Try exploring <code>/static/</code> or guessing common admin paths.</p>"""
@app.route("/note")
def note():
    nid = request.args.get("id","1")
    if nid == "0":
        return jsonify({"id":0, "owner":"admin", "note": FLAG})
    return jsonify({"id":1, "owner":"guest", "note":"Keep looking."})
@app.route("/static/<path:p>")
def static_files(p):
    return send_from_directory(".", p)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
