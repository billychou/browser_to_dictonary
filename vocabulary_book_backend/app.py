import pathlib
import sys

path = pathlib.Path(__file__).parent.absolute()
print(path)
sys.path.append(str(path))

from app_factory import create_app

app = create_app()
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=7001)
