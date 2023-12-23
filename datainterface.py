"""
DataConsumer provides an interface to make
and parse requests to the Darwin API
provided by Network Rail
"""

import configparser as cpr
from os.path import exists

class DataConsumer:
    """
    DataConsumer provides an interface to make
    and parse requests to the Darwin API
    provided by Network Rail
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
            cfg_file = cpr.ConfigParser()
        except PermissionError:
            raise(f"Error: Application does not have\
                  required permissions to open config\
                  file at {config_location}")
