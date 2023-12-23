"""
DataInterface provides an interface to make
and parse requests to the Darwin API
provided by Network Rail
"""

import configparser as cpr
from sys import exit

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
            config_location = "configuration.ini"

        cfg_file = cpr.ConfigParser()

        try:
            cfg_file.read(config_location)
        except PermissionError:
            print(f"""Error: Application does not have required permissions to open config file at {config_location}""")
            exit(1)
        except FileNotFoundError:
            print(f"""Error: Application config file at {config_location} does not exist.""")
            exit(1)
        
        try:
            cfg_file['darwin_config']
        except KeyError as key_error:
            print(f"""Error: Invalid config, missing key: {key_error}""")
            exit(1)