from flask import Flask
from flask_cors import CORS
from flask import request


app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "chrome-extension://bpcmapeoloepbomiddaidikkbbaeodjn"}})
# CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.route('/api/dictionary/hello', methods=['GET'])
def hello_world():
    data = request.args.get("word", None)
    return dict(
        success=True,
        message="Hello World",
        data=data
    )


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=7001)