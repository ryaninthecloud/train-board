"""
Contains routes for the API that
the display controllers contact
"""

from flask import Blueprint
from datainterface import DataInterface

api_blueprint = Blueprint("api_blueprint", __name__)

@api_blueprint.route("/")
def api_heartbeat(methods=["GET"]):
    """
    Returns a simple JSON that merely
    indicates that the API, at its root,
    is contactable.
    """
    return {
        "api_status":"up"
    }

@api_blueprint.route("/get_station_departures")
def get_station_departures(methods=["GET"]):
    """
    This route is used to return departures at
    the station provided within the configuration.ini
    """
    data_interface = DataInterface()
    departures = data_interface.get_station_departures()
    departures = data_interface.return_display_friendly_departures(departures)
    return(departures)