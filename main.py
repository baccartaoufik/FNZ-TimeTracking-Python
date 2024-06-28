from flask import Flask, send_from_directory

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello World"

@app.route('/static/images/<path:filename>')
def static_files(filename):
    return send_from_directory('static/images', filename)

if __name__ == "__main__":
    app.run()