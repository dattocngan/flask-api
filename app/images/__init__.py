from flask import Blueprint

bp = Blueprint("comments", __name__)

from app.images import routes
