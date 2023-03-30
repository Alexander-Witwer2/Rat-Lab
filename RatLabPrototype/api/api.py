import flask
from search import search

app = flask.Flask(__name__)
app.config["DEBUG"] = False
app.register_blueprint(search)

@app.route("/api/version")
def version():
    return "1.0"

app.run(port=8080)