from flask import Flask
from flask_cors import CORS


app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "chrome-extension://bpcmapeoloepbomiddaidikkbbaeodjn"}})

@app.route('/api/dictionary/hello', methods=['GET'])
def hello_world():
    return dict(
        success=True,
        message="Hello World",
        data="hello world"
    )


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=7001)