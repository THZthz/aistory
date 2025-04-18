import logging
from flask import Flask, request, jsonify
from flask_cors import CORS

from db.initialize_step1 import time_str
from server.deepseek import DeepSeek

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)
CORS(app) # Middle-wares.

deepseek = DeepSeek()


@app.teardown_appcontext
def close_database_connection(exception=None) -> None:
    app.logger.debug('Closing database connection')
    deepseek.save()


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route("/api/get/all_messages", methods=["GET"])
def get_all_messages():
    return jsonify(deepseek.messages)


@app.route("/api/post/user_answer", methods=["POST"])
def post_user_answer():
    name = request.json.get('name', 'Amias')
    content = request.json.get('content')
    app.logger.info(name)
    app.logger.info(content)
    response_message = deepseek.user_answner(content, name)
    app.logger.info(response_message)
    return jsonify(response_message)