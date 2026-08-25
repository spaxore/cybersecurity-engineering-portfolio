import os

from flask import Flask, jsonify

app = Flask(__name__)


@app.get("/")
def home():
    return jsonify(
        service="supply-chain-demo",
        status="ok",
        message="This application is protected by the Project 08 delivery pipeline.",
    )


@app.get("/healthz")
def healthz():
    return jsonify(status="healthy")


if __name__ == "__main__":
    host = os.environ.get("APP_HOST", "0.0.0.0")
    port = int(os.environ.get("APP_PORT", "8080"))
    app.run(host=host, port=port, debug=False)
