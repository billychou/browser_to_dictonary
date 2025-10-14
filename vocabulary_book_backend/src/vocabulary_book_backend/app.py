from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "chrome-extension://bpcmapeoloepbomiddaidikkbbaeodjn"}})


if __name__ == "__main__":
    from app_factory import create_app
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=7001)
