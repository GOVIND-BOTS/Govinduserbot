import os

from flask import Flask
from flask_restful import Api, Resource

app = Flask(__name__)
api = Api(app)


class Greeting(Resource):
    def get(self):
        return {"status": "ok", "message": "Govind Userbot is running."}


api.add_resource(Greeting, "/")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
