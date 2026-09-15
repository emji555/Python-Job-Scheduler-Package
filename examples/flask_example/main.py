"""Minimal Flask example."""

from flask import Flask, jsonify

from workloom import job
from workloom.integrations.flask import init_app

flask_app = Flask(__name__)
package_app = init_app(flask_app, backend="eager")


@job
def ping(name: str) -> str:
    return f"pong:{name}"


@flask_app.get("/ping/<name>")
def ping_route(name: str):
    return jsonify({"result": ping.dispatch(name).result()})
