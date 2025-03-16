"""Simple Flask application for debugging."""

import os
import json
from flask import Flask

# Create a simple Flask app for debugging
app = Flask(__name__)


@app.route("/")
def home():
    return "Hello from Vercel Flask app!"


@app.route("/vercel-test")
def vercel_test():
    return "Hello from Vercel serverless function!"


@app.route("/debug-env")
def debug_env():
    env_vars = {k: v for k, v in os.environ.items()}
    return json.dumps(env_vars, indent=2)


# This is important for Vercel deployment
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
