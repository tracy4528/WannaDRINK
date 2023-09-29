from flask import Flask
# from flask_jwt_extended import JWTManager
from werkzeug.exceptions import HTTPException



app = Flask(__name__)
# app.config.from_object(Config)
# db = SQLAlchemy(app, model_class = BaseModel)
# migrate = Migrate(app, db)

# jwt = JWTManager()
# jwt.init_app(app)

@app.errorhandler(404)
def server_error(error):
    return "Page not found", 404

@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        return e
    return "Internal Server Error", 500

from server.controllers import drink_controller