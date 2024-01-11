"""
Contains code that runs the overall
web application, such as the API that
the display controllers reach out to
as well as, in the future, the web
interface that will enable remote
updates to the train stations.
"""

from flask import Flask, request
from api_blueprint import api_blueprint
from app_utilities import validate_configuration_for_application, load_restrictive_ip_configuration
from datainterface import DataInterface

app = Flask(__name__)
app.register_blueprint(api_blueprint, url_prefix="/api")

@app.before_request
def request_authorisation():
    """
    Code here will handle authorisation of 
    requests before they are passed on to 
    blueprints.
    """
    try:
        ip_restrictive_state, allowed_ips = load_restrictive_ip_configuration()
        if ip_restrictive_state and request.remote_addr not in allowed_ips:
            return DataInterface.produce_error_response("internal_auth")
    except Exception:
        return DataInterface.produce_error_response("check_logs_api")

if __name__ == "__main__":
    validate_configuration_for_application()
    app.run()
