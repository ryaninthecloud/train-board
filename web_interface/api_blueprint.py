"""
Contains routes for the API that
the display controllers contact
"""

from flask import Blueprint
api_blueprint = Blueprint("api_blueprint", __name__)

@api_blueprint.route("/")
def api_heartbeat(methods=["GET"]):
    return {
        "api_status":"up"
    }