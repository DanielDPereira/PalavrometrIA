from flask import Flask
from .services import utils

def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = 'Viva-Cristo-Rei!'
    
    utils.create_upload_folder()
    
    from .routes import main
    app.register_blueprint(main)
    return app