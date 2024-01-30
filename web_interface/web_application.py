"""
Contains the Flask web application.
Blueprints should be used for routing
and only pre and post processing
should be contained within this file.
"""

from flask import Flask, request
from api_blueprint import api_blueprint
from app_utilities import validate_configuration_for_application, load_restrictive_ip_configuration
from datainterface import DataInterface

web_application = Flask(__name__)
web_application.register_blueprint(api_blueprint, url_prefix="/api")

@web_application.before_request
def request_authorisation():
    """
    Code here will handle authorisation of 
    requests before they are passed on to 
    blueprints.

    Even when denied access because of IP rule
    implementations, the state of the request
    will be '200'. This is a coding choice, to
    make the handling and parsing of API errors
    easier when received by the Display Controller.
    """
    try:
        ip_restrictive_state, allowed_ips = load_restrictive_ip_configuration()
        if ip_restrictive_state and request.remote_addr not in allowed_ips:
            print("remote host denied", request.remote_addr)
            return DataInterface.produce_error_response("internal_auth")
    except Exception:
        return DataInterface.produce_error_response("check_logs_api")

if __name__ == "__main__":
    """
    For testing application operations.
    This file shouldn't be used for hosting.
    """
    validate_configuration_for_application()
    web_application.run(host="0.0.0.0")
