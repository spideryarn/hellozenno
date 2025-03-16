from flask import Flask

app = Flask(__name__)


@app.route("/")
def home():
    return "Hello World from Flask on Vercel! Woohoo"


@app.route("/about")
def about():
    return "About page - this is a simple Flask app running on Vercel!"


# This is important for Vercel deployment
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
