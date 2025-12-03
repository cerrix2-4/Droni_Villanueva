from flask import Flask
from flask_cors import CORS
from config import Config
from routes import web
from api import api

app = Flask(__name__)

# Configurazione
app.config['SECRET_KEY'] = Config.SECRET_KEY
app.config['DEBUG'] = Config.DEBUG

# CORS
CORS(app, supports_credentials=True, origins=Config.CORS_ORIGINS)

# Security headers
@app.after_request
def security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    return response

# Registra blueprints
app.register_blueprint(web)
app.register_blueprint(api)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
