from flask import Flask

import constants
import webhooks

app = Flask(__name__)
app.register_blueprint(webhooks.bp)


# @app.route('/')
# def hello():
#     return "Hello World!"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=constants.PORT)
