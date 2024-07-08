# app.py

from flask import Flask
from PcBuilder_api import pc_builder_bp
from Product_finder_api import products_finder_bp
from Signup import signup_bp
from Login import login_bp
from models import db
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'supersecretkey'

# Initialize database with the app
db.init_app(app)

# Enable CORS
CORS(app)

# Register the blueprints
app.register_blueprint(pc_builder_bp)
app.register_blueprint(products_finder_bp)
app.register_blueprint(signup_bp)
app.register_blueprint(login_bp)

# Create tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
