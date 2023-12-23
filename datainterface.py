"""
DataInterface provides an interface to make
and parse requests to the Darwin API
provided by Network Rail
"""

import configparser as cpr
from os.path import exists

class DataInterface:
    """
    DataInterface provides an interface to make
    and parse requests to the Darwin API
    provided by Network Rail and returns
    display middleware friendly responses
    """
    def __init__(self, config_location=None):
        """
        :param config_location: the config file 
               location, defaults if None
        :type: string
        """
        if config_location is None:
            config_location = "./configuration.ini"

        cfg_file = cpr.ConfigParser()

        try:
            cfg_file.read("")
        except PermissionError:
            raise(f"Error: Application does not have\
                  required permissions to open config\
                  file at {config_location}")
        except FileNotFoundError:
            raise(f"Error: Application config file at\
                  {config_location} does not exist.")
