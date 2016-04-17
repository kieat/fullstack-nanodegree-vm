# coding=utf-8
from os import urandom
from datetime import timedelta
from flask import Flask, session
from blueprints import category, item, user

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = '/images'
app.secret_key = urandom(24)
app.permanent_session_lifetime = timedelta(days = 30)

app.jinja_env.globals['csrf_token'] = user.generate_csrf_token

app.register_blueprint(user.blueprint)
app.register_blueprint(category.blueprint)
app.register_blueprint(item.blueprint)

app.before_request(user.do_before_request)
app.context_processor(user.inject_context)

if __name__ == "__main__":
  app.debug = True
  app.run(host = '0.0.0.0')