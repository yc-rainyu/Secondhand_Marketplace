import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)

# session / CSRF secret — env var first, otherwise a local file under instance/
_secret = os.environ.get('SECRET_KEY')
if not _secret:
    _secret_path = os.path.join(os.path.dirname(__file__), '..', 'instance', 'secret_key')
    os.makedirs(os.path.dirname(_secret_path), exist_ok=True)
    if os.path.exists(_secret_path):
        with open(_secret_path, 'r', encoding='utf-8') as f:
            _secret = f.read().strip()
    if not _secret:
        _secret = os.urandom(32).hex()
        with open(_secret_path, 'w', encoding='utf-8') as f:
            f.write(_secret)

app.config['SECRET_KEY'] = _secret
app.config['UPLOAD_FOLDER'] = os.path.join('app', 'static', 'uploads')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///market.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 MB
app.config['ALLOWED_EXTENSIONS'] = {'.jpg', '.jpeg', '.png'}

db = SQLAlchemy(app)
csrf = CSRFProtect(app)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

from app import routes
