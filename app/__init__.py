from flask import Flask
import os

# Create the Flask application instance
# Assuming app is run from root, but app package is in app/
# If we want to use templates/ at root, we need to go up one level from app/ folder
template_dir = os.path.abspath('templates')
app = Flask(__name__, template_folder=template_dir)


from app import routes